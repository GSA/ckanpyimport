import urllib, urllib2
import json
import logging
import pprint

from helper import munge_title_to_name, re_munge_name, munge_tag, LICENSES, \
    get_readable_frequency


log = logging.getLogger(__name__)


class Dataset(dict):
    def __init__(self,*arg,**kw):
        super(Dataset, self).__init__(*arg, **kw)

    def create(self, url, api_key='', rename=False):
        if rename:
            self['name'] = re_munge_name(self['name'])
        else:
            self['name'] = munge_title_to_name(self['title'])

        json_dataset = json.dumps(self)
        json_dataset = urllib.quote(json_dataset)

        req = urllib2.Request(url, json_dataset, {
            'X-CKAN-API-Key':api_key,
            'Cookie':'auth_tkt=1'
        })
        try:
            response = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            error_dict = json.loads(e.read())
            if 'name' in error_dict['error']:
                error_message = error_dict['error']['name']
                if error_message[0] == 'That URL is already in use.':
                    dataset_created = self.create(url, api_key, True)
                    return dataset_created
            else:
                log.error(error_dict)
                log.exception('Failed to create dataset')
                quit()
        except urllib2.URLError, e:
            log.exception('Failed to create dataset')
            quit()
        else:
            response_dict = json.loads(response.read())
            assert response_dict['success'] is True
            dataset_created = response_dict['result']
        return dataset_created

    def _update(self, url, api_key=''):
        json_dataset = json.dumps(self)
        json_dataset = urllib.quote(json_dataset)

        req = urllib2.Request(url, json_dataset, {
            'X-CKAN-API-Key':api_key,
            'Cookie':'auth_tkt=1'
        })
        try:
            response = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            print('Error: %s' % e )
            quit()
        except urllib2.URLError, e:
            print('Error: %s' % e )
            quit()
        else:
            response_dict = json.loads(response.read())
            assert response_dict['success'] is True
            dataset_updated = response_dict['result']
        return dataset_updated



def create_dummy_dataset():
    dataset = Dataset()

    dataset['name'] = 'test'
    dataset['notes'] = 'test'
    dataset['tag_string'] = ['test']

    return dataset

def load_dataset(ds):
    dataset = Dataset()
    for key, value in ds.iteritems():
        if key == 'extras':
            continue
        dataset[key] = value
    return dataset

def map_dataset(dataset, ds):

    dataset['private'] = True
    dataset['extras'] = []
    dataset['tags'] = []
    dataset['license_id'] = LICENSES['License Not Specified']

    for key, value in ds.iteritems():
        log.debug('key=%s value=%s', key, value)

        if key in ['title']:
            dataset[key] = value

        if key in [
            'modified',
            'spatial',
            'temporal',
            'is_parent',
            'parent_dataset'
            ]:
            dataset['extras'].append({
                'key': key,
                'value': value
            })

        if key == 'description':
            dataset['notes'] = value

        if key == 'keyword':
            for term in value:
                dataset['tags'].append({
                'name': munge_tag(term)
            })

        if key == 'accessLevel':
            dataset['extras'].append({
                'key': 'public_access_level',
                'value': value
            })

        if key == 'identifier':
            dataset['extras'].append({
                'key': 'unique_id',
                'value': value
            })

        if key == 'publisher':
            dataset['extras'].append({
                'key': 'publisher',
                'value': value['name']
            })
            publisher_1 = value.get('subOrganizationOf', {})
            if publisher_1:
                dataset['extras'].append({
                    'key': 'publisher_1',
                    'value': publisher_1['name']
                })
                publisher_2 = publisher_1.get('subOrganizationOf', {})
                if publisher_2:
                    dataset['extras'].append({
                        'key': 'publisher_2',
                        'value': publisher_2['name']
                    })
                    publisher_3 = publisher_2.get('subOrganizationOf', {})
                    if publisher_3:
                        dataset['extras'].append({
                            'key': 'publisher_3',
                            'value': publisher_3['name']
                        })
                        publisher_4 = publisher_3.get('subOrganizationOf', {})
                        if publisher_4:
                            dataset['extras'].append({
                                'key': 'publisher_4',
                                'value': publisher_4['name']
                            })

        if key == 'bureauCode':
            dataset['extras'].append({
                'key': 'bureau_code',
                'value': ", ".join(value)
            })

        if key == 'programCode':
            dataset['extras'].append({
                'key': 'program_code',
                'value': ", ".join(value)
            })

        if key == 'license':
            if LICENSES.get(value):
                dataset['extras'].append({
                    'key': 'license',
                    'value': value
                })
                dataset['license_id'] = LICENSES.get(value)
            else:
                dataset['extras'].append({
                    'key': 'license_new',
                    'value': value
                })

        if key == 'contactPoint':
            dataset['extras'].append({
                'key': 'contact_name',
                'value': value['fn']
            })
            dataset['extras'].append({
                'key': 'contact_email',
                'value': value['hasEmail'].replace('mailto:', '')
            })

        if key == 'dataQuality':
            dataset['extras'].append({
                'key': 'data_quality',
                'value': False if value in [
                    'off', 'false', 'no', '0'] else True
            })

        if key == 'accrualPeriodicity':
            dataset['extras'].append({
                'key': 'accrual_periodicity',
                'value': get_readable_frequency(value)
            })

        if key == 'issued':
            dataset['extras'].append({
                'key': 'release_date',
                'value': value
            })

        if key == 'primaryITInvestmentUII':
            dataset['extras'].append({
                'key': 'primary_it_investment_uii',
                'value': value
            })

        if key == 'landingPage':
            dataset['extras'].append({
                'key': 'homepage_url',
                'value': value
            })

        if key == 'theme':
            dataset['extras'].append({
                'key': 'category',
                'value': ", ".join(value)
            })

        if key == 'references':
            dataset['extras'].append({
                'key': 'related_documents',
                'value': ", ".join(value)
            })

        if key == 'language':
            dataset['extras'].append({
                'key': 'language',
                'value': ", ".join(value)
            })

        if key == 'systemOfRecords':
            dataset['extras'].append({
                'key': 'system_of_records',
                'value': value
            })

        if key == 'describedBy':
            dataset['extras'].append({
                'key': 'data_dictionary',
                'value': value
            })

        if key == 'describedByType':
            dataset['extras'].append({
                'key': 'data_dictionary_type',
                'value': value
            })

        if key == 'rights':
            dataset['extras'].append({
                'key': 'access_level_comment',
                'value': value
            })
