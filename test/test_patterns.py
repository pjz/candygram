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
		self.assertMatch('text')
		self.assertMatch(13.7)
		self.assertMatch((1, '', lambda: True))

	def testShark(self):
		self.setPattern('land shark')
		self.assertMatch('land shark')
		self.assertNonMatch('dolphin')
		self.assertNonMatch(42)
		self.assertNonMatch([])

	def test13_7(self):
		self.setPattern(13.7)
		self.assertMatch(13.7)
		self.assertNonMatch('text')
		self.assertNonMatch(13.6)
		self.assertNonMatch({'A': 14})

	def testInt(self):
		self.setPattern(int)
		self.assertMatch(13)
		self.assertMatch(42)
		self.assertMatch(0)
		self.assertNonMatch('text')
		self.assertNonMatch(13.7)
		self.assertNonMatch([])

	def testStr(self):
		self.setPattern(str)
		self.assertMatch('plumber')
		self.assertMatch('')
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

	def testTuple2(self):
		self.setPattern((str, 20, lambda x: x < 0))
		self.assertMatch(('shark', 20, -54.76))
		self.assertMatch(('dolphin', 20, -1))
		self.assertNonMatch(('shark', 21, -6))
		self.assertNonMatch((20, 20, -1))
		self.assertNonMatch(('', 20))

	def testList(self):
		self.setPattern(['A', str, str])
		self.assertMatch(['A', 'B', 'C', 'D'])
		self.assertMatch(['A', 'B'])
		self.assertNonMatch(['C', 'B', 'A'])
		self.assertNonMatch(['A'])

	def testList2(self):
		self.setPattern([str, int])
		self.assertMatch(['dolphin', 42, 0])
		self.assertMatch(['shark'])
		self.assertNonMatch([42, 0])
		self.assertNonMatch(['dolphin', 42, 'shark'])

	def testList3(self):
		self.setPattern([cg.Any])
		self.assertMatch(['dolphin', 42, 0.9])
		self.assertMatch([])
		self.assertNonMatch(('dolphin', 42, 0.9))
		self.assertNonMatch('shark')

	def testDict(self):
		self.setPattern({'S': int, 19: str})
		self.assertMatch({'S': 3, 19: 'foo'})
		self.assertMatch({'S': -65, 19: 'bar', 'T': 'me'})
		self.assertNonMatch({'S': 'Charlie', 19: 'foo'})
		self.assertNonMatch({'S': 3})
