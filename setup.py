# I hereby disclaim all copyright to the contents of this file,
# setup.py, and place it into the public domain.
#   -- Michael Hobbs


from distutils.core import setup
import distutils.command.install_data
from glob import glob
import os


PACKAGE = 'candygram'

examples = glob('examples/*.py')
docs = glob('doc/candygram/*')


class InstallData(distutils.command.install_data.install_data):

	"""need to change self.install_dir to the actual library dir"""

	def run(self):
		install_cmd = self.get_finalized_command('install')
		self.install_dir = getattr(install_cmd, 'install_lib')
		return distutils.command.install_data.install_data.run(self)


setup(name = 'Candygram',
		version = '1.0',
		license = 'GNU Lesser General Public License',
		url = 'http://candygram.sourceforge.net',
		author = 'Michael Hobbs',
		author_email = 'mike@hobbshouse.org',
		description = 'A Python implementation of Erlang concurrency primitives.',
		long_description = \
				'Candygram is a Python implementation of Erlang concurrency\n' \
				'primitives. Erlang is widely respected for its elegant built-in\n' \
				'facilities for concurrent programming. This package attempts to\n' \
				'emulate those facilities as closely as possible in Python. With\n' \
				'Candygram, developers can send and receive messages between threads\n'\
				'using semantics nearly identical to those in the Erlang language.',
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
		package_dir = {PACKAGE: 'src'},
		packages = [PACKAGE],
		data_files = [(PACKAGE+'/examples', examples),
				(PACKAGE+'/docs', docs),
				(PACKAGE, ['COPYING', 'ChangeLog'])],
		cmdclass = {'install_data': InstallData})
