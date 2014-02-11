import logging
import numpy as np
import os
import random
import signal
import sys
import time

from multiprocessing import Pool
from tweepy import Cursor

from . import api, config


logger = logging.getLogger(__name__)
signal.signal(signal.SIGINT, lambda signal, frame: sys.exit(0))


def rate(tweet):
    pid = os.getpid()
    np.random.seed(pid)
    random.seed(pid)
    # Call numpy/scipy code here.
    return random.randint(0, 100)


class TweetPoller(object):

    pool = Pool(processes=int(config.get("Poller", "processes")))

    poll_interval = int(config.get("Poller", "interval"))

    q = config.get("Poller", "query")

    def start(self):
        kwargs = dict(q=self.q, result_type="recent", lang="en")
        for page in Cursor(api.search, **kwargs).pages():
            nextpoll = time.time() + self.poll_interval
            logger.info("Processing tweets...")
            self.process_page(page)

            sleeptime = nextpoll - time.time()
            if sleeptime > 0:
                logger.info("Done. Waiting for %s seconds.", sleeptime)
                time.sleep(sleeptime)

    def process_page(self, page):
        tweets = list(page)
        scores = self.pool.map(rate, tweets)
        for tweet, score in zip(tweets, scores):
            # api.update_status("")
            print tweet.id, tweet.text[:20], ('...: %s%%' % score)

