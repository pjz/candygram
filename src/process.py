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

"""Process classes"""

__revision__ = '$Id: process.py,v 1.3 2004/08/18 22:10:24 hobb0001 Exp $'

from candygram import ExitError, _checkSignal
import thread_impl
import condition
import types
import atexit
import sys

class Process:
	"""Abstract Process class"""
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
		"""Return True if process is still running"""
		return self.__alive

	isProcessAlive = isAlive

	def send(self, message):
		"""Send message to process"""
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
		"""Send signal to process"""
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
		"""link a proc with this process"""
		if not proc.__alive:
			self._signal(ExitError('noproc', proc))
			return
		if proc is self:
			return
		self.__linksLock.acquire()
		self.__links[id(proc)] = proc
		self.__linksLock.release()

	def _removeLink(self, proc):
		"""remove link to proc from this process"""
		procId = id(proc)
		self.__linksLock.acquire()
		if procId in self.__links:
			del self.__links[procId]
		self.__linksLock.release()

	def _exit(self, exitError):
		"""signal that process has terminated"""
		self.__alive = False
		self.__linksLock.acquire()
		links = self.__links.values()
		self.__linksLock.release()
		for proc in links:
			proc._signal(exitError)
		pass

	def _processFlag(self, flag, value):
		"""set a process flag"""
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
		"""check if a signal has been received"""
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
		"""raise an exception for signal"""
		assert isinstance(signal, ExitError)
		reason = signal.reason
		if type(reason) is types.TupleType and len(reason) == 3 and \
				issubclass(reason[0], Exception):
			raise reason[0], reason[1], reason[2]
		raise signal



class ThreadProcess(Process):
	"""A process that is running on a thread"""
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
		"""main function of thread"""
		currentThread = thread_impl.getCurrentThread()
		getProcessMapLock().acquire()
		getProcessMap()[currentThread] = self
		getProcessMapLock().release()
		exitError = ExitError('normal', self)
		try:
			self.__func(*self.__args, **self.__kwargs)
		except ExitError, ex:
			exitError = ex
		except:
			exitError = ExitError(sys.exc_info(), self)
		self._exit(exitError)
		getProcessMapLock().acquire()
		del getProcessMap()[currentThread]
		getProcessMapLock().release()



class RootProcess(Process):
	"""a process that represents the main thread"""
	def __init__(self):
		Process.__init__(self)
		atexit.register(self.__atexit)

	def __atexit(self):
		"""invoked when interpreter is exiting"""
		_checkSignal()
		self._exit(ExitError('normal', self))

ProcessMap = None
ProcessMapLock = None

def getProcessMap():
	"""return value of ProcessMap"""
	global ProcessMap
	if ProcessMap is None:
		ProcessMap = {thread_impl.getCurrentThread(): RootProcess()}
	return ProcessMap

def getProcessMapLock():
	"""return value of ProcessMapLock"""
	global ProcessMapLock
	if ProcessMapLock is None:
		ProcessMapLock = thread_impl.allocateLock()
	return ProcessMapLock

