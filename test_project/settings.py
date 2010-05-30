# minimal settings for testing tagging via shell

import os, sys

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "../"))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = 'test.db'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'reputation',
    'test_app',
)

ROOT_URLCONF = 'urls'

REPUTATION_MAX_LOSS_PER_DAY = 200
REPUTATION_MAX_GAIN_PER_DAY = 200
REPUTATION_PERMISSONS = {'voting.can_vote_up': 50,
                         'voting.can_vote_down': 150}
