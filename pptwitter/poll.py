from __future__ import division

import ConfigParser
import logging
import numpy as np
import os
import random
import signal
import sys
import time

from multiprocessing import Pool
from tweepy import Cursor

from . import api, config, config_path
from .poetry_percentile_rank import PercentilePoetryRanker


logger = logging.getLogger(__name__)
signal.signal(signal.SIGINT, lambda signal, frame: sys.exit(0))


ranker = PercentilePoetryRanker(
    config.get("Ranker", "inquirer"),
    config.get("Ranker", "coca"),
    config.get("Ranker", "percentiles"))


def rank(tweet):
    """ Rank each tweet.

    This function must be pickleable. This acheived by making this a
    module level function.
    """

    pid = os.getpid()
    np.random.seed(pid)
    random.seed(pid)
    return ranker.rank([tweet.text])


class TweetPoller(object):

    pool = Pool(processes=int(config.get("Poller", "processes")))

    poll_interval = int(config.get("Poller", "interval"))

    q = config.get("Poller", "query")

    count = config.get("Poller", "count")

    @property
    def since_id(self):
        try:
            return config.get("Twitter", "since_id")
        except ConfigParser.NoOptionError:
            return None

    @since_id.setter
    def since_id(self, id):
        config.set("Twitter", "since_id", id)
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

            for page in Cursor(api.search, **kwargs).pages():
                nextpoll = time.time() + self.poll_interval
                logger.info("Processing tweets...")
                self.process_page(page)
                self.sleep_until(nextpoll)
            self.sleep_until(nextpoll)

    def process_page(self, page):
        tweets = list(page)
        self.since_id = tweets[-1].id
        scores = ranker.rank(list(t.text for t in tweets))
        for tweet, score in zip(tweets, scores):
            # Put score into redis and create a link to some server to show scores.
            avgscore = sum(score.values()) / len(score)
            logger.info('%s...: %.1f%%' % (tweet.text[:20], avgscore))
            api.update_status("Your poem scored %.1f%%" % avgscore, tweet.id)
