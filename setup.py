#!/usr/bin/env python

from setuptools import setup

setup(
    name='sms-santize',
    version='0.1.0',
    author='Damon Kelley',
    author_email='damon.kelley@gmail.com',
    url='https://github.com/damonkelley/sms-santize',
    py_modules=['sanitize'],
    include_package_data=True,
    description='CSV SMS records to JSON',
    install_requires=['phonenumbers', 'python-dateutil'],
    entry_points={
        'console_scripts': ['sms-santize=challenge:main']
    }
)
