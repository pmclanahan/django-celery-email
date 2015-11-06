#!/usr/bin/env python
import os
import sys

import django

from tests import DJCETestSuiteRunner

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
    django.setup()
    failures = DJCETestSuiteRunner().run_tests(["tests"])
    sys.exit(bool(failures))
