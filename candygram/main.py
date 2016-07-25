# candygram.py
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

"""Erlang concurrency primitives"""

__revision__ = '$Id: main.py,v 1.4 2004/09/09 15:47:07 hobb0001 Exp $'


from candygram.threadimpl import getCurrentThread


def spawn(func, *args, **kwargs):
	"""spawn new process"""
	return _doSpawn(func, args, kwargs, None)


def spawnLink(func, *args, **kwargs):
	"""spawn and link to a new process atomically"""
	return _doSpawn(func, args, kwargs, self())


def _doSpawn(func, args, kwargs, initialLink):
	"""performs initiation of new process thread"""
	_checkSignal()
	if not callable(func):
		raise ExitError('badarg')
	class_ = Process
	if '_processClass' in kwargs:
		class_ = kwargs['_processClass']
		del kwargs['_processClass']
	proc = class_()
	proc._startThread(func, args, kwargs, initialLink)
	return proc


def self(noCheck=False):
	"""return current process"""
	# _checkSignal() needs to invoke self(). In order to avoid infinite recursion,
	# don't call _checkSignal() if noCheck is set.
	if not noCheck:
		_checkSignal()
	getProcessMapLock().acquire()
	try:
		currentThread = getCurrentThread()
		assert currentThread in getProcessMap(), \
				'Only the main thread or threads created by spawn*() may invoke self()'
		result = getProcessMap()[currentThread]
	finally:
		getProcessMapLock().release()
	return result

# Alternate name so that the self() function can be used in class methods where
# 'self' is already defined:
self_ = self


def exit(*args):
	"""kill a process"""
	_checkSignal()
	numArgs = len(args)
	if numArgs == 0 or numArgs > 2:
		raise ExitError('badarg')
	if numArgs == 1:
		raise ExitError(args[0])
	elif not isinstance(args[0], Process):
		raise ExitError('badarg')
	args[0]._signal(ExitError(args[1]))
	return True


def link(proc):
	"""link to a process"""
	_checkSignal()
	if not isinstance(proc, Process):
		raise ExitError('badarg')
	selfProc = self()
	selfProc._addLink(proc)
	# The above call may raise a 'noproc' signal
	_checkSignal()
	proc._addLink(selfProc)
	return True


def unlink(proc):
	"""remove link to a process"""
	_checkSignal()
	if not isinstance(proc, Process):
		raise ExitError('badarg')
	selfProc = self()
	proc._removeLink(selfProc)
	selfProc._removeLink(proc)
	return True


def processFlag(flag, value):
	"""set a process flag"""
	return self()._processFlag(flag, value)


def processes():
	"""list all active processes"""
	_checkSignal()
	getProcessMapLock().acquire()
	try:
		return getProcessMap().values()
	finally:
		getProcessMapLock().release()
	# end try


def isProcessAlive(proc):
	"""return True if process is active"""
	if not isinstance(proc, Process):
		raise ExitError('badarg')
	return proc.isAlive()


def send(proc, msg):
	"""send a message to process"""
	if not isinstance(proc, Process):
		raise ExitError('badarg')
	return proc.send(msg)


def _checkSignal():
	"""check if a signal has been sent to current process"""
	self(True)._checkSignal()


class ExitError(Exception):

	"""raised by EXIT signals"""

	def __init__(self, reason, proc=None):
		Exception.__init__(self, reason)
		self.reason = reason
		if proc is None:
			self.proc = self_()
		else:
			self.proc = proc
		# end if


# We can't import these at the top, since the process module imports this one
from candygram.process import Process, getProcessMap, getProcessMapLock
