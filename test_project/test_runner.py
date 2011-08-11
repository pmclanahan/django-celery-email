from django.test.simple import DjangoTestSuiteRunner


class DJCETestSuiteRunner(DjangoTestSuiteRunner):
    def setup_test_environment(self, **kwargs):
        pass

    def teardown_test_environment(self, **kwargs):
        pass

