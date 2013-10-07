import logging
import ckan.lib.cli
import sys

from ckanext.zhgis.helpers import s3
from ckanext.zhgis.helpers import ckan_csw


class ZhGisCommand(ckan.lib.cli.CkanCommand):
    '''Command to handle zhgis data

    Usage:

        # Show this help
        paster --plugin=ckanext-zhgis zhgis help -c <path to config file>

        # Import datasets
        paster --plugin=ckanext-zhgis zhgis import -c <path to config file>

        # List all files in the S3 bucket
        paster --plugin=ckanext-zhgis zhgis list -c <path to config file>

        # Show output from CSW, 'query' is typically the name of a dataset like 'swissboundaries3D'
        paster --plugin=ckanext-zhgis zhgis csw <query> -c <path to config file>

    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__

    def command(self):
        # load pylons config
        self._load_config()
        options = {
                'import': self.importCmd,
                'list': self.listCmd,
                'csw': self.cswCmd,
                'help': self.helpCmd,
        }

        try:
            cmd = self.args[0]
            options[cmd](*self.args[1:])
        except KeyError:
            self.helpCmd()
            sys.exit(1)

    def helpCmd(self):
        print self.__doc__

    def listCmd(self):
        s3_helper = s3.S3();
        for file in s3_helper.list():
            print file

    def cswCmd(self, query=None, lang='de'):
        if (query is None):
            print "Argument 'query' must be set"
            self.helpCmd()
            sys.exit(1)
        csw = ckan_csw.SwisstopoCkanMetadata();
        print csw.get_ckan_metadata(query, lang)


    def importCmd(self):
        raise NotImplementedError

    def showCmd(self):
        raise NotImplementedError
