#!/usr/bin/env python

from setuptools import setup

setup(
    name='GoButler-Challenge',
    version='0.1.0',
    author='Damon Kelley',
    author_email='damon.kelley@gmail.com',
    url='https://github.com/damonkelley/gobutler-challenge',
    py_modules=['challenge'],
    include_package_data=True,
    description='CSV SMS records to JSON',
    install_requires=['phonenumbers', 'python-dateutil'],
    entry_points={
        'console_scripts': ['gobutler-challenge=challenge:main']
    }
)
