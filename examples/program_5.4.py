# I hereby disclaim all copyright to the contents of this file,
# program_5.4.py, and place it into the public domain.
#   -- Michael Hobbs

from candygram import *

def timeout(time, alarm):
	return spawn(timer, self(), time, alarm)

def cancel(timer):
	return timer | (self(),'cancel')

def timer(pid, time, alarm):
	r = Receiver()
	r[Process, 'cancel'] = lambda: True
	return r(time, lambda: pid | alarm)
