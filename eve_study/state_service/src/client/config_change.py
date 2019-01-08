#!/usr/bin/python

'''
Client module for changing configuration of LSS server via LSS REST API

    Curl examples:
        GET
        curl -i http://ss:8000/config/LAB_WHITE_LIST

        POST
        curl -X POST http://ss:8000/config -H  "Content-Type: application/json" -d '{"name": "LAB_WHITE_LIST",  "value": "DummyLab123 vOSP0020"}'
         
        PATCH: requires retrieval of etag
        curl -X PATCH "http://ss:8000/config/LAB_WHITE_LIST" -H "If-Match: c7eb02897d63cd7e0a5363a14ad62a12b56989bd" -H  "Content-Type: application/json" -d '{  "value": "black white"}'

        DELETE: requires retrieval of etag
        curl -X DELETE "http://ss:8000/config/LAB_WHITE_LIST" -H "If-Match: c7eb02897d63cd7e0a5363a14ad62a12b56989bd"
'''

from requests import exceptions
import logging
import rest_client as rest

log = logging.getLogger(__name__)

def set_server_config_entry(name, value = None, service_url=None, **kwargs):
    ''' set the value of 'name' on LSS server to 'value' ''' 
    log.debug('set_server_config_entry(name = %s, value = %s, kwargs = %s)' % (name, value, kwargs))
    try:
        item = rest.get_item('config', name, service_url)
        etag, old_value = item.get('_etag'), item.get('value')
        log.info('SET name: %s [%s] to "%s" (old value: "%s")' % (name, etag, value, old_value))
        rest.patch_item('config', name, {'value': value}, etag, service_url)
    except exceptions.HTTPError as e:
        log.info('item %s not retrieved: %s' % (name, e))
        rest.post_resource('config', 
                {'name': name, 'value': value},
                service_url)

def get_server_config_entry(name = None, service_url=None, **kwargs):
    ''' retrieve the value of 'name' on LSS server and returns it.
        If name is None then whole configuration is retrieved.
        'raw' switch decides whether to return the value (False) or the while item on server
    ''' 
    log.debug('get_server_config_entry(name = %s, kwargs = %s)' % (name, kwargs))
    try:
        item = rest.get_item('config', name, service_url)
        log.debug('get_item(url=%s/config, name=%s): %s' % (service_url, name, item))
    except exceptions.HTTPError as e:
        return None
    return item.get('value')

def remove_server_config_entry(name, service_url=None, **kwargs):
    ''' remove the value of 'name' on LSS server ''' 
    log.debug('remove_server_config_entry(name = %s, kwargs = %s)' % (name, kwargs))
    try:
        item = rest.get_item('config', name, service_url)
        etag = item.get('_etag')
        log.info('REMOVE name: %s [%s]' % (name, etag))
        rest.delete_item('config', name, None, etag, service_url)
        return True
    except exceptions.HTTPError as e:
        log.error('No such config item: %s' % (name))
        return False
