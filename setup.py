from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(
	name='ckanext-zhgis',
	version=version,
	description="CKAN extension of the Office for Spatial Development of the Canton of Zurich",
	long_description="""\
	""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	author='Liip AG',
	author_email='ogd@liip.ch',
	url='http://www.liip.ch',
	license='GPL',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.zhgis'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
	],
	entry_points=\
	"""
    [ckan.plugins]
    zhgis=ckanext.zhgis.plugins:ZhGisHarvest
    zhgis_harvester=ckanext.zhgis.harvesters:ZhGisHarvester
    [paste.paster_command]
    zhgis=ckanext.zhgis.commands.zhgis:ZhGisCommand
    zhgis_harvest=ckanext.zhgis.commands.harvester:Harvester
	""",
)
