# I hereby disclaim all copyright to the contents of this file,
# program_5.1_alt.py, and place it into the public domain.
#   -- Michael Hobbs

from candygram import *

def start():
	loop = Loop()
	return spawn(loop.loop)

class Loop:
	def __init__(self):
		self.val = 0

	def increment(self):
		self.val += 1

	def loop(self):
		r = Receiver()
		r.addHandler('increment', self.increment)
		while True:
			r.receive()
		pass
