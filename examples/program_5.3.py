# I hereby disclaim all copyright to the contents of this file,
# program_5.3.py, and place it into the public domain.
#   -- Michael Hobbs


from candygram import *


def s1():
	r = Receiver()
	r['msg_a'] = s2
	r['msg_c'] = s3
	return r()


def s2():
	r = Receiver()
	r['msg_x'] = s3
	r['msg_h'] = s4
	return r()


def s3():
	r = Receiver()
	r['msg_b'] = s1
	r['msg_y'] = s2
	return r()


def s4():
	r = Receiver()
	r['msg_i'] = s3
	return r()
