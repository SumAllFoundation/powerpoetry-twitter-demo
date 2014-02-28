import datetime

from peewee import CharField, DateTimeField, FloatField

from . import db


class Tweet(db.Model):

    tweeted_by = CharField(index=True)

    tweet_id = CharField()

    text = CharField()

    score = FloatField(index=True)

    language = FloatField(index=True)

    poetic = FloatField(index=True)

    sentiment = FloatField(index=True)

    created_at = DateTimeField(index=True, default=datetime.datetime.now)

    def __str__(self):
        return "%s: %s" % (self.tweeted_by, self.tweet[:25])
