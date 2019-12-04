import json
import logging
import sys
import urllib.error
import urllib.parse
import urllib.request


log = logging.getLogger(__name__)


class Resource(dict):
    def create(self, url, api_key=''):
        json_resource = json.dumps(self)

        # This looks like a bug in CKAN. When application/json is specified we
        # get a 400 https://github.com/GSA/datagov-deploy/issues/1177
        req = urllib.request.Request(url, json_resource.encode('utf8'), {
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
            'X-CKAN-API-Key':api_key,
            'Cookie':'auth_tkt=1'
        })
        try:
            response = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            log.exception(e)
            sys.exit(1)
        except urllib.error.URLError as e:
            log.exception(e)
            sys.exit(1)
        else:
            response_dict = json.loads(response.read().decode('utf8'))
            assert response_dict['success'] is True
            resource_created = response_dict['result']
        return resource_created

def map_resource(resource, res, dataset_id):
    resource['package_id'] = dataset_id
    if res.get('downloadURL'):
        resource['url'] = res.get('downloadURL')
        resource['resource_type'] = 'file'
    elif res.get('accessURL'):
        resource['url'] = res.get('accessURL')
        if res.get('format') == 'API':
            resource['resource_type'] = 'api'
        else:
            resource['resource_type'] = 'accessurl'
    else:
        resource['url'] = None

    resource['format'] = res.get('mediaType')
    resource['name'] = res.get('title')
    resource['formatReadable'] = res.get('format')
    resource['description'] = res.get('description')

    if res.get('describedBy'):
        resource['describedBy'] = res.get('describedBy')

    if res.get('describedByType'):
        resource['describedByType'] = res.get('describedByType')
