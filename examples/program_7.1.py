# I hereby disclaim all copyright to the contents of this file,
# program_7.1.py, and place it into the public domain.
#   -- Michael Hobbs

from candygram import *

my_name = None

def start():
	global my_name
	my_name = spawn(process)
	return my_name

def process():
	r = Receiver()
	def stop(msg):
		_, method = msg
		if method == 'return':
			return True
		else:
			exit('normal')
		pass
	r['stop', Any] = stop, Message
	r[Any] = process
	return r()
