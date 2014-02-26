from flask_peewee.auth import BaseUser
from peewee import BooleanField, CharField

from . import db


class User(db.Model, BaseUser):

    email = CharField(unique=True)

    password = CharField()

    active = BooleanField(default=True)

    admin = BooleanField(default=False)

    locale = CharField(default="en")

    @property
    def username(self):
        return self.email

    @username.setter
    def username(self, value):
        self.email = value

    def __str__(self):
        return self.username
