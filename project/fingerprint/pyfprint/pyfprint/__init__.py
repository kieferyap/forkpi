# -*- coding: utf-8 -*-
"""A Python (SWIG) Wrapper for libfprint"""

__version__ = '0.0'
__date__ = '2008/06/25'
__author__ = 'Lukas Sandström <luksan -at- gmail -dot- com>'
__url__ = 'http://repo.or.cz/w/pyfprint.git, http://lists.reactivated.net/pipermail/fprint/'

__all__ = [
	"fp_init",
	"fp_exit",
	"discover_prints",
	"discover_devices",
	"Device",
	"DiscoveredDevices",
	"DiscoveredPrints",
	"Driver",
	"Fingers",
	"Fprint",
	"Image",
	"Minutia",
]

from pyfprint import *