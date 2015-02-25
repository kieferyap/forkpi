"""PyNFC distutils installer file"""

#  Pynfc is a python wrapper for the libnfc library
#  Copyright (C) 2009  Mike Auty
#  PyCrypto1 is based on public domain optimized code by I.C.Weiner
#  See (http://cryptolib.com/ciphers/crypto1/crypto1.c)
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from distutils.core import setup, Extension

setup(
    name = "pynfc",
    version = "1.7.0_alpha1",
    description = "Python bindings for libnfc",
    author = "Mike Auty",
    data_files = [('examples', ['mifareauth.py'])],
    license = "GPL-2",
    py_modules = ['pynfc', 'pycrypto1', 'py14443a']
)

