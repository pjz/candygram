# I hereby disclaim all copyright to the contents of this file,
# program_7.3_alt.py, and place it into the public domain.
#   -- Michael Hobbs


from candygram import *


demo_ = None


def start():
	global demo_
	demo_ = spawn(demo)
	return demo_


def demo():
	processFlag('trap_exit', True)
	demo1 = Demo1()
	demo1.demo1()


class Demo1:
	def __init__(self):
		self.stop = False

	def normalExit(self, msg):
		_, from_, _ = msg
		print 'Demo process received normal exit from %s' % from_

	def otherExit(self, msg):
		_, from_, reason = msg
		print 'Demo process received exit signal %s from %s' % (reason, from_)

	def finished(self):
		print 'Demo finished '
		self.stop = True

	def other(self, msg):
		print 'Demo process message %s' % msg

	def demo1(self):
		r = Receiver()
		r.addHandler(('EXIT', Process, 'normal'), self.normalExit, Message)
		r.addHandler(('EXIT', Process, Any), self.otherExit, Message)
		r.addHandler('finished_demo', self.finished)
		r.addHandler(Any, self.other, Message)
		for _ in r:
			if self.stop:
				break
			# end if
		return True


def demonstrate_normal():
	def func():
		link(demo_)
	spawn(func)


def demonstrate_exit(what):
	def func():
		link(demo_)
		exit(what)
	spawn(func)


def demonstrate_message(what):
	def func():
		demo_.send(what)
	spawn(func)


def demonstrate_error():
	def func():
		link(demo_)
		1 / 0
	spawn(func)
