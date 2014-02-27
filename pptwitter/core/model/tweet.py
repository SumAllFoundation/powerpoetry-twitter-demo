import datetime

from peewee import CharField, DateTimeField, FloatField
from playhouse.postgres_ext import JSONField

from . import db


class Tweet(db.Model):

    tweeted_by = CharField(index=True)

    tweet_id = CharField()

    text = CharField()

    json_score = JSONField(default={})

    score = FloatField(index=True, default=0)

    language = FloatField(index=True, default=0)

    poetic = FloatField(index=True, default=0)

    sentiment = FloatField(index=True, default=0)

    created_at = DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return "%s: %s" % (self.tweeted_by, self.tweet[:25])
