# condition.py
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

"""A customized version of threading.Condition.

The Condition class that exists in the threading package has one problem. When
calling wait() with a timeout argument, the method does not return any
indication whether it timed out or if it was awakened by a notify(). It is
possible to make a guess at whether the method timed out or not by checking the
time after the method returns, but then one still can't be sure that a notify()
didn't come in at the last moment.

This Condition class fixes that problem by returning True if the wait() call
was awakened by a notify() and False if it timed out. The class is also
simplified by making the following assumptions:
 - There will only be one waiting thread at a time.
 - The lock need not be reentrant.
 - wait() and notify() will only be invoked by the thread that has established
   the lock.
"""

__revision__ = '$Id: condition.py,v 1.4 2004/08/19 23:18:02 hobb0001 Exp $'


import time

from candygram.threadimpl import allocateLock


class Condition:

	"""modified Condition class"""

	def __init__(self):
		self.__lock = allocateLock()
		self.acquire = self.__lock.acquire
		self.release = self.__lock.release
		self.locked = self.__lock.locked
		self.__waiter = None

	def wait(self, timeout=None):
		"""wait for notify()"""
		assert self.locked()
		waiter = allocateLock()
		waiter.acquire()
		self.__waiter = waiter
		self.release()
		try:
			return _acquire(waiter, timeout)
		finally:
			self.acquire()
		# end try

	def notify(self):
		"""wake up wait()ers"""
		assert self.locked()
		if self.__waiter is not None:
			self.__waiter.release()
			self.__waiter = None
		# end if


def _acquire(lock, timeout):
	"""try to acquire a lock, with a timeout"""
	if timeout is None:
		lock.acquire()
		return True
	timeout = time.time() + timeout
	delay = 0.0005  # 500 us -> initial delay of 1 ms
	while True:
		if lock.acquire(0):
			return True
		remaining = timeout - time.time()
		if remaining <= 0:
			break
		delay = min(delay * 2, remaining, .05)
		time.sleep(delay)
	return False
