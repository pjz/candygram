"""Tests that patterns in documentation work as advertised"""


import unittest
import sys
import StringIO

import candygram as cg


class TestDeprecation(unittest.TestCase):

	def setUp(self):
		# Redirect stderr to a StringIO buffer.
		self.oldErr = sys.stderr
		sys.stderr = StringIO.StringIO()

	def tearDown(self):
		# Restore stderr
		sys.stderr.close()
		sys.stderr = self.oldErr

	def testAnyRemaining(self):
		r = cg.Receiver()
		r.addHandler([str, cg.AnyRemaining])
		stderr = sys.stderr.getvalue()
		# The text we want to compare is after the second colon:
		idx = stderr.index('test_deprecation.py') + 1
		idx = stderr.index(':', idx) + 1
		idx = stderr.index(':', idx) + 1
		self.assertEqual(stderr[idx:],
				' DeprecationWarning: ' \
				'The candygram.AnyRemaining constant is deprecated. ' \
				'Please use a standard list pattern instead.\n' \
				'  r.addHandler([str, cg.AnyRemaining])\n')
