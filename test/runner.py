"""Executes all tests located in this directory"""


import sys
import os
import glob
import unittest


def loadCandygram(pwd):
	# Add the parent directory to sys.path so that we can import src
	parent = os.path.dirname(pwd)
	sys.path.insert(0, parent)
	# Import src and then rename it to 'candygram' in sys.modules
	#
	# Importing src causes src/__init__.py to import a bunch of candygram.* 
	# modules before we are able to redefine the candygram package. We therefore 
	# need to remove these modules, redefine src as candygram, and then reload 
	# src.
	import src
	for module in sys.modules.keys():
		if module.startswith('candygram'):
			del sys.modules[module]
		# end if
	sys.modules['candygram'] = src
	reload(src)


def main():
	pwd = os.path.dirname(os.path.abspath(sys.argv[0]))
	# Load the development version of Candygram so that unit test will use it,
	# instead of whatever is installed in site-packages.
	loadCandygram(pwd)
	# Locate all test modules in this script's directory.
	testFiles = glob.glob(os.path.join(pwd, 'test_*.py'))
	tests = [os.path.basename(file)[:-3] for file in testFiles]
	# Explicitly add this script's directory to sys.path so that we can import the
	# tests as modules.
	sys.path.insert(0, pwd)
	# Run all of each module's test cases.
	for test in tests:
		suite = unittest.defaultTestLoader.loadTestsFromName(test)
		unittest.TextTestRunner(verbosity=2).run(suite)
	# end for
	
	
if __name__ == '__main__':
	main()
	