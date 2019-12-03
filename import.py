import ConfigParser
import json
import logging
import pprint
import sys
import urllib, urllib2

from dataset import load_dataset, create_dummy_dataset, map_dataset
from resource import Resource, map_resource

logging.basicConfig(
        stream=sys.stderr,
        level=logging.INFO,
        format='%(message)s'
)

if len(sys.argv) < 3:
    logging.error('Error: Provide server and org names.')
    quit()

CONFIG_DEFAULTS = {
    'main': {
        'log_level': 'INFO',
    },
}

config = ConfigParser.ConfigParser(CONFIG_DEFAULTS)
config.read('server.ini')

log_level = config.get('main', 'log_level')
logging.getLogger().setLevel(log_level)

servers = config.sections()
server = sys.argv[1]
owner_org = sys.argv[2]
if server not in servers[1:]:
    logging.error('Error: Server ' + server + ' not found.')
    quit()

query_url = config.get('main', 'query')
pagecount = config.getint('main', 'pagecount')
url_server = config.get(server, 'url')
api_key = config.get(server, 'api')

create_url = url_server + '/api/action/package_create'
update_url = url_server + '/api/action/package_update'
resource_url = url_server + '/api/action/resource_create'

def main():
    dss_children = []
    dss_standalone = []
    dss_parents = []

    ids_parents = set()
    ids_children = set()
    ids_pair_parents = {}

    req = urllib2.Request(query_url, None, {'Cookie':'auth_tkt=1'})
    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        logging.error('Error: %s' % e )
        quit()
    except urllib2.URLError, e:
        logging.error('Error: %s' % e )
        quit()
    else:
        response_dict = json.loads(response.read())
        assert response_dict['conformsTo'] \
            == 'https://project-open-data.cio.gov/v1.1/schema'
        dss = response_dict['dataset']

    for ds in dss:
        if ds.get('isPartOf'):
            dss_children.append(ds)
            ids_parents.add(ds['isPartOf'])
            ids_children.add(ds['identifier'])

    for ds in dss:
        id = ds['identifier']
        if id in ids_parents and id in ids_children:
            logging.info('dataset be both parent and child: %s' % id)
        elif id in ids_parents and id not in ids_children:
            dss_parents.append(ds)
        elif id not in ids_parents and id not in ids_children:
            dss_standalone.append(ds)

    logging.info('%i standalone datasets to be Added.' % len(dss_standalone))
    logging.info('%i parent datasets to be Added.' % len(dss_parents))
    logging.info('%i children dataset to be Added.' % len(dss_children))

    total = len(dss_standalone)
    i = 0
    for ds in dss_standalone:
        i += 1
        dataset = import_ds(ds)
        logging.info('%i/%i Added dataset: %s' % (i, total, dataset['name']))

    total = len(dss_parents)
    i = 0
    for ds in dss_parents:
        i += 1
        dataset = import_ds(ds, 'parent')
        ids_pair_parents[ds['identifier']] = dataset['id']
        logging.info('%i/%i Added parent: %s' % (i, total, dataset['name']))

    total = len(dss_children)
    i = 0
    skipped = 0
    for ds in dss_children:
        i += 1
        parent_id = ds['isPartOf']
        parent_identifier = ids_pair_parents.get(parent_id)
        if not parent_identifier:
            logging.info('%i/%i Skipped child: %s' % (i, total, ds['identifier']))
            skipped += 1
            continue 
        dataset = import_ds(ds, 'child', parent_identifier)
        logging.info('%i/%i Added child: %s' % (i, total, dataset['name']))
    if skipped:
        logging.info('%i of %i chilren datasets skipped.' % (skipped, total))

def import_ds(ds, type=None, parent_id=None):
    if type == 'parent':
        ds['is_parent'] = 'true'
    else:
        ds.pop('is_parent', None)

    if type == 'child':
        ds['parent_dataset'] = parent_id
    else:
        ds.pop('parent_dataset', None)

    dataset_dummy = create_dummy_dataset()
    dataset_dummy['title'] = ds['title']
    dataset_dummy['owner_org'] = owner_org

    # first run to get name created.
    ds_created = dataset_dummy.create(create_url, api_key)

    # then update the dataset with all info
    dataset_full = load_dataset(ds_created)
    logging.debug(ds)
    map_dataset(dataset_full, ds)
    dataset_full._update(update_url, api_key)

    # add resource
    resources = ds.get('distribution', [])
    for res in resources:
        resource = Resource()
        map_resource(resource, res, dataset_full['id'])
        # skip and report empty resource
        if resource['url']:
            res_created = resource.create(resource_url, api_key)
        else:
            logging.info('   Empty resource skipped for: %s' % ds['title'])

    return dataset_full

if __name__ == '__main__':
    main()
