from __future__ import division

import ConfigParser
import logging
import os
import signal
import sys
import time
import tweepy

from multiprocessing import Pool
from tweepy import API, Cursor, OAuthHandler

from poetry_percentile_rank import PercentilePoetryRanker


logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(message)s",
    level=logging.INFO)


config_path = os.path.join("config.ini")
config = ConfigParser.ConfigParser()

try:
    config.read(config_path)
except IOError:
    logging.error("Please create a config.ini.")
    raise

auth_config = lambda k: config.get("Twitter", k)
auth = OAuthHandler(auth_config("consumer_key"), auth_config("consumer_secret"))
auth.set_access_token(auth_config("access_token"), auth_config("access_token_secret"))

api = API(auth)


logger = logging.getLogger(__name__)


ranker = PercentilePoetryRanker(
    config.get("Ranker", "inquirer"),
    config.get("Ranker", "coca"),
    config.get("Ranker", "percentiles"))


class TweetPoller(object):

    pool = Pool(processes=int(config.get("Poller", "processes")))

    poll_interval = int(config.get("Poller", "interval"))

    q = config.get("Poller", "query")

    count = config.get("Poller", "count")

    @property
    def since_id(self):
        try:
            return int(config.get("Poller", "since_id"))
        except ConfigParser.NoOptionError:
            return None

    @since_id.setter
    def since_id(self, id):
        config.set("Poller", "since_id", id)
        with open(config_path, "wb") as configfile:
            config.write(configfile)

    def sleep_until(self, nextpoll):
        sleeptime = nextpoll - time.time()
        if sleeptime > 0:
            logger.info("Done. Waiting for %s seconds.", sleeptime)
            time.sleep(sleeptime)

    def start(self):
        while True:
            nextpoll = time.time() + self.poll_interval
            kwargs = dict(q=self.q, count=self.count, result_type="recent", lang="en")

            if self.since_id is not None:
                kwargs["since_id"] = self.since_id

            try:
                for page in Cursor(api.search, **kwargs).pages():
                    nextpoll = time.time() + self.poll_interval
                    logger.info("Processing tweets...")
                    self.process_page(page)
                    self.sleep_until(nextpoll)
            except tweepy.error.TweepError:
                logger.error("Unknown error.", exc_info=True)

            self.sleep_until(nextpoll)

    def process_page(self, page):
        tweets = list(page)
        self.since_id = tweets[-1].id
        scores = ranker.rank(list(t.text for t in tweets))
        for tweet, score in zip(tweets, scores):
            # Put score into redis and create a link to some server to show scores.
            self.update_status(tweet, score)

    def update_status(self, tweet, score):
        avgscore = sum(score.values()) / len(score)
        screen_name = tweet.user.screen_name
        logger.info('%s @%s %s...: %.1f%%' % (tweet.id, screen_name, tweet.text[:20], avgscore))
        if True:
            print "@%s Your poem scored %.1f%%" % (screen_name, avgscore), tweet.id
            return

        try:
            api.update_status("@%s Your poem scored %.1f%%" % (screen_name, avgscore), tweet.id)
        except tweepy.error.TweepError:
            logger.error("Error updating status.", exc_info=True)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda signal, frame: sys.exit(0))
    TweetPoller().start()
