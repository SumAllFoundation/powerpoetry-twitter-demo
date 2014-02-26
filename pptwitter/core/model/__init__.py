import inspect
import peewee
import sys

from .. import db

from .config import Config  # NOQA
from .schema import Schema  # NOQA
from .tweet import Tweet  # NOQA
from .user import User  # NOQA


def create_tables():
    tables = []
    module = sys.modules[__name__]
    for sym in dir(module):
        attr = getattr(module, sym)
        if inspect.isclass(attr) and issubclass(attr, db.Model) and not attr.__abstract__:
            tables.append(attr)

    peewee.drop_model_tables(tables, fail_silently=True)
    peewee.create_model_tables(tables, fail_silently=True)

    try:
        from ... import migration
        version, _ = migration.migrations[-1]
    except IndexError:
        version = "000"

    Schema.create(version=version, description="Initial state.")


def create_static_data():
    pass
