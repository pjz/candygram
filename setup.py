# I hereby disclaim all copyright to the contents of this file,
# setup.py, and place it into the public domain.
#   -- Michael Hobbs

from distutils.core import setup
import distutils.command.install_data
from glob import glob

examples = glob('examples/*.py')
docs = glob('doc/candygram/*')

class InstallData(distutils.command.install_data.install_data):
	"""need to change self.install_dir to the actual library dir"""
	def run(self):
		install_cmd = self.get_finalized_command('install')
		self.install_dir = getattr(install_cmd, 'install_lib')
		return distutils.command.install_data.install_data.run(self)

setup(name = 'Candygram',
		version = '1.0 beta 1',
		license = 'GNU Lesser General Public License',
		url = 'http://candygram.sourceforge.net',
		author = 'Michael Hobbs',
		author_email = 'mike@hobbshouse.org',
		package_dir = {'candygram': 'src'},
		packages = ['candygram'],
		data_files = [('candygram/examples', examples), ('candygram/docs', docs)],
		cmdclass = {'install_data': InstallData})
