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

try:
	import stackless
except:
	pass

DEFAULT = 0
STACKLESS = 1

getCurrentThread = None
startThread = None
allocateLock = None

def setImplementation(implType):
	global getCurrentThread, startThread, allocateLock
	if implType == DEFAULT:
		import thread
		getCurrentThread = thread.get_ident
		startThread = thread.start_new_thread
		allocateLock = thread.allocate_lock
		return
	if implType == STACKLESS:
		getCurrentThread = stackless_get_ident
		startThread = stackless_start_new_thread
		allocateLock = StacklessLock
		return
	assert False, 'Unknown implType: %d' % implType



def stackless_get_ident():
	current = stackless.getcurrent()
	if current.is_main:
		#~ print 0
		return 0
	frame = current.frame
	while frame is not None:
		# Find frame of __run() method of _ThreadProcess
		if frame.f_back is None and frame.f_code.co_name == '__run':
			#~ print id(frame.f_locals['self'])
			return id(frame.f_locals['self'])
		frame = frame.f_back
	#~ print 'not found', id(current)
	return id(current)

def stackless_start_new_thread(func, args):
	task = stackless.tasklet(func)
	task.setup(*args)
	task.run()

class StacklessLock:
	def __init__(self):
		self.acquired = False
		self.channel = stackless.channel()

	def acquire(self, wait=None):
		task = stackless.getcurrent()
		atomic = task.set_atomic(True)
		try:
			if not self.acquired:
				print 'acquired %d' % id(self)
				self.acquired = True
				return True
			pass
		finally:
			task.set_atomic(atomic)
		if wait is not None and wait == 0:
			return False
		print 'wait %d' % id(self)
		self.channel.receive()
		print 'done waiting %d' % id(self)
		return True

	def release(self):
		task = stackless.getcurrent()
		atomic = task.set_atomic(True)
		try:
			if self.channel.balance == 0:
				print 'released %d' % id(self)
				self.acquired = False
				return
			pass
		finally:
			task.set_atomic(atomic)
		print 'release %d' % id(self)
		self.channel.send(None)
		print 'done release %d' % id(self)

	def locked(self):
		task = stackless.getcurrent()
		atomic = task.set_atomic(True)
		try:
			return self.acquired
		finally:
			task.set_atomic(atomic)
		pass
