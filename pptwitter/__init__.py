import ConfigParser
import logging
import os

from tweepy import API, OAuthHandler


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
