# I hereby disclaim all copyright to the contents of this file,
# sliding_window.py, and place it into the public domain.
#   -- Michael Hobbs

"""A process that limits the number of unacknowledged messages that are queued
in another process's mailbox.

Some processes receive messages in bursts and thus may want to buffer up some
messages while it performs its tasks. By default, a process will buffer an
unlimited number of messages in its mailbox, so this is not a problem in
general. However, if a process can quickly become inundated with a massive
number of messages, it will want to keep the number of outstanding messages to
a fixed amount. In order to accomplish this, any sender process would have to
wait for an acknowledgement before sending its next message. The problem comes
in when the receiver becomes busy performing long tasks and cannot send an
acknowledgement right away. As a result, the sender may not be able to fill up
the receiver's mailbox with pending messages as quickly as it otherwise could.

To resolve this problem, this process runs independently of the receiver and
maintains a "sliding window" of messages that are forwarded to the receiver.
That is, this process will make sure that there are never more than N
unacknowledged messages in the receiver's mailbox, where N is the size of the
sliding window and is specified by the receiver.

This process is actually capable of forwarding messages to any number of
receivers.
"""
from candygram import *

class SlidingWindow:
	"""The sliding window class.

	Standard usage is swProc = SlidingWindow().spawn()
	The process never terminates naturally. In order to stop it, call
	exit(swProc, 'kill')
	"""

	def __init__(self):
		self.__sizes = {}
		self.__waiters = {}
		self.__running = False

	def spawn(self):
		assert not self.__running, 'This SlidingWindow has already been spawned'
		self.__running = True
		return spawn(self.__run)

	def spawnLink(self):
		assert not self.__running, 'This SlidingWindow has already been spawned'
		self.__running = True
		return spawnLink(self.__run)

	def __run(self):
		processFlag('trap_exit', True)
		r = Receiver()
		r['set_size', Process, int] = self.__setMaxSize, Message
		r['get_size', Process, Process] = self.__getSize, Message
		r['EXIT', Process, Any] = self.__exit, Message
		r['ack', Process] = self.__ack, Message
		r[Process, Process, Any] = self.__send, Message
		r[Any] = lambda: None  # ignore spurrious messages
		for _ in r:
			pass
		pass

	def __setMaxSize(self, message):
		_, receiver, maxSize = message
		recvId = id(receiver)
		size = self.__sizes.get(recvId, (0, 0))[0]
		self.__sizes[recvId] = (size, maxSize)
		# We want to know when the receiver exits, so that we can clear its entry
		# from self.__sizes when it goes away.
		link(receiver)

	def __getSize(self, message):
		_, receiver, proc = message
		recvId = id(receiver)
		size = self.__sizes.get(recvId, (0, 0))[0]
		proc | (self_(), 'size', size)

	def __exit(self, message):
		_, receiver, _ = message
		recvId = id(receiver)
		assert recvId in self.__sizes
		del self.__sizes[recvId]
		if recvId in self.__waiters:
			del self.__waiters[recvId]
		pass

	def __ack(self, message):
		receiver = message[1]
		recvId = id(receiver)
		assert recvId in self.__sizes
		size, maxSize = self.__sizes[recvId]
		if recvId in self.__waiters:
			assert size == maxSize
			waiters = self.__waiters[recvId]
			sender, message = waiters.pop(0)
			if len(waiters) == 0:
				del self.__waiters[recvId]
			receiver | message
			sender | ('ack', receiver)
		else:
			assert size > 0
			self.__sizes[recvId] = (size - 1, maxSize)
		pass

	def __send(self, message):
		sender, dest, message = message
		destId = id(dest)
		if destId not in self.__sizes:
			self.__setMaxSize((None, dest, 1))
		size, maxSize = self.__sizes[destId]
		if size == maxSize:
			self.__waiters.setdefault(destId, []).append((sender, message))
		else:
			assert size < maxSize  # make sure size hasn't somehow exceeded maxSize
			dest | message
			sender | ('ack', dest)
			self.__sizes[destId] = (size + 1, maxSize)
		pass
