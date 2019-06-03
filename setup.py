from graphgen.nauty import NAUTY_PATH

from setuptools import setup
import setuptools.command.develop
import setuptools.command.build_py
from subprocess import check_call

def _install_nauty():
	"""
	Install the Nauty library.
	"""

	check_call(['make', 'clean', '-C', NAUTY_PATH])
	check_call(['make', '-C', NAUTY_PATH])

def _custom_install():
	"""
	Custom installation.
	"""

	_install_nauty()

class develop(setuptools.command.develop.develop):
	def run(self):
		_custom_install()

		setuptools.command.develop.develop.run(self)

class build(setuptools.command.build_py.build_py):
	def run(self):
		_custom_install()

		setuptools.command.build_py.build_py.run(self)

setup(name='graphgen',
	  version='1.0',
	  description='A library for random graph generation',
	  url='https://github.com/Nico-Salamone/graphgen',
	  author='Nico Salamone',
	  author_email='nico.salamone2411@gmail.com',
	  license='MIT',
	  python_requires='>=3.0.*',
	  install_requires=['networkx',
						'numpy',
						'scipy'],
	  include_package_data=True,
	  cmdclass={
		'develop': develop,
		'build_py': build
	  },
	  classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Intended Audience :: Developers',
		'Intended Audience :: Education',
		'Intended Audience :: Science/Research',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 3 :: Only',
		'Topic :: Software Development :: Libraries',
		'Topic :: Software Development :: Libraries :: Python Modules'
	  ],
	  packages=['graphgen'])
