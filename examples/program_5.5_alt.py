# I hereby disclaim all copyright to the contents of this file,
# program_5.5_alt.py, and place it into the public domain.
#   -- Michael Hobbs


from candygram import *


number_analyser = None


def start():
	global number_analyser
	server = Server({})
	number_analyser = spawn(server.server)
	return number_analyser


# The interface functions.
def add_number(seq, dest):
	return request(('add_number',seq,dest))


def analyse(seq):
	return request(('analyse',seq))


def request(req):
	number_analyser.send((self(), req))
	r = Receiver()
	r.addHandler((number_analyser,Any), lambda msg: msg[1], Message)
	return r.receive()


# The server.
class Server:
	def __init__(self, analTable):
		self.analTable = analTable

	def sendAnal(self, msg):
		from_, (_, seq) = msg
		result = self.analTable.get(seq, None)
		from_.send((number_analyser, result))

	def sendAck(self, msg):
		from_, (_, seq, dest) = msg
		from_.send((number_analyser, 'ack'))
		self.analTable[seq] = dest

	def server(self):
		r = Receiver()
		r.addHandler((Process, ('analyse',str)), self.sendAnal, Message)
		r.addHandler((Process, ('add_number', str, Any)), self.sendAck, Message)
		for _ in r:
			pass
		return True
