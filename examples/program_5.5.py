# I hereby disclaim all copyright to the contents of this file,
# program_5.5.py, and place it into the public domain.
#   -- Michael Hobbs


from candygram import *


number_analyser = None


def start():
	global number_analyser
	number_analyser = spawn(server, {})
	return number_analyser


# The interface functions.
def add_number(seq, dest):
	return request(('add_number',seq,dest))


def analyse(seq):
	return request(('analyse',seq))


def request(req):
	number_analyser | (self(), req)
	r = Receiver()
	r[number_analyser,Any] = lambda msg: msg[1], Message
	return r()


# The server.
def server(analTable):
	r = Receiver()
	def sendAnal(msg):
		from_, (_, seq) = msg
		result = analTable.get(seq, None)
		from_ | (number_analyser, result)
		return server(analTable)
	r[Process, ('analyse',str)] = sendAnal, Message
	def sendAck(msg):
		from_, (_, seq, dest) = msg
		from_ | (number_analyser, 'ack')
		analTable[seq] = dest
		return server(analTable)
	r[Process, ('add_number', str, Any)] = sendAck, Message
	return r()
