#!/usr/bin/python
import os
from setuptools import setup

this_dir = os.path.realpath(os.path.dirname(__file__))
long_description = open(os.path.join(this_dir, 'README.md'), 'r').read()

setup(
    name = 'etsy',
    version = '0.2.1',
    author = 'Dan McKinley',
    author_email = 'dan@etsy.com',
    description = 'Python access to the Etsy API',
    license = 'GPL v3',
    keywords = 'etsy api handmade',
    packages = ['etsy'],
    long_description = long_description,
    test_suite = 'test',
    install_requires=['simplejson >= 2.0'],
    extras_require = {
        'OAuth': ["oauth2>=1.2.0"],
    }
)
