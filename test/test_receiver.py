"""Tests that patterns in documentation work as advertised"""


import unittest
import sys
import StringIO

import candygram as cg


class TestReceiver(unittest.TestCase):

	def receive(self, receiver):
		receiver.receive()

	def testSingleProc(self):
		r = cg.Receiver()
		r.addHandler(1, cg.self().send, 'one')
		proc = cg.spawn(self.receive, r)
		proc.send(1)
		r = cg.Receiver()
		r.addHandler('one', lambda: 'success')
		self.assertEqual(r.receive(1000), 'success')
		cg.exit(proc, 'kill')

	def testMultiProc(self):
		r1 = cg.Receiver()
		r1.addHandler(1, cg.self().send, 'one')
		proc1 = cg.spawn(self.receive, r1)
		proc2 = cg.spawn(self.receive, r1)
		proc1.send(1)
		proc2.send(1)
		r = cg.Receiver()
		r.addHandler('one', lambda: 'success')
		self.assertEqual(r.receive(1000), 'success')
		self.assertEqual(r.receive(1000), 'success')
		proc3 = cg.spawn(self.receive, r1)
		proc3.send(1)
		self.assertEqual(r.receive(1000), 'success')
		cg.exit(proc1, 'kill')
		cg.exit(proc2, 'kill')
		cg.exit(proc3, 'kill')

	def testReset(self):
		# test that Receiver resets pointer back to front of mailbox after switching
		# to another process
		r1 = cg.Receiver()
		r1.addHandler(1, cg.self().send, 'one')
		proc1 = cg.spawn(self.receive, r1)
		proc1.send(2)
		proc1.send(1)
		r = cg.Receiver()
		r.addHandler('one', lambda: 'success')
		self.assertEqual(r.receive(1000), 'success')
		proc2 = cg.spawn(self.receive, r1)
		proc2.send(1)
		self.assertEqual(r.receive(1000), 'success')
		cg.exit(proc1, 'kill')
		cg.exit(proc2, 'kill')
