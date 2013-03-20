#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on 2013-03-20.  Copyright (C) Yeolar <yeolar@gmail.com>
#

from setuptools import setup, find_packages


setup(
    name='TorBench',
    version='1.0',
    description='TorBench is a benchmark and url checker tool based on Tornado.',
    long_description=open('README.md').read().split('\n\n', 1)[1],
    author='Yeolar',
    author_email='yeolar@gmail.com',
    url='http://www.yeolar.com',
    packages=find_packages(),
    install_requires=[
        'tornado>=2.3',
    ],
    entry_points={
        'console_scripts': [
            'torbench = torbench.benchclient:main',
            'toranalyzer = torbench.analyzer:main',
            'torchecker = torbench.checker:main',
        ]
    },
)
