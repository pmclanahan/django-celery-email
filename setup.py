#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import codecs

from setuptools import setup, find_packages, Command


base_dir = os.path.dirname(__file__)


class RunTests(Command):
    description = 'Run the django test suite from the tests dir.'
    user_options = []

    def run(self):
        this_dir = os.getcwd()
        testproj_dir = os.path.join(this_dir, 'test_project')
        sys.path.append(testproj_dir)

        from django.core.management import execute_from_command_line
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
        os.chdir(testproj_dir)
        execute_from_command_line([__file__, 'test'])
        os.chdir(this_dir)

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


with codecs.open(os.path.join(base_dir, 'README.rst')) as f:
    long_description = f.read()

about = {}
with open(os.path.join(base_dir, 'djcelery_email', '__about__.py')) as f:
    exec (f.read(), about)


setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__summary__'],
    long_description=long_description,
    license=about['__license__'],
    url=about['__uri__'],
    author=about['__author__'],
    author_email=about['__email__'],
    platforms=['any'],
    packages=find_packages(exclude=['ez_setup', 'test_project', 'test_project.*']),
    scripts=[],
    zip_safe=False,
    install_requires=[
        'django>=1.7',
        'celery>=2.3.0',
        'django-appconf',
    ],
    cmdclass={'test': RunTests},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Topic :: Communications',
        'Topic :: Communications :: Email',
        'Topic :: System :: Distributed Computing',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    entry_points={},
)
