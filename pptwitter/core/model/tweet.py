import datetime

from peewee import CharField, DateTimeField
from playhouse.postgres_ext import JSONField

from . import db


class Tweet(db.Model):

    tweeted_by = CharField()

    tweet_id = CharField()

    text = CharField()

    score = JSONField()

    created_at = DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return "%s: %s" % (self.tweeted_by, self.tweet[:25])
