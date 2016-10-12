#!/usr/bin/env python
# coding=utf-8

import os
import sys

from setuptools import setup, find_packages

if not hasattr(sys, 'version_info') or sys.version_info < (3, 0, 0, 'final'):
	sys.exit('kevi requires Python 2.6 or later.')

setup(
	name = 'kevi',
	version = '0.2',

	author = 'King Chung Huang',
	author_email = 'kchuang@ucalgary.ca',
	description = 'Key-value inference.',

	packages = find_packages(),
	install_requires = [
		
	],

	zip_safe = True
)
