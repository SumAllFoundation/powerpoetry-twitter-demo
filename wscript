#! /usr/bin/env python
# encoding: utf-8
import datetime
import os

APPNAME = "powerpoetry-twitter-demo"
VERSION = "0.0.1"

top = "."
out = "env"


services = [
    "celeryd",
    "karma",
    "redis",
    "postgres"
]

PORT_BASE = 6000
FLASK_PORT = 1 + PORT_BASE
POSTGRES_PORT = 2 + PORT_BASE
REDIS_PORT = 3 + PORT_BASE

if os.environ.get("VIRTUAL_ENV"):
    raise OSError("Please deactivate the virtual env first. Try: \n  $ deactivate")

if os.path.exists("services.cfg"):
    with open("services.cfg") as svc:
        services = [s.strip() for s in svc.read().split(",")]


def options(ctx):
    ctx.recurse("src")


def configure(ctx):
    ctx.recurse("src")


def venv(cmd):
    return os.linesep.join((". env/bin/activate", cmd, "deactivate"))


def venv(cmd):
    return os.linesep.join((". env/bin/activate", cmd, "deactivate"))


def style(ctx):
    print("→ Running flake8 on python code...")
    ctx.exec_command(venv("flake8 pptwitter"))
    print("→ Running jshint on javascript code...")
    ctx.exec_command(venv("jshint pptwitter/static/js "))


def start(ctx, services=services):
    return service(ctx, "start", services)


def stop(ctx, services=services):
    return service(ctx, "stop", services)


def service(ctx, cmd, services):
    cmd = os.linesep.join(["cd $VIRTUAL_ENV"] + ["etc/init.d/%s %s" % (s, cmd) for s in services])
    ctx.exec_command(venv(cmd))


def dump(ctx):
    print("→ Save database dump...")
    ctx.exec_command(venv("mkdir -p $VIRTUAL_ENV/../dumps"))

    dumpfile = "%s-%s.dump" % (APPNAME, datetime.datetime.now().isoformat())
    cmd = "pg_dump --username=postgres --port=%s pptwitter -f $VIRTUAL_ENV/../dumps/%s" % (
        POSTGRES_PORT, dumpfile)
    ctx.exec_command(venv(cmd))

    masterdump = "dumps/%s.dump" % APPNAME
    if os.path.exists(masterdump):
        os.unlink(masterdump)
    os.symlink(dumpfile, masterdump)


def load(ctx):
    print("→ Recreating database...")
    cmd = (
        "echo \"DROP DATABASE pptwitter; CREATE DATABASE pptwitter\" | "
        "   psql --username=postgres --port=%s postgres") % POSTGRES_PORT
    ctx.exec_command(venv(cmd))

    cmd = (
        "echo \"CREATE EXTENSION HSTORE\" | "
        "   psql --username=postgres --port=%s pptwitter") % POSTGRES_PORT
    ctx.exec_command(venv(cmd))

    print("→ Load database dump...")
    cmd = "psql --username=postgres --port=%s -d pptwitter -f $VIRTUAL_ENV/../dumps/%s.dump" % (
        POSTGRES_PORT, APPNAME)
    ctx.exec_command(venv(cmd))


def stage(ctx):
    print("→ Starting staging server...")
    ctx.exec_command(venv(
        "gunicorn pptwitter.app:app "
        "--bind unix:env/gunicorn_flask.sock "
        "--pid $VIRTUAL_ENV/run/gunicorn.pid "
        "--workers 2 "
        "--daemon"))


def restage(ctx):
    print("→ Reloading staging server code")
    ctx.exec_command(venv("kill -HUP `cat $VIRTUAL_ENV/run/gunicorn.pid`"))


def unstage(ctx):
    print("→ Stopping staging server")
    ctx.exec_command(venv("kill `cat $VIRTUAL_ENV/run/gunicorn.pid`"))


def serve(ctx):
    print("→ Starting development server on port %d..." % FLASK_PORT)
    ctx.exec_command(venv("./manage.py runserver --port %s") % FLASK_PORT)


def resetdb(ctx):
    print("→ Resetting database for development...")
    ctx.exec_command(venv("./manage.py create_tables"))
    ctx.exec_command(venv("./manage.py create_seed_data"))


def migratedb(ctx):
    print("→ Migrating database schema")
    ctx.exec_command(venv("python manage.py migrate_db"))


def updatejs(ctx):
    print("→ Updating bower dependencies...")
    ctx.exec_command(venv("cd env && bower update --save"))


def test(ctx):
    if os.path.exists(".coverage"):
        os.remove(".coverage")

    if os.path.exists("cover"):
        shutil.rmtree("cover")

    ctx.exec_command(venv("nosetests dogbox/tests --with-coverage --cover-html"))


def testjs(ctx):
    ctx.exec_command(venv("karma run pptwitter/tests/js/config.js"))


def build(ctx):
    ctx(rule="virtualenv .", target="bin/python")
    ctx.template(
        "src/activate.tmpl", format=False, executable=True,
        source="bin/python", target="bin/activate")

    ctx.recurse("src")

    # Add machine to pythonpath
    ctx(
        rule=ctx.venv("cd $VIRTUAL_ENV/.. && python setup.py develop"),
        source="bin/activate",
        target="lib/python2.7/site-packages/pptwitter.egg-link")

    # Create etc dir
    ctx(
        rule=ctx.venv("""
            mkdir -p "$VIRTUAL_ENV/etc"
            touch "$VIRTUAL_ENV/etc/.done"
        """),
        source="bin/activate",
        target="etc/.done")

    # Initialize db
    pgopts = dict(port=POSTGRES_PORT, dbname="pptwitter")
    ctx.template(
        "etc/initdb.template",
        executable=True,
        source=["etc/.done", "bin/postmaster"],
        target="etc/initdb",
        template_args=pgopts)

    ctx.template(
        "etc/init.d/postgres.template",
        executable=True,
        source="etc/initdb",
        target="etc/init.d/postgres",
        template_args=pgopts)

    ctx(
        rule=lambda target: ctx.venv_exec("""
            rm -rf $VIRTUAL_ENV/postgres
            mkdir $VIRTUAL_ENV/postgres
            mkdir -p $VIRTUAL_ENV/log
            pushd $VIRTUAL_ENV/etc
            ./initdb
            popd
        """),
        source="etc/init.d/postgres",
        target="postgres/data/PG_VERSION")

    # Initialize redis
    redisopts = dict(port=REDIS_PORT)
    ctx.template(
        "etc/conf/redis.conf.template",
        source=["etc/.done", "bin/redis-server"],
        target="etc/conf/redis.conf",
        template_args=redisopts)

    ctx.template(
        "etc/init.d/redis.template",
        executable=True,
        source="etc/conf/redis.conf",
        target="etc/init.d/redis",
        template_args=redisopts)

    # Initialize celery daemon
    ctx.template(
        "etc/conf/celeryd.conf.template",
        source="etc/.done",
        target="etc/conf/celeryd.conf")

    ctx.template(
        "etc/init.d/celeryd.template",
        executable=True,
        source="etc/conf/celeryd.conf",
        target="etc/init.d/celeryd")

    # Initialize karma server
    ctx.template(
        "etc/init.d/karma.template",
        executable=True,
        source="bin/karma",
        target="etc/init.d/karma")
