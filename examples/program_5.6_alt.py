# I hereby disclaim all copyright to the contents of this file,
# program_5.6_alt.py, and place it into the public domain.
#   -- Michael Hobbs


from candygram import *


resource_alloc = None


def start(resources):
	global resource_alloc
	server = Server(resources, [])
	pid = spawn(server.server)
	resource_alloc = pid
	return pid


# The interface functions.
def allocate():
	return request('alloc')


def free(resource):
	return request(('free',resource))


def request(req):
	resource_alloc.send((self(),req))
	r = Receiver()
	r.addHandler((resource_alloc,Any), lambda msg: msg[1], Message)
	return r.receive()


# The server.
class Server:
	def __init__(self, free, allocated):
		self.free = free
		self.allocated = allocated

	def server(self):
		r = Receiver()
		r.addHandler((Process,'alloc'), self.allocate, Message)
		r.addHandler((Process,('free',Any)), self.free_, Message)
		for _ in r:
			pass
		return True

	def allocate(self, msg):
		from_, _ = msg
		if self.free:
			r, self.free = self.free[0], self.free[1:]
			from_.send((resource_alloc,('yes',r)))
			self.allocated.insert(0, (r,from_))
		else:
			from_.send((resource_alloc,'no'))
		# end if

	def free_(self, msg):
		from_, (_, r) = msg
		if (r,from_) in self.allocated:
			from_.send((resource_alloc,'ok'))
			self.free.insert(0, r)
			self.allocated.remove((r,from_))
		else:
			from_.send((resource_alloc,'error'))
		# end if
