#n -*- coding: utf-8 -*-

from ckan import model
from ckan.model import Session
from ckan.logic import get_action, action
from ckan.lib.helpers import json
from ckan.lib.munge import munge_title_to_name

from ckanext.harvest.model import HarvestObject
from ckanext.harvest.harvesters import HarvesterBase

from ckanext.zhgis.helpers import ckan_csw

import logging
log = logging.getLogger(__name__)


class ZhGisHarvester(HarvesterBase):
    '''
    The harvester for zhgis
    '''
    HARVEST_USER = u'harvest'

    DATASETS = {
        'c80f283d-6ab8-4ce4-a480-c7995c575b24': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=994',
            'tags': ['Archäologie', 'archäologische Zonen']
        },
        '1eac72b1-068d-4272-b011-d0010cc4bf676': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=691',
            'tags': ['Denkmalschutz', 'Denkmalpflege', 'Inventar', 'Schutzliste', 'Objektliste']
        },
        '0ef6823f-f46e-4df2-966b-3c52af8f1310': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=935',
            'tags': ['Denkmalschutz', 'Denkmalpflege', 'Inventar', 'Schutzliste', 'Objektliste']
        },
        '3a4782f1-d6c3-402b-bea0-8a160c3347491': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=265',
            'tags': ['Ortsbild', 'Ortsbildschutz', 'schutzwürdig']
        },
        'f454fd4d-d47d-47b6-b09b-21c7c865e61b3': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=290',
            'tags': ['Waldvegetation', 'Wald']
        },
        '690425da-b1bc-4f30-be01-c0a4af4f8d5f': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=1057',
            'tags': ['Schadstoffbelastung', 'Emissionen', 'Immissionen']
        },
        '238d1b4f-0039-4dc2-a171-c7b1bc72a2be': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=1058',
            'tags': ['Schadstoffbelastung', 'Emissionen', 'Immissionen']
        },
        '8eff8b9a-960a-42cb-afd0-daeb5f70813a': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=1054',
            'tags': ['Gemeinden', 'Gemeindegrenzen', 'administrative Grenzen', 'Hoheitsgrenzen']
        },
        'b3bd50ae-b026-40a0-8b39-1cbcd4c4ac98': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=1055',
            'tags': ['Haltestelle', 'ZVV', 'VBZ']
        },
        '8802b5b2-5c6a-46ad-9bf2-66757ebf04af': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=1056',
            'tags': ['Haltestelle', 'ZVV', 'VBZ']
        },
        '81d38577-6635-4394-803b-334d616967aa': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=1061',
            'tags': ['Siedlung', 'Siedlungsverzeichnis', 'Statistik']
        },
        '33cfa26c-c568-4972-bbc7-14ae52f9b319': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=956',
            'tags': []
        },
        '68a3f148-b3f5-4ba3-87d5-a26aafc03c14': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=955',
            'tags': []
        },
        'c34149b8-1ffe-46de-a3eb-01acb3fbeac5': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=870',
            'tags': ['Vögel', 'Feuchtgebiet', 'Ried', 'Flachmoor', 'Feuchtwiese', 'Heuschrecken', 'Geomorphologie', 'Geotope', 'Vegetationskartierung', 'Feuchtgebiete', 'Trockenstandorte', 'Libellen', 'Naturschutz', 'Biotope', 'Lichter Wald', 'Aktionsplan', 'Zielarten', 'Reptilien', 'Landschaftsschutz', 'Schutzverordnung', 'Pufferzone', 'Tagfalter', 'Sommervogel']
        },
        'b83d1172-bed6-4e04-a56c-fcc55995dbc9': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=931',
            'tags': ['Naturschutz', 'Biotope', 'Lichter Wald', 'Aktionsplan', 'Zielarten']
        },
        'fb796034-407d-4f8d-906b-3a1b52f828da': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=932',
            'tags': []
        },
        '22550ba0-da1e-433e-a39e-ee95607b19d6': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=930',
            'tags': []
        },
        'dff63f01-001a-4416-ae0f-9cb6ce14ffe6': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=913',
            'tags': ['Naturschutz', 'Landschaftsschutz', 'Schutzverordnung', 'Pufferzone']
        },
        '668e0bda-f150-48b0-aa05-38a5eac3cc16': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=933',
            'tags': []
        },
        '79bffc8f-e721-47d1-9ebf-d8a47c4cf3d0': {
        'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=1077',
        'tags': ['Neophyten', 'invasiv', 'Asiatischer Staudenknöterich', 'Riesenbärenklau', 'Essigbaum', 'Ambrosia', 'Goldrute', 'Drüsiges Springkraut']
        },
        '1ba987a4-0236-44e2-b5c0-f6cc5f167981': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=1120',
            'tags': ['Strasse', 'Strassenverkehr', 'Verkehrsnetz', 'Strassennetz', 'Nationalstrassen', 'Staatsstrassen', 'Kanton Zürich']
        },
        '893345ff-8c84-4495-9b2f-53c0ec8390f9': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=1119',
            'tags': ['Strasse', 'Strassenverkehr', 'Verkehrsnetz', 'Strassennetz', 'Nationalstrassen', 'Staatsstrassen', 'Kanton Zürich']
        },
        '3233bf0f-c87d-404f-ac34-98df45d5dc90': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=1118',
            'tags': ['Strasse', 'Strassenverkehr', 'Verkehrsnetz', 'Strassennetz', 'Nationalstrassen', 'Staatsstrassen', 'Kanton Zürich']
        },
        '86e20e7c-29fe-4840-8229-a540211d7bb5': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=1117',
            'tags': ['Strasse', 'Strassenverkehr', 'Verkehrsnetz', 'Strassennetz', 'Nationalstrassen', 'Staatsstrassen', 'Kanton Zürich']
        },
        'eda09949-0750-4eac-ba2b-6c78ca54d69e': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=1097',
            'tags': []
        },
        'a35fcf31-56f4-4b6d-b90a-54770a71bd8d': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=1178',
            'tags': []
        },
        '9f1cfeee-c40e-4e5b-84ba-f6c19048bcad': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=1217',
            'tags': ['Tiefbau', 'Strassen', 'Verkehr', 'Baustellen', 'Verkehrsbehinderung']
        },
        'e112d147-3b8e-42de-9b94-0ae23b05e3be': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=1297',
            'tags': []
        },
        'fc314cc0-6916-42d6-96ca-18dd9394d02d': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=1277',
            'tags': ['Wasser', 'Fluss', 'Bach', 'Ökomorphologie', 'Gewässer', 'Verbauung', 'Uferbereich']
        },
        '22b0d59f-363c-4643-929b-8a06cddf7f75': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=1197',
            'tags': ['Freianlagen', 'Sporthallen', 'Bäder', 'Eissportanlagen']
        },
        '2999470f-b6c8-458f-b10d-a55d2d86abde': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=1238',
            'tags': ['Velo', 'Radweg', 'Veloinfrastruktur', 'Velomarkierung', 'Radstreifen', 'Busspur']
        },
        '46cd5817-5ac4-4de9-909d-233bd319a6b9': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=1237',
            'tags': ['Velo', 'Parkierung', 'öffentlich', 'Veloparkieranlage', 'Anlagen']
        },
        'b7ce6cfb-8ce0-41dc-8e24-0a0dff2d9aba': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=1260',
            'tags': ['Verkehr', 'Verkehrsmessstellen', 'Verkehrszählstellen', 'Verkehrsmodell']
        },
        '9a4cc889-7907-454b-9d99-5b12c450e3ca': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=1177',
            'tags': []
        },
        '7693752a-6294-4087-ae5e-83e8a0176315': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=1258',
            'tags': ['Tiefbau', 'Strassen', 'Verkehr', 'Baustellen', 'Verkehrsbehinderung']
        },
        '8174aafe-3b3b-4e44-9a70-96bb6064018a': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=1298',
            'tags': []
        },
        '6a4b6960-2c21-420c-b36d-d7dd3c184643': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=1262',
            'tags': []
        },
        '2024fa34-6418-4de1-85f5-c619bda2c961': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=1261',
            'tags': ['Velo', 'Parkierung', 'öffentlich', 'Veloparkieranlage', 'Anlagen']
        },
        '0db7eda5-2a95-4bbf-9b10-d1942bd85ca7': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=1259',
            'tags': ['Verkehr', 'Verkehrsmessstellen', 'Verkehrszählstellen', 'Verkehrsmodell']
        },
        '4e27e579-88cf-4fb1-be90-869a9caeeac3': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=1257',
            'tags': ['Wald']
        },
        '3479db7a-30e7-4505-b452-977852a187c9': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=1320',
            'tags': ['Schutzwald', 'gravitative Naturgefahren', 'Schadenpotential', 'Schutzfunktion']
        },
        '5117c450-b502-42c1-823b-128bce2b1997': {
            'geolion_url': 'http://www.geolion.zh.ch/geodatenservice/show?nbid=1319',
            'tags': ['WNB']
        },
    }

    LICENSE = {
        'name': 'GIS-ZH Lizenz',
        'url': (
            'http://www.are.zh.ch/internet/baudirektion/are/de/'
            'geoinformationen/gis-zh_gis-zentrum/geodaten.html'
        ),
    }

    ORGANIZATION = {
        u'de': {
            'name': u'Kanton Zürich',
            'description': (
                u'Im Rahmen eines Pilotversuchs veröffentlicht der Kanton '
                u'Zürich ausgewählte Datensätze des Statistischen Amts '
                u'und des GIS-ZH (Geografisches Informationssystem '
                u'des Kantons Zürich).'
            ),
            'website': 'http://opendata.zh.ch',
        },
        u'fr': {
            'name': u'Canton de Zurich',
            'description': (
                u"Dans le cadre d'un projet pilote le canton de Zurich publie "
                u"des données sélectionnées de l'Office de la statistique "
                u"et du GIS-ZH (Système d'information géographique du "
                u"canton de Zurich)."
            ),
        },
        u'it': {
            'name': u'Cantone di Zurigo',
            'description': (
                u"Come parte di un test pilota, il cantone di Zurigo pubblica "
                u"dei dati selezionati dell'Ufficio statistico e del GIS-ZH "
                u"(Sistema Informativo Territoriale del cantone di Zurigo)"
            ),
        },
        u'en': {
            'name': u'Canton of Zurich',
            'description': (
                u"As part of a pilot project, the Canton of Zurich publishes "
                u"selected data of the Statistical Office and of the GIS-ZH "
                u"(Geographic Information System of the Canton of Zurich)."
            ),
        }
    }

    GROUPS = {
        u'de': [u'Raum und Umwelt'],
        u'fr': [u'Espace et environnement'],
        u'it': [u'Territorio e ambiente'],
        u'en': [u'Territory and environment']
    }

    def info(self):
        return {
            'name': 'zhgis',
            'title': 'zhgis',
            'description': 'Harvests the zhgis data',
            'form_config_interface': 'Text'
        }

    def gather_stage(self, harvest_job):
        log.debug('In ZhGisHarvester gather_stage')

        ids = []
        for dataset_id, dataset in self.DATASETS.iteritems():
            csw = ckan_csw.ZhGisCkanMetadata()
            metadata = csw.get_ckan_metadata_by_id(dataset_id).copy()
            log.debug(metadata)

            # Fix metadata information
            metadata['name'] = munge_title_to_name(metadata['name'])
            metadata['service_type'] = (
                metadata['service_type'].replace('OGC:', '')
            )

            # Enrich metadata with hardcoded values
            metadata['url'] = dataset['geolion_url']
            metadata['tags'].extend(dataset['tags'])

            metadata['translations'] = self._generate_term_translations()
            log.debug("Translations: %s" % metadata['translations'])

            metadata['resources'] = (
                self._generate_resource_dict_array(metadata)
            )
            log.debug(metadata['resources'])

            metadata['license_id'] = self.LICENSE['name']
            metadata['license_url'] = self.LICENSE['url']

            obj = HarvestObject(
                guid=metadata['id'],
                job=harvest_job,
                content=json.dumps(metadata)
            )
            obj.save()
            log.debug('adding ' + metadata['name'] + ' to the queue')
            ids.append(obj.id)

        return ids

    def fetch_stage(self, harvest_object):
        log.debug('In ZhGisHarvester fetch_stage')
        return True

    def import_stage(self, harvest_object):
        log.debug('In ZhGisHarvester import_stage')

        if not harvest_object:
            log.error('No harvest object received')
            return False

        try:
            package_dict = json.loads(harvest_object.content)

            package_dict['id'] = harvest_object.guid
            user = model.User.get(self.HARVEST_USER)
            context = {
                'model': model,
                'session': Session,
                'user': self.HARVEST_USER
                }

            # Find or create group the dataset should get assigned to
            package_dict['groups'] = self._find_or_create_groups(context)

            # Find or create the organization
            # the dataset should get assigned to
            package_dict['owner_org'] = self._find_or_create_organization(
                context
            )

            # Save license url in extras
            extras = []
            if 'license_url' in package_dict:
                extras.append(('license_url', package_dict['license_url']))
            package_dict['extras'] = extras

            package = model.Package.get(package_dict['id'])
            model.PackageRole(
                package=package,
                user=user,
                role=model.Role.ADMIN
            )

            log.debug(
                'Save or update package %s (%s)'
                % (package_dict['name'], package_dict['id'])
            )
            self._create_or_update_package(package_dict, harvest_object)

            log.debug('Save or update term translations')
            self._submit_term_translations(context, package_dict)
            Session.commit()

        except Exception, e:
            log.exception(e)
            raise
        return True

    def _find_or_create_groups(self, context):
        group_name = self.GROUPS['de'][0]
        data_dict = {
            'id': group_name,
            'name': munge_title_to_name(group_name),
            'title': group_name
            }
        try:
            group = get_action('group_show')(context, data_dict)
        except:
            group = get_action('group_create')(context, data_dict)
            log.info('created the group ' + group['id'])
        group_ids = []
        group_ids.append(group['id'])
        return group_ids

    def _find_or_create_organization(self, context):
        try:
            data_dict = {
                'permission': 'edit_group',
                'id': munge_title_to_name(self.ORGANIZATION[u'de']['name']),
                'name': munge_title_to_name(self.ORGANIZATION[u'de']['name']),
                'title': self.ORGANIZATION[u'de']['name'],
                'description': self.ORGANIZATION[u'de']['description'],
                'extras': [
                    {
                        'key': 'website',
                        'value': self.ORGANIZATION[u'de']['website']
                    }
                ]
            }
            organization = get_action('organization_show')(context, data_dict)
        except:
            organization = get_action('organization_create')(
                context,
                data_dict
            )
        return organization['id']

    def _generate_term_translations(self):
        '''
        Generate term translatations for groups, organizations and metadata
        '''
        try:
            translations = []

            for lang, org in self.ORGANIZATION.items():
                if lang != u'de':
                    for field in ['name', 'description']:
                        translations.append({
                            'lang_code': lang,
                            'term': self.ORGANIZATION[u'de'][field],
                            'term_translation': org[field]
                        })

            for lang, groups in self.GROUPS.iteritems():
                if lang != u'de':
                    for idx, group in enumerate(self.GROUPS[lang]):
                        translations.append({
                            'lang_code': lang,
                            'term': self.GROUPS[u'de'][idx],
                            'term_translation': group
                            })

            return translations

        except Exception, e:
            log.exception(e)
            raise

    def _submit_term_translations(self, context, package_dict):
        for translation in package_dict['translations']:
            log.debug(translation)
            action.update.term_translation_update(context, translation)

    def _generate_resource_dict_array(self, metadata):
        resources = [{
            'url': metadata['service_url'],
            'name': "%s (%s)" % (metadata['service_type'], metadata['title']),
            'format': metadata['service_type'],
            'resource_type': 'api'
        }]

        return resources
