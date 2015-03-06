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
    'djcelery_email',
    'appconf',
    'tester',
)

SECRET_KEY = 'unique snowflake'

# Django 1.7 throws dire warnings if this is not set.
# We don't actually use any middleware, given that there are no views.
MIDDLEWARE_CLASSES = ()

TEST_RUNNER = "test_runner.DJCETestSuiteRunner"

# Not set here - see 'test_runner.py'
# EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'

CELERY_EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
CELERY_EMAIL_TASK_CONFIG = {
    'queue': 'django_email',
    'delivery_mode': 1,  # non persistent
    'rate_limit': '50/m',  # 50 chunks per minute
}
