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
)

ROOT_URLCONF = 'urls'

MAX_REPUTATION_LOSS_PER_DAY = 200
MAX_REPUTATION_GAIN_PER_DAY = 200

REPUTATION_PERMISSONS = {'can_vote_up': 50,
                         'can_vote_down': 150,
                         'can_add_tag': 250}

'''
REPUTATION_ENABLED = True
BASE_REPUTATION = 5000
REPUTATION_REQUIRED_TEMPLATE = 'reputation/reputation_required.html'
'''
