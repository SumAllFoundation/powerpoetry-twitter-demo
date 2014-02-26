import functools
import httplib2
import json

from playhouse.postgres_ext import JSONField
from wtforms import fields
from wtfpeewee import orm

from .. import db

http = httplib2.Http()


class WPJSONField(fields.TextAreaField):
    """ Convert HSTORE fields to and from JSON notation. """

    def _value(self):
        return self.data and json.dumps(self.data) or u""

    def convert(self, jsonstr):
        return jsonstr and json.loads(jsonstr) or {}

    def process_formdata(self, valuelist):
        return super(WPJSONField, self).process_formdata(
            ["%s=>%s" % (k, v) for value in valuelist for k, v in self.convert(value).iteritems()])


orm.ModelConverter.defaults[JSONField] = WPJSONField


def transaction(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        with db.database.transaction():
            return func(*args, **kwargs)
    return inner
