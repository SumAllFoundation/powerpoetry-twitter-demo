""" Database schema and data migration support.

A migration is a module within this package that ends.
It must end with a 3 digit version string. For example
example_migration_001.py. Migrations are applied according
to this number. No two migrations may have the same version
number.
"""

import glob
import importlib
import peewee
import os
import re
import sys

from playhouse import migrate

from ..core import db, model
from ..core.model import Schema


db = db.database
migrator = migrate.Migrator(db)


for path in glob.glob(os.path.dirname(__file__) + "/*.py"):
    f = os.path.splitext(os.path.basename(path))[0]
    if not f.startswith("__"):
        importlib.import_module(".%s" % f, "pptwitter.migration")


migrations = []
for f in dir(sys.modules[__name__]):
    m = re.match(".*_(\d\d\d)", f)
    if m is not None:
        migrations.append((m.group(1), m.group(0)))
migrations.sort()


def schema_version():
    """ Determine current database schema version. """
    with db.transaction():
        try:
            return Schema.select().order_by(Schema.version.desc()).get().version
        except peewee.psycopg2.ProgrammingError:
            return "000"


def migrate():
    """ Migrate the database to the latest schema. """
    module = sys.modules[__name__]
    version = schema_version()
    for migration_version, sym in migrations:
        if migration_version <= version:
            continue

        with db.transaction():
            migration = getattr(module, sym)
            migration.forwards(migrator, model)
            Schema.create(version=migration_version, description=migration.forwards.__doc__)
            print "* Upgraded schema @ %s - %s" % (migration_version, sym)
