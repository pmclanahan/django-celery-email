from django.conf import settings
from django.test.simple import DjangoTestSuiteRunner


class DJCETestSuiteRunner(DjangoTestSuiteRunner):
    def setup_test_environment(self, **kwargs):
        super(DJCETestSuiteRunner, self).setup_test_environment(**kwargs)
        settings.EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
