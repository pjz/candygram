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

import thread_impl
import types

# TODO: test program 7.2 behavior against current Erlang


def spawn(func, *args, **kwargs):
	_checkSignal()
	t = type(func)
	if not callable(t):
		raise ExitError('badarg')
	return _ThreadProcess(func, args, kwargs)

def spawnLink(func, *args, **kwargs):
	_checkSignal()
	t = type(func)
	if not callable(t):
		raise ExitError('badarg')
	return _ThreadProcess(func, args, kwargs, self())

def self(__noCheck=False):
	# _checkSignal() needs to invoke self(). In order to avoid infinite recursion,
	# don't call _checkSignal() if __noCheck is set.
	if not __noCheck:
		_checkSignal()
	ProcessMapLock().acquire()
	try:
		currentThread = thread_impl.getCurrentThread()
		assert currentThread in ProcessMap(), 'Only the main thread or threads ' \
				'created by spawn*() may invoke self()'
		result = ProcessMap()[currentThread]
	finally:
		ProcessMapLock().release()
	return result

# Alternate name so that the self() function can be used in class methods where
# 'self' is already defined:
self_ = self

def exit(*args):
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
	_checkSignal()
	if not isinstance(proc, Process):
		raise ExitError('badarg')
	selfProc = self()
	proc._removeLink(selfProc)
	selfProc._removeLink(proc)
	return True

def processFlag(flag, value):
	return self()._processFlag(flag, value)

def processes():
	_checkSignal()
	ProcessMapLock().acquire()
	try:
		return ProcessMap().values()
	finally:
		ProcessMapLock().release()
	pass

def isProcessAlive(proc):
	if not isinstance(proc, Process):
		raise ExitError('badarg')
	return proc.isAlive()

def send(proc, msg):
	if not isinstance(proc, Process):
		raise ExitError('badarg')
	return proc.send(msg)



class ExitError(Exception):
	def __init__(self, reason, proc=None):
		Exception.__init__(self, reason)
		self.reason = reason
		if proc is None:
			self.proc = self_()
		else:
			self.proc = proc
		pass



def _checkSignal():
	self(True)._checkSignal()



# We can't import these at the top, since the process module imports this one
from process import Process, _ThreadProcess, ProcessMap, ProcessMapLock
