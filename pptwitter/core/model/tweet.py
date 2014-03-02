import datetime

from peewee import CharField, DateTimeField, FloatField, ForeignKeyField, IntegerField

from . import db


class Tweet(db.Model):

    tweeted_by = CharField(index=True)

    tweet_id = CharField()

    text = CharField()

    rating = FloatField(index=True, default=0)

    rate_count = IntegerField(default=0)

    score = FloatField(index=True)

    language = FloatField(index=True)

    poetic = FloatField(index=True)

    sentiment = FloatField(index=True)

    created_at = DateTimeField(index=True, default=datetime.datetime.now)

    def __str__(self):
        return "%s: %s" % (self.tweeted_by, self.tweet[:25])


class Rating(db.Model):

    tweet = ForeignKeyField(Tweet)

    rating = IntegerField()

    remote_addr = CharField()

    class Meta:
        indexes = (
            (("tweet", "remote_addr"), True),
        )
