# Copyright 1999-2008 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

EAPI=0

EGIT_REPO_URI="git://repo.or.cz/pyfprint.git"
EGIT_BRANCH="master"

NEED_PYTHON=2.3

inherit eutils distutils git

DESCRIPTION="Python bindings for the libfprint fingerprinting library."
HOMEPAGE="http://repo.or.cz/w/pyfprint.git"
SRC_URI=""

LICENSE="LGPL-2"

SLOT="0"
KEYWORDS="~x86 ~amd64"
IUSE="" #docs
PYTHON_MODNAME="pyfprint"

DEPEND=">=dev-lang/swig-1.3.34
	media-libs/libfprint"

RDEPEND="media-libs/libfprint"

src_unpack() {
	git_src_unpack
	cd ${S}
}
