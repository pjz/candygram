"""Executes all tests located in this directory"""


import sys
import os
import glob
import unittest

def main():
	pwd = os.path.dirname(os.path.abspath(sys.argv[0]))
	# Locate all test modules in this script's directory.
	testFiles = glob.glob(os.path.join(pwd, 'test_*.py'))
	tests = [os.path.basename(file)[:-3] for file in testFiles]
	# Explicitly add this script's directory to sys.path so that we can import the
	# tests as modules.
	sys.path.insert(0, pwd)
	# Run all of each module's test cases.
	for test in tests:
		suite = unittest.defaultTestLoader.loadTestsFromName(test)
		result = unittest.TextTestRunner(verbosity=2).run(suite)
		if not result.wasSuccessful():
			break
		# end if
	# end for


if __name__ == '__main__':
	main()
