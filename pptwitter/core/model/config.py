from . import db

from peewee import CharField


class Config(db.Model):

    name = CharField()

    value = CharField()

    def __str__(self):
        return "%s: %s" % (self.name, self.value)
