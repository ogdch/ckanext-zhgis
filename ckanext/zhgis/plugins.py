import ckan
import ckan.plugins as p
from pylons import config

class ZhGisHarvest(p.SingletonPlugin):
    """
    Plugin containg the harvester for zhgis
    """
