import logging
import os

from celery.task.schedules import crontab
from celery.task import periodic_task
from tweepy import Cursor, TweepError

import pptwitter

from pptwitter.app import celery  # NOQA
from pptwitter.app import api, app
from pptwitter.core.model import Config, Tweet
from pptwitter.poetry_percentile_rank import PercentilePoetryRanker


logger = logging.getLogger(__file__)

basedir = os.path.dirname(pptwitter.__file__)
ranker = PercentilePoetryRanker(
    os.path.join(basedir, "..", app.config["INQUIRER_PATH"]),
    os.path.join(basedir, "..", app.config["COCA_PATH"]),
    os.path.join(basedir, "..", app.config["PERCENTILES_PATH"]))


@periodic_task(run_every=crontab(minute="*/1"))
def process_poems():
    logger.info("Processing poems...")
    q = app.config.get("QUERY")
    count = app.config.get("COUNT")
    kwargs = dict(q=q, count=count, result_type="recent", lang="en")
    try:
        config_since_id = Config.get(Config.name == "since_id")
    except Config.DoesNotExist:
        config_since_id = Config(name="since_id", value="")

    if config_since_id.value:
        kwargs["since_id"] = int(config_since_id.value)
        logger.info("Since ID: %s" % kwargs["since_id"])

    for page in Cursor(api.search, **kwargs).pages():
        process_page(page, config_since_id)
        config_since_id.save()


def process_page(page, config_since_id):
    tweets = list(page)
    logger.info("Received %d tweets..." % len(tweets))
    scores = ranker.rank(list(t.text for t in tweets))
    for tweet, score in zip(tweets, scores):
        config_since_id.value = tweet.id
        avgscore = sum(score.values()) / len(score)
        screen_name = tweet.user.screen_name
        local_tweet_id = Tweet.create(
            text=tweet.text,
            tweet_id=tweet.id,
            tweeted_by=screen_name,
            score=score).id

        logger.info('%s @%s %s...: %.1f%%' % (tweet.id, screen_name, tweet.text[:20], avgscore))
        logger.info("%s: @%s Your poem scored %.1f%%" % (tweet.id, screen_name, avgscore))
        config_since_id.value = tweet.id
        if app.config.get("TWITTER", "update_status"):
            link = "%s/?route=poetic/%s" % (app.config.get("DOMAIN"), local_tweet_id)
            message_tmpl = "@%s Your poem scored %.1f%%. For a detailed explanation see: %s"
            status = message_tmpl % (screen_name, avgscore, link)
            try:
                api.update_status(status, tweet.id, wrap_links="true")
            except TweepError:
                logger.info("Unable to update twitter status.", exc_info=True)
