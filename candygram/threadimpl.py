# threadimpl.py
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

"""provides threading primitives"""

__revision__ = "$Id: threadimpl.py,v 1.1 2004/08/19 23:14:50 hobb0001 Exp $"


import _thread


# If we ever use a different implementation (like, say, stackless) use an
# environment variable to specify which implementation, a la pychecker.
#
# I strongly disagree :-) We should instead use a parameter passed to a
# (e.g., in a constructor or function) that takes a sensible defualt but offers
# the library user with the option of providing other supported "backends."
getCurrentThread = _thread.get_ident
startThread = _thread.start_new_thread
allocateLock = _thread.allocate_lock
