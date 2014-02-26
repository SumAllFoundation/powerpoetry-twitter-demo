from flask_peewee.auth import Auth

from . import db
from ..app import app
from .model import User


class Auth(Auth):

    def authenticate(self, email, password):
        active_value = True
        active = self.User.select().where(self.User.active == active_value)
        try:
            user = active.where(self.User.email == email).get()
        except self.User.DoesNotExist:
            return False

        if not user.check_password(password):
            return False

        return user


auth = Auth(app, db, user_model=User)
