# I hereby disclaim all copyright to the contents of this file,
# program_5.3_alt.py, and place it into the public domain.
#   -- Michael Hobbs

from candygram import *

def s():
	s1 = Receiver()
	s2 = Receiver()
	s3 = Receiver()
	s4 = Receiver()
	s1.addHandler('msg_a', lambda: s2)
	s1.addHandler('msg_c', lambda: s3)
	s2.addHandler('msg_x', lambda: s3)
	s2.addHandler('msg_h', lambda: s4)
	s3.addHandler('msg_b', lambda: s1)
	s3.addHandler('msg_y', lambda: s2)
	s4.addHandler('msg_i', lambda: s3)
	r = s1
	while True:
		r = r.receive()
	pass
