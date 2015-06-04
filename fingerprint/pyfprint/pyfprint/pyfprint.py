# encoding=utf-8
############################################################################
#    Copyright (C) 2008 by Lukas Sandström                                 #
#    luksan@gmail.com                                                      #
#                                                                          #
#    This program is free software; you can redistribute it and/or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program; if not, write to the                         #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

import pyfprint_swig as pyf

# TODO:
#	exceptions, especially for RETRY_* errors
#	constants for fingers
#	tests
#	documentation
#	for x in y => map ?
#	Image(img) for devices which don't support imaging? Is img NULL?

_init_ok = False

def _dbg(*arg):
	#print arg
	pass

def fp_init():
	"""Call this before doing anything else."""
	_init_ok = (pyf.fp_init() == 0)
	if not _init_ok:
		raise "fprint initialization failed."

def fp_exit():
	"""pyfprint can't be used after this is called."""
	pyf.fp_exit()
	_init_ok = False

# """Enumeration of the different fingers, used when using Fprint.save_to_disk()."""
Fingers = dict(
	
	LEFT_THUMB = pyf.LEFT_THUMB,
	LEFT_INDEX = pyf.LEFT_INDEX,
	LEFT_MIDDLE = pyf.LEFT_MIDDLE,
	LEFT_RING = pyf.LEFT_RING,
	LEFT_LITTLE = pyf.LEFT_LITTLE,
	RIGHT_THUMB = pyf.RIGHT_THUMB,
	RIGHT_INDEX = pyf.RIGHT_INDEX,
	RIGHT_MIDDLE = pyf.RIGHT_MIDDLE,
	RIGHT_RING = pyf.RIGHT_RING,
	RIGHT_LITTLE = pyf.RIGHT_LITTLE
	)

