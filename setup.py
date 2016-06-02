#!/usr/bin/env/ python
from setuptools import setup
import os
import subprocess

# edit setup details here
name='binpacking'
license='GNU GPLv3'
description='2D binpacking solver'
url=''
author='Brecht Baeten'
author_email='brecht.baeten@gmail.com'
packages=['binpacking']
install_requires=['pyomo','numpy','matplotlib']
classifiers = ['Programming Language :: Python :: 2.7']


################################################################################
# do not edit
################################################################################
# Get the git version
try:
	# get the current git branch
	branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD' ])[:-1]
	if not branch=='master':
		print('Warning: the current branch ({}) is not master.'.format(branch))

	# get the current git commit
	commit = subprocess.check_output(['git', 'rev-parse' ,'HEAD'])[:-1]

	# check the current commit has a tag
	try:
		tag = subprocess.check_output(['git', 'describe' ,'--exact-match', '--tags', commit])[:-1]
	except:
		print('Warning: the current commit has no tag.')
		tag = ''

	# parse the tag to a version number
	try:
		splittag = tag.split('.')
		version_major = int(splittag[0])
		version_minor = int(splittag[1])
		version_patch = int(splittag[2])
		version = tag
		
		# write the version to version.py
		for dir in packages:
			f = open( '{}//version.py'.format(dir), 'w')
			f.write( '__version__ = \'{}\''.format(version) )
			f.close()
			
	except:
		version_major = -1
		version_minor = -1
		version_patch = -1
		version = ''
		if not tag == '':
			print('Warning: the current tag ({}) does not describe a version number.'.format(tag))
		
except:
	print('Warning: probably no git version control')
	version = ''
	

	
# run the setup command
setup(
    name=name,
    version=version,
    license=license,
	description=description,
	long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
	url=url,
	author=author,
	author_email=author_email,
	packages=packages,
	install_requires=install_requires,
	classifiers=classifiers,
)