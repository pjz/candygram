"""Tests that patterns in documentation work as advertised"""


import unittest

import candygram as cg


class TestPatterns(unittest.TestCase):
	
	def setUp(self):
		self.r = cg.Receiver()
		
	def setPattern(self, pattern):
		self.r.addHandler(pattern, lambda: 'match')
		self.r.addHandler(cg.Any, lambda: 'non-match')
		
	def assertMatch(self, value):
		cg.self().send(value)
		self.assertEqual(self.r.receive(), 'match')
		
	def assertNonMatch(self, value):
		cg.self().send(value)
		self.assertEqual(self.r.receive(), 'non-match')
		
	def testAny(self):
		self.setPattern(cg.Any)
		self.assertMatch('shark')
		self.assertMatch(13.7)
		self.assertMatch((1, '', lambda: True))
		
	def testShark(self):
		self.setPattern('shark')
		self.assertMatch('shark')
		self.assertNonMatch('dolphin')
		self.assertNonMatch(42)
		self.assertNonMatch([])
		
	def test13_7(self):
		self.setPattern(13.7)
		self.assertMatch(13.7)
		self.assertNonMatch('shark')
		self.assertNonMatch(13.6)
		self.assertNonMatch({'A': 14})
		
	def testInt(self):
		self.setPattern(int)
		self.assertMatch(13)
		self.assertMatch(42)
		self.assertMatch(0)
		self.assertNonMatch('shark')
		self.assertNonMatch(13.7)
		self.assertNonMatch([])
		
	def testStr(self):
		self.setPattern(str)
		self.assertMatch('shark')
		self.assertMatch('')
		self.assertMatch('dolphin')
		self.assertNonMatch(42)
		self.assertNonMatch(0.9)
		self.assertNonMatch(lambda: True)

	def testLambda(self):
		self.setPattern(lambda x: x > 20)
		self.assertMatch(42)
		self.assertMatch(100)
		self.assertMatch(67.7)
		self.assertNonMatch(13)
		self.assertNonMatch(0)
		self.assertNonMatch(-67.7)
		
	def testTuple(self):
		self.setPattern((str, int))
		self.assertMatch(('shark', 42))
		self.assertMatch(('dolphin', 0))		
		self.assertNonMatch(['shark', 42])
		self.assertNonMatch(('dolphin', 42, 0))
		
	def testAnyRemaining(self):
		self.setPattern((str, int, cg.AnyRemaining))
		self.assertMatch(('dolphin', 0))
		self.assertMatch(('dolphin', 42, 0.9))
		self.assertNonMatch(('dolphin',))
		self.assertNonMatch((42, 'dolphin'))

	def testList(self):
		self.setPattern([str, 20, lambda x: x < 0])
		self.assertMatch(['shark', 20, -54.76])
		self.assertMatch(['dolphin', 20, -1])
		self.assertNonMatch(['shark', 21, -6])
		self.assertNonMatch([20, 20, -1])
		self.assertNonMatch(['', 20])
	
	def testDict(self):
		self.setPattern({'S': int, 19: str})
		self.assertMatch({'S': 3, 19: 'foo'})
		self.assertMatch({'S': -65, 19: 'bar', 'T': 'me'})
		self.assertNonMatch({'S': 'Charlie', 19: 'foo'})
		self.assertNonMatch({'S': 3})
		