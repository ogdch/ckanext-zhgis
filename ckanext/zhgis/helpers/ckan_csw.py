# -*- coding: utf-8 -*-

from owslib.csw import CatalogueServiceWeb
from lxml import etree
import logging
log = logging.getLogger(__name__)

namespaces = {
    'atom': 'http://www.w3.org/2005/Atom',
    'che': 'http://www.geocat.ch/2008/che',
    'csw': 'http://www.opengis.net/cat/csw/2.0.2',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'dct': 'http://purl.org/dc/terms/',
    'dif': 'http://gcmd.gsfc.nasa.gov/Aboutus/xml/dif/',
    'fgdc': 'http://www.opengis.net/cat/csw/csdgm',
    'gco': 'http://www.isotc211.org/2005/gco',
    'gmd': 'http://www.isotc211.org/2005/gmd',
    'gml': 'http://www.opengis.net/gml',
    'ogc': 'http://www.opengis.net/ogc',
    'ows': 'http://www.opengis.net/ows',
    'rim': 'urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'srv': 'http://www.isotc211.org/2005/srv',
    'xs': 'http://www.w3.org/2001/XMLSchema',
    'xs2': 'http://www.w3.org/XML/Schema',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
}


class Attribute(object):
    def __init__(self, config, **kwargs):
        self._config = config
        self.env = kwargs

    def get_value(self, **kwargs):
        """ Abstract method to return the value of the attribute """
        raise NotImplementedError


class StringAttribute(Attribute):
    def get_value(self, **kwargs):
        return self._config


class XmlAttribute(Attribute):
    def get_value(self, **kwargs):
        self.env.update(kwargs)
        xml = self.env['xml']
        return etree.tostring(xml)


class XPathAttribute(Attribute):
    def get_element(self, xml, xpath):
        return xml.xpath(xpath, namespaces=namespaces)[0]

    def get_value(self, **kwargs):
        self.env.update(kwargs)
        xml = self.env['xml']

        lang = self.env['lang']
        xpath = self._config.replace('#DE', '#' + lang.upper())
        log.debug("Lang: %s, XPath: %s" % (lang, xpath))

        try:
            # this should probably return a XPathTextAttribute
            value = self.get_element(xml, xpath)
        except Exception as e:
            log.exception(e)
            value = ''
        return value


class XPathMultiAttribute(XPathAttribute):
    def get_element(self, xml, xpath):
        return xml.xpath(xpath, namespaces=namespaces)


class XPathTextAttribute(XPathAttribute):
    def get_value(self, **kwargs):
        value = super(XPathTextAttribute, self).get_value(**kwargs)
        return value.text if hasattr(value, 'text') else value


class XPathMultiTextAttribute(XPathMultiAttribute):
    def get_value(self, **kwargs):
        value = super(XPathMultiTextAttribute, self).get_value(**kwargs)
        return value.text if hasattr(value, 'text') else value


class CombinedAttribute(Attribute):
    def get_value(self, **kwargs):
        self.env.update(kwargs)
        value = ''
        if 'separator' in self.env:
            separator = self.env['separator']
        else:
            separator = ' '
        for attribute in self._config:
            new_value = attribute.get_value(**kwargs)
            if new_value is not None:
                value = value + attribute.get_value(**kwargs) + separator
        return value.strip(separator)


class MultiAttribute(Attribute):
    def get_value(self, **kwargs):
        self.env.update(kwargs)
        value = ''
        if 'separator' in self.env:
            separator = self.env['separator']
        else:
            separator = ' '
        for attribute in self._config:
            new_value = attribute.get_value(**kwargs)
            try:
                iterator = iter(new_value)
                for inner_attribute in iterator:
                    # it should be possible to call inner_attribute.get_value
                    # and the right thing(tm) happens'
                    if hasattr(inner_attribute, 'text'):
                        value = value + inner_attribute.text + separator
                    else:
                        value = value + inner_attribute + separator
            except TypeError:
                value = value + new_value + separator
        return value.strip(separator)


class ArrayAttribute(Attribute):
    def _isstr(s):
        try:
            return isinstance(s, basestring)
        except NameError:
            return isinstance(s, str)

    def get_value(self, **kwargs):
        self.env.update(kwargs)
        value = []
        for attribute in self._config:
            new_value = attribute.get_value(**kwargs)
            try:
                if self._isstr(new_value):
                    raise TypeError
                iterator = iter(new_value)
                for inner_attribute in iterator:
                    # it should be possible to call inner_attribute.get_value
                    # and the right thing(tm) happens'
                    if hasattr(inner_attribute, 'text'):
                        value.append(inner_attribute.text)
                    else:
                        value.append(inner_attribute)
            except TypeError:
                value.append(new_value)
        return value


class FirstInOrderAttribute(CombinedAttribute):
    def get_value(self, **kwargs):
        for attribute in self._config:
            value = attribute.get_value(**kwargs)
            if value != '':
                return value
        return ''


