import os.path
import sys

import djcelery

djcelery.setup_loader()

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, '..'))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'db.sqlite'),
    }
}


ROOT_URLCONF = 'test_project.urls'

INSTALLED_APPS = (
    'djcelery',
    'djcelery_email',
    'tester',
)

TEST_RUNNER = "test_runner.DJCETestSuiteRunner"

CELERY_ALWAYS_EAGER = True
CELERY_EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
# for tests
CELERY_EMAIL_TASK_CONFIG = {
    'queue' : 'django_email',
    'delivery_mode' : 1, # non persistent
    'rate_limit' : '50/m', # 50 emails per minute
}
