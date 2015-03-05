#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import codecs
import platform

try:
    from setuptools import setup, find_packages, Command
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages, Command

import djcelery_email as distmeta

if os.path.exists("README.rst"):
    long_description = codecs.open("README.rst", "r", "utf-8").read()
else:
    long_description = "See http://pypi.python.org/pypi/django-celery-email"


setup(
    name='django-celery-email',
    version=distmeta.__version__,
    description=distmeta.__doc__,
    author=distmeta.__author__,
    author_email=distmeta.__contact__,
    url=distmeta.__homepage__,
    platforms=["any"],
    license="BSD",
    packages=find_packages(exclude=['ez_setup', 'test_project', 'test_project.*']),
    scripts=[],
    zip_safe=False,
    install_requires=[
        "django-celery>=2.2.0",
    ],
    tests_require=(
        'django-setuptest',
    ),
    test_suite='setuptest.setuptest.SetupTestSuite',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Topic :: Communications",
        "Topic :: Communications :: Email",
        "Topic :: System :: Distributed Computing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points={},
    long_description=long_description,
)
