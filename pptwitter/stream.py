import json
import random

from tweepy import Stream
from tweepy.streaming import StreamListener

from . import auth, api


class PoeticListener(StreamListener):
    """ Runs algorithm on tweets to determine how poetic they are. """

    message = "@%s Your tweet \"%s\" was %d%% poetic?"

    def on_data(self, data):
        data = json.loads(data)

        username = data["user"]["screen_name"]

        text = data["text"]
        maxlen = 140 - len(self.message) - len(username)
        tweet = (text[:maxlen] + '..') if len(text) > maxlen else text
        score = random.randint(0, 100)

        api.update_status(self.message % (username, tweet, score))
        return True

    def on_error(self, status):
        print status


if __name__ == "__main__":
    l = PoeticListener()
    stream = Stream(auth, l)
    stream.filter(track=["#basketball"])
