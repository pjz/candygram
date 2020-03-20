"""Tests that patterns in documentation work as advertised"""


import unittest
import time

import pytest
import candygram as cg


# These exceptions won't be raised until the Python interpreter exits, so they
# can't really be tested as a suite. Simply comment one out below to test it
# on the command line
class TestExitException:

	def exception(self):
		raise Exception('test exception')

	def testExit(self):
		proc = cg.spawnLink(self.exception)
		time.sleep(0.1)

	def testDoubleException(self):
		with pytest.raises(Exception, match="test exception"):
			proc = cg.spawnLink(self.exception)
			time.sleep(0.1)
			raise Exception('second exception')


if __name__ == '__main__':
	test = TestExitException()
	#~ test.testExit()
	#~ test.testDoubleException()
