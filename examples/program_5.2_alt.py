# I hereby disclaim all copyright to the contents of this file,
# program_5.2_alt.py, and place it into the public domain.
#   -- Michael Hobbs

from candygram import *

# First the interface functions.
def start():
	loop = Loop()
	return spawn(loop.loop)

def increment(counter):
	return counter.send('increment')

def value(counter):
	counter.send((self(),'value'))
	r = Receiver()
	r.addHandler((counter, int), lambda msg: msg[1], Message)
	return r.receive()

def stop(counter):
	return counter.send('stop')

# The counter loop.
class Loop:
	def __init__(self):
		self.val = 0
		self.stop = False

	def increment(self):
		self.val += 1

	def sendVal(self_, msg):
		from_, _ = msg
		from_.send((self(),self_.val))

	def stopFunc(self):
		self.stop = True

	def loop(self):
		r = Receiver()
		r.addHandler('increment', self.increment)
		r.addHandler((Process, 'value'), self.sendVal, Message)
		r.addHandler('stop', self.stopFunc)
		r.addHandler(Any) # All other messages
		while not self.stop:
			r.receive()
		return True
