#!/usr/bin/env python
import os
import codecs

from setuptools import setup, find_packages


base_dir = os.path.dirname(__file__)

with codecs.open(os.path.join(base_dir, 'README.rst'), 'r', encoding='utf8') as f:
    long_description = f.read()

about = {}
with open(os.path.join(base_dir, 'djcelery_email', '__about__.py')) as f:
    exec(f.read(), about)


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
    packages=find_packages(exclude=['ez_setup', 'tests']),
    scripts=[],
    zip_safe=False,
    install_requires=[
        'django>=2.2',
        'celery>=4.0',
        'django-appconf',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Topic :: Communications',
        'Topic :: Communications :: Email',
        'Topic :: System :: Distributed Computing',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
