DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}


INSTALLED_APPS = (
    'djcelery_email',
    'appconf',
)

SECRET_KEY = 'unique snowflake'

# Django 1.7 throws dire warnings if this is not set.
# We don't actually use any middleware, given that there are no views.
MIDDLEWARE_CLASSES = ()

CELERY_EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
CELERY_EMAIL_TASK_CONFIG = {
    'queue': 'django_email',
    'delivery_mode': 1,  # non persistent
    'rate_limit': '50/m',  # 50 chunks per minute
}
