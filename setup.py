#!/usr/bin/env/ python
from setuptools import setup
import os
import sys
import subprocess

# edit setup details here
name='binpacking'
license='GNU GPLv3'
description='A package for solving 2D binpacking problems'
url=''
author='Brecht Baeten'
author_email='brecht.baeten@gmail.com'
packages=['binpacking']
install_requires=['numpy','matplotlib','pyomo']
classifiers = ['Programming Language :: Python :: 2.7']
version = '0.0.1'

changelog = ''

################################################################################
# do not edit
################################################################################
if sys.argv[-1] == 'version':
	
	branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD' ])[:-1]

	if not branch=='master':
		raise ValueError('the current branch ({}) is not master.'.format(branch))
		
	# get the old version number from version.py
	try:
		versionfilename = '{}//__version__.py'.format(packages[0])
		f = open( versionfilename, 'r')
		content = f.readline()
		splitcontent = content.split('\'')
		oldversion = splitcontent[1]
		splitoldversion = oldversion.split('.')
		f.close()

		# check if the new version is higher than the old version
		splitversion = version.split('.')
		if sum([int(v)*1000**i for i,v in enumerate(splitversion[::-1])]) <= sum([int(v)*1000**i for i,v in enumerate(splitoldversion[::-1])]):
			raise ValueError('the new version ({}) is not higher than the old version ({})'.format(version,oldversion))
	except:
		raise Exception('Error while checking the version number. Check __version__.py')
		
	# write the version to version.py
	f = open( versionfilename, 'w')
	f.write( 'version = \'{}\''.format(version) )
	f.close()
		
	print('Creating a new distribution version for {}'.format(name) )	
	print('GIT branch: {}'.format(branch) )
	print('Version: {}'.format(version) )
	print('Changelog:\n{}'.format(changelog) )
	
	# create a commit message
	message = 'Created new version\nVersion: {}'.format(version)
	
	if not changelog == '':
		# add the changelog to the commit message
		message = message + '\n\nChangelog:\n{}'.format(changelog)
	
	message = message + '\n\nThis is an automated commit.'
	
	# create the commit
	output = subprocess.check_output(['git', 'commit', '-a', '-m', message])[:-1]
	
	# add a git tag
	output = subprocess.check_output(['git', 'tag' ,'{}'.format(version)])[:-1]
	
else:	
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