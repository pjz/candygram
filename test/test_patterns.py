import candygram as cg
import unittest


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
