import functools
import httplib2
import json
import math

from peewee import fn
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


def pnormaldist(qn):
    """ inverse of normal distribution ([2])

    Pr( (-\infty, x] ) = qn -> x
    """
    b = [
        1.570796288, 0.03706987906, -0.8364353589e-3,
        -0.2250947176e-3, 0.6841218299e-5, 0.5824238515e-5,
        -0.104527497e-5, 0.8360937017e-7, -0.3231081277e-8,
        0.3657763036e-10, 0.6936233982e-12
    ]

    if(qn < 0.0 or 1.0 < qn):
        raise ValueError("qn <= 0 or qn >= 1  in pnorm()!")

    if qn == 0.5:
        return 0.0

    w1 = qn if qn < 0.5 else 1.0 - qn
    w3 = -math.log(4.0 * w1 * (1.0 - w1))
    w1 = b[0]

    for i in xrange(1, 11):
        w1 += b[i] * w3 ** i

    return math.sqrt(w1 * w3) if qn > 0.5 else -math.sqrt(w1 * w3)


def wilson_confidence_column(score_col, count_col, max_score=100, confidence=0.95):
    z = pnormaldist(1 - (1 - confidence) / 2)
    return (
        (
            (score_col / (max_score * count_col)) +
            (z * z / (2 * max_score * count_col)) -
            (
                z * fn.Sqrt((
                    (1 / count_col * (1 - 1 / (max_score * count_col))) +
                    (z * z) / (4 * max_score * count_col)) / (max_score * count_col)
                )
            )
        ) /
        (1 + z * z / (max_score * count_col))
    )
