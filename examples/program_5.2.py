# I hereby disclaim all copyright to the contents of this file,
# program_5.2.py, and place it into the public domain.
#   -- Michael Hobbs


from candygram import *


# First the interface functions.
def start():
	return spawn(loop, 0)


def increment(counter):
	return counter | 'increment'


def value(counter):
	counter | (self(),'value')
	r = Receiver()
	r[counter, int] = lambda msg: msg[1], Message
	return r()


def stop(counter):
	return counter | 'stop'


# The counter loop.
def loop(val):
	r = Receiver()
	r['increment'] = loop, val + 1
	def sendVal(msg):
		from_, _ = msg
		from_ | (self(),val)
		return loop(val)
	r[Process, 'value'] = sendVal, Message
	r['stop'] = lambda: True  # No recursive call here
	r[Any] = loop, val  # All other messages
	return r()
