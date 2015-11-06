#!/bin/sh

# steps to release the lib to pypi.
# only do this after a test build.

rm -rf dist build *.egg-info
python setup.py sdist bdist_wheel
twine upload -s dist/*