class Device:
	"""Provides access to a fingerprint reading device. Don't construct this
	directly, use discover_devices() instead."""
	def __init__(self, dev_ptr = None, dscv_ptr = None, DscvList = None):
		"""For internal use only."""
		self.dev = dev_ptr
		self.dscv = dscv_ptr
		self.DscvList = DscvList
		if dscv_ptr and DscvList == None:
			raise "Programming error? Device contructed with dscv without DscvList."

	def close(self):
		"""Closes the device. No more methods, except open(), may be called after this."""
		if self.dev:
			pyf.fp_dev_close(self.dev)
		self.dev = None

	def open(self):
		"""Connects to the device."""
		if self.dev:
			raise "Device already open"
		self.dev = pyf.fp_dev_open(self.dscv)
		if not self.dev:
			raise "device open failed"

	def driver(self):
		"""
		Return a Driver instance.

		open() is not required before this method.
		"""
		if self.dev:
			return Driver(pyf.fp_dev_get_driver(self.dev))
		if self.dscv:
			return Driver(pyf.fp_dscv_dev_get_driver(self.dscv))

	def devtype(self):
		"""
		Return an integer representing the type of device.

		open() is not required before this method.
		"""
		if self.dev:
			return pyf.fp_dev_get_devtype(self.dev)
		if self.dscv:
			return pyf.fp_dscv_dev_get_devtype(self.dev)

	def nr_enroll_stages(self):
		"""
		Return how many times enroll_finger needs to be called
		before the finger is successfully enrolled.
		"""
		if self.dev:
			return pyf.fp_dev_get_nr_enroll_stages(self.dev)
		raise "Device not open"

	def is_compatible(self, fprint):
		"""
		Checks whether the passed fprint is compatible with the device.

		open() is not required before this method.
		"""
		if self.dev:
			if fprint.data_ptr:
				return pyf.fp_dev_supports_print_data(self.dev, fprint.data_ptr) == 1
			if fprint.dscv_ptr:
				return pyf.fp_dev_supports_dscv_print(self.dev, fprint.dscv_ptr) == 1
			raise "No print found"
		if self.dscv:
			if fprint.data_ptr:
				return pyf.fp_dscv_dev_supports_print_data(self.dscv, fprint.data_ptr) == 1
			if fprint.dscv_ptr:
				return pyf.fp_dscv_dev_supports_dscv_print(self.dscv, fprint.dscv_ptr) == 1
			raise "No print found"
		raise "No device found"

	def supports_imaging(self):
		"""If true, the device can return an image of the finger."""
		if self.dev:
			return pyf.fp_dev_supports_imaging(self.dev) == 1
		raise "Device not open"

	def img_width(self):
		"""Return the width of the images scanned by the device, in pixels."""
		if self.dev:
			return pyf.fp_dev_get_img_width(self.dev)
		raise "Device not open"

	def img_height(self):
		"""Return the height of the images scanned by the device, in pixels."""
		if self.dev:
			return pyf.fp_dev_get_img_height(self.dev)
		raise "Device not open"

	def capture_image(self, wait_for_finger):
		"""
		Captures an image from the device. Return None if imaging isn't supported.
		wait_for_finger controls if the device should wait for a finger to be placed
		on the sensor before image capture.
		"""
		if not self.dev:
			raise "Device not open"

		if not self.supports_imaging():
			return None

		unconditional = 1
		if wait_for_finger == True:
			unconditional = 0

		(r, img) = pyf.pyfp_dev_img_capture(self.dev, unconditional)
		img = Image(img)
		if r != 0:
			raise "image_capture failed. error: %i" % r
		return img

	def enroll_finger(self):
		"""FIXME: docstring, error handling"""
		if not self.dev:
			raise "Device not open"
		(r, fprint, img) = pyf.pyfp_enroll_finger_img(self.dev)
		img = Image(img)
		if r < 0:
			raise "Internal I/O error while enrolling: %i" % i
		if r == pyf.FP_ENROLL_COMPLETE:
			_dbg("enroll complete")
			return (Fprint(data_ptr = fprint), img)
		if r == pyf.FP_ENROLL_FAIL:
			print "Failed. Enrollmet process reset."
		if r == pyf.FP_ENROLL_PASS:
			_dbg("enroll PASS")
			return (None, img)
		if r == pyf.FP_ENROLL_RETRY:
			_dbg("enroll RETRY")
			pass
		if r == pyf.FP_ENROLL_RETRY_TOO_SHORT:
			_dbg("enroll RETRY_SHORT")
			pass
		if r == pyf.FP_ENROLL_RETRY_CENTER_FINGER:
			_dbg("enroll RETRY_CENTER")
			pass
		if r == pyf.FP_ENROLL_RETRY_REMOVE_FINGER:
			_dbg("enroll RETRY_REMOVE")
			pass
		return ("xxx", None)

	def verify_finger(self, fprint):
		"""
		Compare the finger on the device with the supplied Fprint.
		Return true if the finger and the Fprint matches.
		"""
		if not self.dev:
			raise "Device not open"
		(r, img) = pyf.pyfp_verify_finger_img(self.dev, fprint._get_print_data_ptr())
		img = Image(img)
		if r < 0:
			raise "verify error: %i" % r
		if r == pyf.FP_VERIFY_NO_MATCH:
			return (False, img)
		if r == pyf.FP_VERIFY_MATCH:
			return (True, img)
		if r == pyf.FP_VERIFY_RETRY:
			pass
		if r == pyf.FP_VERIFY_RETRY_TOO_SHORT:
			pass
		if r == pyf.FP_VERIFY_RETRY_CENTER_FINGER:
			pass
		if r == pyf.FP_VERIFY_RETRY_REMOVE_FINGER:
			pass
		return (None, None)

	def supports_identification(self):
		"""Return True if the device supports the identify_finger method."""
		if not self.dev:
			raise "Device not open"
		return pyf.fp_dev_supports_identification(self.dev) == 1

	def identify_finger(self, fprints):
		"""
		FIXME: error handling

		Match the finger on the reader against a list of Fprints.

		Return a tuple: (list_offset, Fprint, Image) if a match is found,
		(None, None, Image) otherwise.

		Image is None if the device doesn't support imaging.
		"""

		if not self.dev:
			raise "Device not open"
		gallery = pyf.pyfp_print_data_array(len(fprints))
		for x in fprints:
			if not self.is_compatible(x):
				raise "can't verify uncompatible print"
			gallery.append(x._get_print_data_ptr())
		(r, offset, img) = pyf.pyfp_identify_finger_img(self.dev, gallery.list)
		img = Image(img)
		if r < 0:
			raise "identification error"
		if r == pyf.FP_VERIFY_NO_MATCH:
			return (None, None, img)
		if r == pyf.FP_VERIFY_MATCH:
			return (offset, fprints[offset], img)
		if r == pyf.FP_VERIFY_RETRY:
			pass
		if r == pyf.FP_VERIFY_RETRY_TOO_SHORT:
			pass
		if r == pyf.FP_VERIFY_RETRY_CENTER_FINGER:
			pass
		if r == pyf.FP_VERIFY_RETRY_REMOVE_FINGER:
			pass
		return None

	def load_print_from_disk(self, finger):
		"""
		Load a stored fingerprint from the users home directory.

		- finger should be a value from Fingers.

		Return a Fprint.
		"""
		if not self.dev:
			raise "Device not open"
		(r, print_ptr) = pyf.fp_print_data_load(self.dev, finger)
		if r != 0:
			raise "could not load print from disk"
		return Fprint(data_ptr = print_ptr)

	def delete_stored_finger(self, finger):
		"""
		Delete a fingerprint stored in the users home directory

		- finger should be a value from Fingers.
		"""
		if not self.dev:
			raise "Device not open"
		r = pyf.fp_print_data_delete(self.dev, finger)
		if r != 0:
			raise "delete failed"

