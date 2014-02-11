#! /usr/bin/env python
# encoding: utf-8
import os

APPNAME = "powerpoetry-twitter-demo"
VERSION = "0.0.1"

top = "."
out = "env"


if os.environ.get("VIRTUAL_ENV"):
    raise OSError("Please deactivate the virtual env first. Try: \n  $ deactivate")


def options(ctx):
    ctx.recurse("src")


def configure(ctx):
    ctx.recurse("src")


def venv(cmd):
    return os.linesep.join((". env/bin/activate", cmd, "deactivate"))


def style(ctx):
    print("→ Running flake8 on python code...")
    ctx.exec_command(venv("flake8 pptwitter"))


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

