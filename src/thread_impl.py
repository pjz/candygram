# thread_impl.py
#
# Copyright (c) 2004 Michael Hobbs
#
# This file is part of Candygram.
#
# Candygram is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.
#
# Candygram is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Candygram; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""Provides threading primitives"""

__revision__ = '$Id: thread_impl.py,v 1.3 2004/08/18 20:57:50 hobb0001 Exp $'

DEFAULT = 0

getCurrentThread = None
startThread = None
allocateLock = None

def setImplementation(implType):
	"""Specify which threading implementation to use"""
	global getCurrentThread, startThread, allocateLock
	if implType == DEFAULT:
		import thread
		getCurrentThread = thread.get_ident
		startThread = thread.start_new_thread
		allocateLock = thread.allocate_lock
		return
	assert False, 'Unknown implType: %d' % implType