class CkanMetadata(object):
    """ Provides general access to CSW for CKAN """
    def __init__(self, url, schema, version='2.0.2', lang='en-US'):
        self.schema = schema
        self.catalog = CatalogueServiceWeb(
            url,
            lang,
            version,
            timeout=10,
            skip_caps=True
        )
        self.metadata = dict.fromkeys([
            'id',
            'name',
            'title',
            'url',
            'author',
            'maintainer',
            'maintainer_email',
            'license_url',
            'version',
            'service_url',
            'service_type',
            'notes',
            'tags',
            'metadata_url',
            'metadata_raw',
        ])

    def get_by_search(self, searchterm, propertyname='csw:AnyText'):
        """ Returns the found csw dataset with the given searchterm """
        self.catalog.getrecords(
            keywords=[searchterm],
            propertyname=propertyname
        )
        if (self.catalog.response is None or
                self.catalog.results['matches'] == 0):
            raise DatasetNotFoundError(
                "No dataset for the given searchterm '%s' (%s) found"
                % (searchterm, propertyname)
            )
        return self.catalog.records

    def get_by_id(self, id):
        """ Returns the csw dataset with the given id """
        self.catalog.getrecordbyid(id=[id], outputschema=self.schema)
        return self.catalog.response

    def get_id_by_dataset_name(self, dataset_name):
        """
            Returns the id of a dataset identified by it's name.
            If there are multiple datasets with the given name,
            only the id of the first one is returned.
        """
        dataset_list = self.get_by_search(dataset_name, 'title')
        return dataset_list.itervalues().next().identifier

    def get_attribute(self, ckan_attribute, dataset_name=None):
        """
        Abstract method to define the mapping
        of a ckan attribute to a csw attribute
        """
        raise NotImplementedError

    def get_xml(self, id):
        dataset_xml_string = self.get_by_id(id)
        if dataset_xml_string is None:
            raise DatasetNotFoundError("Dataset with id %s not found" % id)
        return dataset_xml_string

    def get_ckan_metadata_by_id(self, id, language='de'):
        log.debug("Dataset ID: %s" % id)

        dataset_xml = etree.fromstring(self.get_xml(id))
        for key in self.metadata:
            log.debug("Metadata key: %s" % key)
            attribute = self.get_attribute(key)
            self.metadata[key] = attribute.get_value(
                xml=dataset_xml,
                lang=language
            )
        return self.metadata

    def get_ckan_metadata(self, dataset_name, language='de'):
        """ Returns the requested dataset mapped to CKAN attributes """
        id = self.get_id_by_dataset_name(dataset_name)
        return self.get_ckan_metadata_by_id(id, language)


class ZhGisCkanMetadata(CkanMetadata):
    """ Provides access to the csw service of GIS-ZH metadata """

    default_mapping = {
        'id': XPathTextAttribute('.//gmd:fileIdentifier/gco:CharacterString'),
        'name': XPathTextAttribute(
            ".//gmd:identificationInfo//gmd:citation//gmd:title//gmd:textGroup"
            "/gmd:LocalisedCharacterString[@locale='#DE']"
        ),
        'title': FirstInOrderAttribute([
            XPathTextAttribute(
                ".//gmd:identificationInfo//gmd:citation//gmd:alternateTitle"
                "//gmd:textGroup/gmd:LocalisedCharacterString[@locale='#DE']"
            ),
            XPathTextAttribute(
                ".//gmd:identificationInfo//gmd:citation//gmd:title"
                "//gmd:textGroup/gmd:LocalisedCharacterString[@locale='#DE']"
            )
        ]),
        'url': XPathTextAttribute(
            ".//gmd:contact//gmd:onlineResource//gmd:linkage"
        ),
        'author': XPathTextAttribute(
            ".//gmd:contact//gmd:organisationName//gmd:textGroup"
            "/gmd:LocalisedCharacterString[@locale='#DE']"
        ),
        'maintainer': StringAttribute(u'GIS-Zentrum Kanton Zürich'),
        'maintainer_email': StringAttribute('gis@bd.zh.ch'),
        'license_url': StringAttribute(
            'http://www.are.zh.ch/internet/baudirektion/are/de/geoinformation/geodaten_uebersicht/Open_Data_Kanton_Zuerich.html#subtitle-content-internet-baudirektion-are-de-geoinformation-geodaten_uebersicht-Open_Data_Kanton_Zuerich-jcr-content-contentPar-textimage_1'  # noqa
        ),
        'version': XPathTextAttribute(
            ".//gmd:identificationInfo//gmd:citation//gmd:date/gco:Date"
        ),
        'service_url': XPathTextAttribute(
            ".//gmd:identificationInfo//srv:connectPoint//gmd:linkage"
            "//che:LocalisedURL[@locale='#DE']"
        ),
        'service_type': XPathTextAttribute(
            ".//gmd:identificationInfo//srv:serviceType//gco:LocalName"
        ),
        'notes': XPathTextAttribute(
            ".//gmd:identificationInfo//gmd:abstract//gmd:textGroup"
            "/gmd:LocalisedCharacterString[@locale='#DE']"
        ),
        'tags': ArrayAttribute([
            StringAttribute('gis'),
            StringAttribute('geodaten')]
        ),
        'metadata_url': StringAttribute(''),
        'metadata_raw': XmlAttribute(''),
    }

    def __init__(
            self,
            url='http://www.geocat.ch/geonetwork/srv/eng/csw?',
            schema='http://www.geocat.ch/2008/che',
            version='2.0.2',
            lang='en-US'):
        super(ZhGisCkanMetadata, self).__init__(url, schema, version, lang)

    def get_id_by_dataset_name(self, dataset_name):
        return super(ZhGisCkanMetadata, self).get_id_by_dataset_name(
            dataset_name
        )

    def get_mapping(self, dataset_name=None):
        return self.default_mapping

    def get_attribute(self, ckan_attribute, dataset_name=None):
        mapping = self.get_mapping(dataset_name)
        if ckan_attribute in mapping:
            return mapping[ckan_attribute]
        raise AttributeMappingNotFoundError(
            "No mapping found for attribute '%s'"
            % ckan_attribute
        )


class DatasetNotFoundError(Exception):
    pass


class AttributeMappingNotFoundError(Exception):
    pass
