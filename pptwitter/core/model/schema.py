import datetime

from peewee import CharField, DateTimeField, TextField

from . import db


class Schema(db.Model):

    version = CharField(unique=True)

    applied_on = DateTimeField(default=datetime.datetime.now)

    description = TextField()
