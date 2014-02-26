import celery
import logging

from flask import Flask
from flask.ext.assets import Environment
from flask.ext.compress import Compress
from flask_peewee.db import Database
from tweepy import API, OAuthHandler

from . import settings


app = Flask(__name__)
app.config.from_object(settings)
celery = celery.Celery()
celery.config_from_object(settings)

assets = Environment(app)
compress = Compress(app)
db = Database(app)

auth_config = lambda k: app.config["TWITTER"][k]
auth = OAuthHandler(auth_config("consumer_key"), auth_config("consumer_secret"))
auth.set_access_token(auth_config("access_token"), auth_config("access_token_secret"))

api = API(auth)


log_format = """
Message type:       %(levelname)s
Location:           %(pathname)s:%(lineno)d
Module:             %(module)s
Function:           %(funcName)s
Time:               %(asctime)s

Message:

%(message)s
"""


@app.before_first_request
def setup_logging():
    """ In production, add log handler to sys.stderr. """
    if not app.debug:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter(log_format))
        app.logger.addHandler(stream_handler)
        app.logger.setLevel(logging.INFO)


from . import routes  # NOQA
from .core import admin, rest, util  # NOQA
