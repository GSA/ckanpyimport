import configparser
import json
import logging
import sys
import urllib.error
import urllib.parse
import urllib.request

from dataset import create_dummy_dataset, load_dataset, map_dataset
from resource import Resource, map_resource # pylint: disable=wrong-import-order

logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format='%(message)s'
)

if len(sys.argv) < 3:
    logging.error('Error: Provide server and org names.')
    sys.exit(1)

CONFIG_DEFAULTS = {
    'main': {
        'log_level': 'INFO',
    },
}

config = configparser.ConfigParser(CONFIG_DEFAULTS)
config.read('server.ini')

log_level = config.get('main', 'log_level')
logging.getLogger().setLevel(log_level)

servers = config.sections()
server = sys.argv[1]
owner_org = sys.argv[2]
if server not in servers[1:]:
    logging.error('Error: Server %s not found.', server)
    sys.exit(1)


query_url = config.get('main', 'query')
pagecount = config.getint('main', 'pagecount')
url_server = config.get(server, 'url')
api_key = config.get(server, 'api')

create_url = url_server + '/api/action/package_create'
update_url = url_server + '/api/action/package_update'
resource_url = url_server + '/api/action/resource_create'

def main(): # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    dss_children = []
    dss_standalone = []
    dss_parents = []

    ids_parents = set()
    ids_children = set()
    ids_pair_parents = {}

    req = urllib.request.Request(query_url, None, {'Cookie':'auth_tkt=1'})
    try:
        response = urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        logging.error('Error: %s', e)
        sys.exit(1)
    except urllib.error.URLError as e:
        logging.error('Error: %s', e)
        sys.exit(1)
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
        _id = ds['identifier']
        if _id in ids_parents and _id in ids_children:
            logging.info('dataset be both parent and child: %s', _id)
        elif _id in ids_parents and _id not in ids_children:
            dss_parents.append(ds)
        elif _id not in ids_parents and _id not in ids_children:
            dss_standalone.append(ds)

    logging.info('%i standalone datasets to be Added.', len(dss_standalone))
    logging.info('%i parent datasets to be Added.', len(dss_parents))
    logging.info('%i children dataset to be Added.', len(dss_children))

    total = len(dss_standalone)
    i = 0
    for ds in dss_standalone:
        i += 1
        dataset = import_ds(ds)
        logging.info('%i/%i Added dataset: %s', i, total, dataset['name'])

    total = len(dss_parents)
    i = 0
    for ds in dss_parents:
        i += 1
        dataset = import_ds(ds, 'parent')
        ids_pair_parents[ds['identifier']] = dataset['id']
        logging.info('%i/%i Added parent: %s', i, total, dataset['name'])

    total = len(dss_children)
    i = 0
    skipped = 0
    for ds in dss_children:
        i += 1
        parent_id = ds['isPartOf']
        parent_identifier = ids_pair_parents.get(parent_id)
        if not parent_identifier:
            logging.info('%i/%i Skipped child: %s', i, total, ds['identifier'])
            skipped += 1
            continue
        dataset = import_ds(ds, 'child', parent_identifier)
        logging.info('%i/%i Added child: %s', i, total, dataset['name'])
    if skipped:
        logging.info('%i of %i chilren datasets skipped.', skipped, total)

def import_ds(ds, dataset_type=None, parent_id=None):
    if dataset_type == 'parent':
        ds['is_parent'] = 'true'
    else:
        ds.pop('is_parent', None)

    if dataset_type == 'child':
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
    dataset_full._update(update_url, api_key) # pylint: disable=protected-access

    # add resource
    resources = ds.get('distribution', None)
    if not resources:
        return dataset_full

    for res in resources:
        resource = Resource()
        map_resource(resource, res, dataset_full['id'])
        # skip and report empty resource
        if resource['url']:
            resource.create(resource_url, api_key)
        else:
            logging.info('   Empty resource skipped for: %s', ds['title'])

    return dataset_full

if __name__ == '__main__':
    main()
