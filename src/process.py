# process.py
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

from candygram import ExitError, _checkSignal
import thread_impl
import condition
import types
import thread
import atexit
import sys

class Process:
	def __init__(self):
		self.__alive = True
		self._mailbox = []
		self._mailboxCondition = condition.Condition()
		self._receiverRefs = []
		self._receiverRefsLock = thread_impl.allocateLock()
		self.__signal = None
		self.__signalSet = False
		self.__trapExit = False
		self.__signalLock = thread_impl.allocateLock()
		self.__links = {}
		self.__linksLock = thread_impl.allocateLock()

	def isAlive(self):
		return self.__alive

	isProcessAlive = isAlive

	def send(self, message):
		_checkSignal()
		if not self.isAlive():
			return message
		self._mailboxCondition.acquire()
		self._mailbox.append(message)
		self._mailboxCondition.notify()
		self._mailboxCondition.release()
		return message

	__or__ = send

	def __repr__(self):
		return '<PID %d>' % id(self)

	def _signal(self, signal):
		assert isinstance(signal, ExitError)
		assert signal.proc is not self
		self.__signalLock.acquire()
		try:
			self._removeLink(signal.proc)
			if self.__trapExit and signal.reason != 'kill':
				self.send(('EXIT', signal.proc, signal.reason))
				return
			elif signal.reason == 'normal':
				return
			elif self.__signal is None:
				self.__signal = signal
				self.__signalSet = True
			pass
		finally:
			self.__signalLock.release()
		# Wake up process if it is waiting on a receive().
		self._mailboxCondition.acquire()
		self._mailboxCondition.notify()
		self._mailboxCondition.release()

	def _addLink(self, proc):
		if not proc.__alive:
			self._signal(ExitError('noproc', proc))
			return
		if proc is self:
			return
		self.__linksLock.acquire()
		self.__links[id(proc)] = proc
		self.__linksLock.release()

	def _removeLink(self, proc):
		procId = id(proc)
		self.__linksLock.acquire()
		if procId in self.__links:
			del self.__links[procId]
		self.__linksLock.release()

	def _exit(self, exitError):
		self.__alive = False
		self.__linksLock.acquire()
		links = self.__links.values()
		self.__linksLock.release()
		for proc in links:
			proc._signal(exitError)
		pass

	def _processFlag(self, flag, value):
		if flag == 'trap_exit':
			if type(value) is not types.BooleanType:
				raise ExitError('badarg')
			self.__signalLock.acquire()
			result = self.__trapExit
			self.__trapExit = value
			self.__signalLock.release()
			return result
		else:
			raise ExitError('badarg')
		pass

	def _checkSignal(self):
		# Since self.__signalSet is just a boolean value, we don't need to worry
		# about acquiring a lock before inspecting its value. This way, we can check
		# if a signal has been set much more quickly.
		if not self.__signalSet:
			return
		self.__signalLock.acquire()
		signal = self.__signal
		self.__signal = None
		self.__signalSet = False
		self.__signalLock.release()
		self._raise(signal)
		pass

	def _raise(self, signal):
		assert isinstance(signal, ExitError)
		reason = signal.reason
		if type(reason) is types.TupleType and len(reason) == 3 and \
				issubclass(reason[0], Exception):
			raise reason[0], reason[1], reason[2]
		raise signal



class _ThreadProcess(Process):
	def __init__(self, func, args, kwargs, initialLink=None):
		Process.__init__(self)
		self.__func = func
		self.__args = args
		self.__kwargs = kwargs
		if initialLink is not None:
			self._addLink(initialLink)
			initialLink._addLink(self)
		thread_impl.startThread(self.__run, ())

	def __run(self):
		currentThread = thread_impl.getCurrentThread()
		ProcessMapLock().acquire()
		ProcessMap()[currentThread] = self
		ProcessMapLock().release()
		exitError = ExitError('normal', self)
		try:
			self.__func(*self.__args, **self.__kwargs)
		except ExitError, e:
			exitError = e
		except:
			exitError = ExitError(sys.exc_info(), self)
		self._exit(exitError)
		ProcessMapLock().acquire()
		del ProcessMap()[currentThread]
		ProcessMapLock().release()



class _RootProcess(Process):
	def __init__(self):
		Process.__init__(self)
		atexit.register(self.__atexit)

	def __atexit(self):
		_checkSignal()
		self._exit(ExitError('normal', self))

_ProcessMap = None
_ProcessMapLock = None

def ProcessMap():
	global _ProcessMap
	if _ProcessMap is None:
		_ProcessMap = {thread_impl.getCurrentThread(): _RootProcess()}
	return _ProcessMap

def ProcessMapLock():
	global _ProcessMapLock
	if _ProcessMapLock is None:
		_ProcessMapLock = thread_impl.allocateLock()
	return _ProcessMapLock

