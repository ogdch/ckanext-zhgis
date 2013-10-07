#n -*- coding: utf-8 -*-

import random
import os
import shutil
import tempfile
import zipfile
from pprint import pprint
from collections import defaultdict

from ckan.lib.base import c
from ckan import model
from ckan.model import Session, Package
from ckan.logic import ValidationError, NotFound, get_action, action
from ckan.lib.helpers import json
from ckanext.harvest.harvesters.base import munge_tag
from ckan.lib.munge import munge_title_to_name

from ckanext.harvest.model import HarvestJob, HarvestObject, HarvestGatherError, HarvestObjectError
from base import OGDCHHarvesterBase

from ckanext.zhgis.helpers import ckan_csw
from ckanext.zhgis.helpers import s3

import logging
log = logging.getLogger(__name__)

class ZhGisHarvester(OGDCHHarvesterBase):
    '''
    The harvester for zhgis
    '''

    def info(self):
        return {
            'name': 'zhgis',
            'title': 'zhgis',
            'description': 'Harvests the zhgis data',
            'form_config_interface': 'Text'
        }

    def gather_stage(self, harvest_job):
        log.debug('In ZhGisHarvester gather_stage')

    def fetch_stage(self, harvest_object):
        log.debug('In ZhGisHarvester fetch_stage')

    def import_stage(self, harvest_object):
        log.debug('In ZhGisHarvester import_stage')
