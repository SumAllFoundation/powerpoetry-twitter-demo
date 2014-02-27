from peewee import BaseModel

from ..app import app, assets, celery, compress, db  # NOQA


class BaseMeta(BaseModel):

    def __new__(meta, name, bases, attrs):
        abstract = attrs.pop("__abstract__", False)
        cls = super(BaseMeta, meta).__new__(meta, name, bases, attrs)
        cls.__abstract__ = abstract
        return cls


class Model(db.Model):

    __metaclass__ = BaseMeta

    __abstract__ = True


db.Model = Model
