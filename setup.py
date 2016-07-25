# I hereby disclaim all copyright to the contents of this file,
# setup.py, and place it into the public domain.
#   -- Michael Hobbs


from setuptools import setup, find_packages
from glob import glob


PACKAGE = 'candygram'


setup(name = 'Candygram',
		version = '1.0.1',
		license = 'GNU Lesser General Public License',
		url = 'http://candygram.sourceforge.net',
		author = 'Michael Hobbs',
		author_email = 'mike@hobbshouse.org',
		description = 'A Python implementation of Erlang concurrency primitives.',
		long_description =  """
				Candygram is a Python implementation of Erlang concurrency
				primitives. Erlang is widely respected for its elegant built-in
				facilities for concurrent programming. This package attempts to
				emulate those facilities as closely as possible in Python. With
				Candygram, developers can send and receive messages between threads
				using semantics nearly identical to those in the Erlang language.""",
		keywords = ['erlang', 'concurrent', 'threads', 'message', 'passing'],
		platforms = ['Python'],
		classifiers = [
				'Development Status :: 5 - Production/Stable',
				'Intended Audience :: Developers',
				'License :: OSI Approved :: ' \
						'GNU Library or Lesser General Public License (LGPL)',
				'Natural Language :: English',
				'Operating System :: Microsoft :: Windows',
				'Operating System :: OS Independent',
				'Operating System :: POSIX',
				'Programming Language :: Erlang',
				'Programming Language :: Python',
				'Topic :: Software Development :: Libraries :: Python Modules'],
		download_url = 'http://sourceforge.net/project/showfiles.php?' \
				'group_id=114295&package_id=123762&release_id=276784',
		packages = find_packages(),
		data_files = [
                (PACKAGE+'/examples', glob('examples/*.py')),
				(PACKAGE+'/docs', glob('doc/candygram/*')),
				(PACKAGE, ['COPYING', 'ChangeLog'])
        ],
        extras_require = { 'tests': [ 'pytest', 'pytest-timeout', 'pytest-cov' ] }
      )