class Minutia(pyf.fp_minutia):
	"""A single point of interest in a fingerprint."""
	def __init__(self, minutia_ptr, img):
		# We need to keep a reference to the image,
		# since the pointer we're referring to might
		# be free'd otherwise
		self.img = img
		self.ptr = minutia_ptr
		pyf.fp_minutia.__init__(self, minutia_ptr)

class Image:
	"""An image returned from the fingerprint reader."""
	def __init__(self, img_ptr, bin = False):
		"""Private method."""
		self._img = img_ptr
		self._bin = bin
		self._std = False
		self._minutiae = None

	def __del__(self):
		if self._img:
			pyf.fp_img_free(self._img)

	def height(self):
		"""The height of the image in pixels."""
		return pyf.fp_img_get_height(self._img)
	def width(self):
		"""The width of the image in pixels."""
		return pyf.fp_img_get_width(self._img)

	def data(self):
		"""
		Return a string containing one byte per pixel, representing a grayscale image.
		"""
		return pyf.pyfp_img_get_data(self._img)

	def rgb_data(self):
		"""
		Return a string containing three bytes per pixel, representing a gray RGB image.
		"""
		return pyf.pyfp_img_get_rgb_data(self._img)

	def save_to_file(self, filename):
		"""Save the image as a pgm file."""
		r = pyf.fp_img_save_to_file(self._img, filename)
		if r != 0:
			raise "Save failed"

	def standardize(self):
		"""Normalize orientation and colors of the image."""
		pyf.fp_img_standardize(self._img)
		self._std = True

	def binarize(self):
		"""
		Return the image converted to a black/white binary image of the print.
		The returned Image is a copy of the original. The old image remains
		un-binarized.

		This will standardize() the image, if it isn't already so.
		"""
		if self._bin:
			return
		if not self._std:
			self.standardize()
		i = pyf.fp_img_binarize(self._img)
		if i == None:
			raise "Binarize failed"
		i = Image(img_ptr = i, bin = True)
		i._minutiae = self._minutiae
		return i

	def minutiae(self):
		"""
		Return a list of the minutiae found in the image.

		This method will fail on a binarized image.
		"""
		if self._minutiae:
			return self._minutiae
		if self._bin:
			raise "Cannot find minutiae in binarized image"
		if not self._std:
			self.standardize()
		(min_list, nr) = pyf.fp_img_get_minutiae(self._img)
		l = []
		for n in range(nr):
			l.append(Minutia(img = self, minutia_ptr = pyf.pyfp_deref_minutiae(min_list, n)))
		self._minutiae = l
		return l

class Driver:
	"""Provides access to some information about a libfprint driver."""
	def __init__(self, swig_drv_ptr):
		"""Private."""
		self.drv = swig_drv_ptr

	def __del__(self):
		#FIXME: free drv?
		pass

	def name(self):
		"""Return the driver name."""
		return pyf.fp_driver_get_name(self.drv)

	def full_name(self):
		"""A longer, more desciptive version of the driver name."""
		return pyf.fp_driver_get_full_name(self.drv)

	def driver_id(self):
		"""Return an integer uniqly identifying the driver."""
		return pyf.fp_driver_get_driver_id(self.drv)

