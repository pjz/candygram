# receiver.py
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

"""Receiver class"""

__revision__ = '$Id: receiver.py,v 1.4 2004/08/18 22:10:24 hobb0001 Exp $'

from candygram import _checkSignal, self_
from pattern import genFilter
import types
import time
import weakref



Message = object()

class Receiver:
	"""Retrieves messages from process's mailbox"""
	def __init__(self):
		_checkSignal()
		self.__handlers = []
		self.__lastMessage = 0
		self.__owner = self_()
		self.__mailbox = self.__owner._mailbox
		self.__mailboxCondition = self.__owner._mailboxCondition
		self.__timeout = None
		self.__timeoutHandler = None
		self.__timeoutArgs = None
		self.__timeoutKWArgs = None
		self.__receiverRefs = self.__owner._receiverRefs
		self.__receiverRefsLock = self.__owner._receiverRefsLock
		self.__receiverRefsLock.acquire()
		self.__receiverRefs.append(weakref.ref(self, self.__finalizeRef))
		self.__receiverRefsLock.release()

	def __finalizeRef(self, ref):
		"""called when no more [strong] references to self"""
		assert ref is self
		self.__receiverRefsLock.acquire()
		for i in range(len(self.__receiverRefs)):
			if self.__receiverRefs[i]() is ref:
				del self.__receiverRefs[i]
				break
			pass
		self.__receiverRefsLock.release()

	def addHandler(self, pattern, handler=None, *args, **kwargs):
		"""add pattern handler to receiver"""
		_checkSignal()
		self.__checkOwner()
		if handler is not None:
			assert callable(handler),'The handler value must be callable'
		filter_ = genFilter(pattern)
		self.__handlers.append((filter_, handler, args, kwargs))
		# Clear all skipped messages, since the new handler might be able to handle
		# them.
		self.__lastMessage = 0
		return filter_

	def after(self, timeout, handler=None, *args, **kwargs):
		"""add timeout handler to receiver"""
		_checkSignal()
		self.__checkOwner()
		self.__setAfter(timeout, handler, args, kwargs)

	def __setitem__(self, key, value):
		if type(value) is types.TupleType:
			self.addHandler(key, value[0], *value[1:])
		else:
			self.addHandler(key, value)
		pass

	def __getitem__(self, key):
		self.addHandler(key)
		return None

	def addHandlers(self, receiver):
		"""copy handlers from receiver to self"""
		_checkSignal()
		self.__checkOwner()
		self.__handlers.extend(receiver.__handlers)
		# Clear all skipped messages, since the new handler might be able to handle
		# them.
		self.__lastMessage = 0

	def receive(self, timeout=None, handler=None, *args, **kwargs):
		"""retrieve one message from mailbox"""
		_checkSignal()
		self.__checkOwner()
		if timeout is not None:
			self.__setAfter(timeout, handler, args, kwargs)
		expire = None
		if self.__timeout is not None:
			expire = time.time() + self.__timeout
		handlerInfo = None
		self.__mailboxCondition.acquire()
		while handlerInfo is None:
			handlerInfo = self.__scanMailbox()
			# If none of the filters picked up a message from the mailbox, wait
			# until a new message is sent and then try again.
			if handlerInfo is None:
				handlerInfo = self.__wait(expire)
			pass
		self.__mailboxCondition.release()
		if timeout is not None:
			self.__removeAfter()
		message, handler, args, kwargs = handlerInfo
		if handler is None:
			return None
		args = _replaceMessageArgs(args, message)
		kwargs = _replaceMessageKWArgs(kwargs, message)
		return handler(*args, **kwargs)

	__call__ = receive
	next = receive

	def __iter__(self):
		return self

	def __setAfter(self, timeout, handler, args, kwargs):
		"""set timeout handler"""
		assert self.__timeout is None, 'A timeout has already been set for this '\
				'Receiver'
		assert type(timeout) is types.IntType,'The timeout value must be an integer'
		if handler is not None:
			assert callable(handler),'The handler value must be callable'
		# Timeout is specified in milliseconds
		self.__timeout = float(timeout) / 1000
		self.__timeoutHandler = handler
		self.__timeoutArgs = args
		self.__timeoutKWArgs = kwargs

	def __removeAfter(self):
		"""remove timeout handler"""
		assert self.__timeout is not None
		self.__timeout = None
		self.__timeoutHandler = None
		self.__timeoutArgs = None
		self.__timeoutKWArgs = None

	def __scanMailbox(self):
		"""see if any message in mailbox matches a registered pattern"""
		assert self.__mailboxCondition.locked()
		for i in xrange(self.__lastMessage, len(self.__mailbox)):
			message = self.__mailbox[i]
			for filter_, handler, args, kwargs in self.__handlers:
				if filter_(message):
					self.__deleteMessage(i)
					return message, handler, args, kwargs
				pass
			self.__lastMessage = i + 1
		return None

	def __deleteMessage(self, i):
		"""remove i'th message from mailbox, notifying any other receivers"""
		assert self.__mailboxCondition.locked()
		self.__receiverRefsLock.acquire()
		del self.__mailbox[i]
		for ref in self.__receiverRefs:
			receiver = ref()
			assert receiver is not None  # __finalizeRef() should not leave any strays
			if receiver.__lastMessage > i:
				receiver.__lastMessage -= 1
			pass
		self.__receiverRefsLock.release()

	def __wait(self, expire):
		"""wait expire milliseconds for a new message"""
		waitTime = None
		if expire is not None:
			waitTime = max(0, expire - time.time())
		if not self.__mailboxCondition.wait(waitTime):
			return None, self.__timeoutHandler, self.__timeoutArgs, \
					self.__timeoutKWArgs
		# We may have been woken up by a signal
		_checkSignal()
		return None

	def __checkOwner(self):
		"""check that current process is owner of this receiver"""
		assert self_() is self.__owner, 'Only the process that created a Receiver '\
				'may invoke its methods'

def _replaceMessageArgs(args, message):
	"""replace any instance of Message with message"""
	result = []
	for arg in args:
		if arg is Message:
			result.append(message)
		else:
			result.append(arg)
		pass
	return result

def _replaceMessageKWArgs(kwargs, message):
	"""replace any instance of Message with message"""
	result = {}
	for key, value in kwargs.items():
		if value is Message:
			result[key] = message
		else:
			result[key] = value
		pass
	return result
