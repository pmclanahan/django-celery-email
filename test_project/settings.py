import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, '..'))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}


INSTALLED_APPS = (
    'appconf',
    'djcelery',
    'djcelery_email',
    'tester',
)

SECRET_KEY = 'unique snowflake'


CELERY_EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
TEST_RUNNER = "test_runner.DJCETestSuiteRunner"
CELERY_EMAIL_TASK_CONFIG = {
    'queue' : 'django_email',
    'delivery_mode' : 1, # non persistent
    'rate_limit' : '50/m', # 50 emails per minute
}
BROKER_URL = 'memory://'

# Not set here - see 'test_runner.py'
# EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