class Fprint:
	def __init__(self, serial_data = None, data_ptr = None, dscv_ptr = None, DscvList = None):
		"""
		The only parameter that should be used is serial_data, which
		should be data previously aquired from data(), in the form of a string.
		All other parameters are for internal use only.
		"""
		# data_ptr is a SWIG pointer to a struct pf_print_data
		# dscv_ptr is a SWIG pointer to a struct pf_dscv_print
		# DscvList is a class instance used to free the allocated pf_dscv_print's
		#          with pf_dscv_prints_free when they're all unused.
		# serial_data is a string as returned by data()

		self.data_ptr = data_ptr
		self.dscv_ptr = dscv_ptr
		self.DscvList = DscvList

		if serial_data:
			self.data_ptr = pyf.fp_print_data_from_data(serial_data)
			return

		if dscv_ptr != None and DscvList == None:
			raise "Programming error: Fprint constructed with dscv_prt with DscvList == None"

	def __del__(self):
		if self.data_ptr:
			pyf.fp_print_data_free(self.data_ptr)
		# The dscv_ptr is freed when all the dscv prints have been garbage collected

	def _get_print_data_ptr(self):
		if not self.data_ptr:
			self._data_from_dscv()
		return self.data_ptr

	def driver_id(self):
		"""Return an integer identifing the driver used to scan this print."""
		if self.data_ptr:
			return pyf.fp_print_data_get_driver_id(self.data_ptr)
		elif self.dscv_ptr:
			return pyf.fp_dscv_print_get_driver_id(self.dscv_ptr)
		raise "no print"

	def devtype(self):
		"""Return an integer representing the type of device used to scan this print."""
		if self.data_ptr:
			return pyf.fp_print_data_get_devtype(self.data_ptr)
		elif self.dscv_ptr:
			return pyf.fp_dscv_print_get_devtype(self.dscv_ptr)
		raise "no print"

	def finger(self):
		"""
		If the Fprint was returned from discover_prints(), return
		the Finger the Fprint represents. Otherwise raise an exception.
		"""
		if not self.dscv_ptr:
			raise "finger() needs a discovered print"
		return pyf.fp_dscv_print_get_finger(self.dscv_ptr)

	def delete_from_disk(self):
		"""
		If the Fprint was returned from discover_prints(), delete it
		from the users home directory. Otherwise raise an exception.
		"""
		if not self.dscv_ptr:
			raise "delete needs a discovered print"
		return pyf.fp_dscv_print_delete(self.dscv_ptr)

	def save_to_disk(self, finger):
		"""Save the print to the users home directory.

		- finger is a member of Fingers, indicating which
		  finger this is.
		"""
		r = pyf.fp_print_data_save(self.data_ptr, finger)
		if r != 0:
			raise "save failed"

	def _data_from_dscv(self):
		if self.data_ptr:
			return
		if not self.dscv_ptr:
			raise "no print"
		(r, ptr) = pyf.fp_print_data_from_dscv_print(self.dscv_ptr)
		if r != 0:
			raise "print data from dscv failed"
		self.data_ptr = ptr

	def data(self):
		"""
		Return a serialized dataset representing the fprint.
		This data could be stored away, and later passed to the
		contructor of Fprint.
		"""
		if not self.data_ptr:
			raise "no print"
		s = pyf.pyfp_print_get_data(self.data_ptr)
		if not len(s):
			raise "serialization failed"
		return s

class DiscoveredPrints(list):
	"""
	A list of stored fingerprints available from the users
	home directory.
	"""
	def __init__(self, dscv_devs_list):
		self.ptr = dscv_devs_list
		i = 0
		while True:
			x = pyf.pyfp_deref_dscv_print_ptr(dscv_devs_list, i)
			if x == None:
				break
			self.append(Fprint(dscv_ptr = x, DscvList = self))
			i = i + 1
	def __del__(self):
		pyf.pf_dscv_prints_free(self.ptr)

def discover_prints():
	"""Look for fingerprints in the users home directory ;)"""
	if not _init_ok:
		fp_init()

	prints = pyf.fp_discover_prints()

	if not prints:
		print "Print discovery failed"
	return DiscoveredPrints(prints)


class DiscoveredDevices(list):
	"""A list of available devices."""
	def __init__(self, dscv_devs_list):
		self.swig_list_ptr = dscv_devs_list
		i = 0
		while True:
			x = pyf.pyfp_deref_dscv_dev_ptr(dscv_devs_list, i)
			if x == None:
				break
			self.append(Device(dscv_ptr = x, DscvList = self))
			i = i + 1

	def __del__(self):
		pyf.fp_dscv_devs_free(self.swig_list_ptr)

	def find_compatible(self, fprint):
		"""
		Return a Device that is compatible with the fprint,
		or None if no compatible device is found.
		"""
		for n in self:
			if n.is_compatible(fprint):
				return n
		return None

def discover_devices():
	"""Return a list of available devices."""
	if not _init_ok:
		fp_init()

	devs = pyf.fp_discover_devs()

	if not devs:
		raise "Device discovery failed"
	return DiscoveredDevices(devs)