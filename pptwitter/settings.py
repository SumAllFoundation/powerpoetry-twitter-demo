import os


DOMAIN = "http://localhost:6001"

DEBUG = True
ASSETS_DEBUG = True

SECRET_KEY = "powertothepoem"

BROKER_TRANSPORT = "redis"
BROKER_URL = "redis://localhost:6003/0"
CELERY_RESULT_BACKEND = "redis://localhost:6003"
DATABASE = {
    "name": "pptwitter",
    "engine": "playhouse.postgres_ext.PostgresqlExtDatabase",
    "port": 6002,
    "user": "pptwitter",
    "password": "root"
}

REDIS = {
    "host": "localhost",
    "port": 6003
}

TWITTER = {}
COCA_PATH = "data/coca.json"
INQUIRER_PATH = "data/inquirer.json"
PERCENTILES_PATH = "data/twitter_percentiles.csv"
QUERY = "#powerpoetrydemo"
COUNT = 20

CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']


config_file = os.path.join(os.path.dirname(__file__), "..", "settings.cfg")
if os.path.exists(config_file):
    execfile(config_file, globals(), locals())
