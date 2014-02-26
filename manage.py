#!/usr/bin/env python
import datetime

from flask.ext.script import Manager

from pptwitter.app import app
from pptwitter.migration import migrate
from pptwitter.core import db, model


manager = Manager(app)


@manager.command
def create_tables():
    """ Creates database tables. """
    model.create_tables()
    model.create_static_data()


@manager.command
def migrate_db():
    """ Migrate database to latest schema. """
    migrate()


@manager.command
def create_seed_data():
    """ Seed the database with development data. """
    users = ["ram.mehta@gmail.com", "mary@sumall.org"]
    for u in users:
        user = model.User(email=u, admin=True, active=True)
        user.set_password("poetic")
        user.save()


if __name__ == "__main__":
    manager.run()
