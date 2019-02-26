import urllib, urllib2
import json
import pprint

class Resource(dict):
    def __init__(self,*arg,**kw):
        super(Resource, self).__init__(*arg, **kw)

    def create(self, url, api_key=''):
        json_resource = json.dumps(self)
        json_resource = urllib.quote(json_resource)

        req = urllib2.Request(url, json_resource, {
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
    
    


