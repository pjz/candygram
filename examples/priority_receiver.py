# I hereby disclaim all copyright to the contents of this file,
# priority_receiver.py, and place it into the public domain.
#   -- Michael Hobbs


from candygram import *


TIMEOUT = object


def timeout():
	return TIMEOUT


class PriorityReceiver:
	def __init__(self, receivers):
		self.__receivers = []
		prevReceiver = None
		for receiver in receivers:
			mergedReceiver = Receiver()
			if prevReceiver is not None:
				mergedReceiver.addHandlers(prevReceiver)
			mergedReceiver.addHandlers(receiver)
			self.__receivers.append(mergedReceiver)
			prevReceiver = mergedReceiver
		# end for

	def receive(self, *args, **kwargs):
		for receiver in self.__receivers[:-1]:
			result = receiver.receive(0, timeout)
			if result is not TIMEOUT:
				return result
			# end if
		return self.__receivers[-1].receive(*args, **kwargs)

	__call__ = receive
	next = receive

	def __iter__(self):
		return self
