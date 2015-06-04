#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Python bindings for libfprint"""

import os
from distutils.core import setup, Extension

setup(name="pyfprint",
	version="0.0",
	description="Python bindings for the libfprint fingerprinting library",
	author="Lukas Sandström",
	author_email="luksan@gmail.com",
	url="http://repo.or.cz/w/pyfprint.git",
	license="GPL-2",
	packages=["pyfprint"],
	ext_modules=[Extension('pyfprint._pyfprint_swig',
		['pyfprint/pyfprint_swig.i'],
		swig_opts=['-modern'],
		libraries=['fprint'],)],
	)