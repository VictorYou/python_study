'''LSS client REST methods
'''
import logging
import requests
import time
import json
import sys
import os
import random
import re
from .globals import *
from .utils import load_json_content

log = logging.getLogger(__name__)

def post_resource(resource, data, base_url, raise_error=True, **params):
    ''' add item to LSS server resource

    :param resource LSS resource such as 'labs', 'reservations' etc.
    :param data data for item as dict, will be sent in JSON format to LSS server
    :param base_url url of LSS server e.g. 'http://web:8000'
    :param raise_error  whether to raise exception in case of request failure
    '''
    url = base_url + "/{0}".format(resource)
    log.info("POST '{}' url: '{}' request: '{}'".format(resource, url, json.dumps(data)))
    response = requests.post(url, json=data, params=params)
    log.info("POST '{}' response: '{}' \n".format(resource, response.text))
    if raise_error:
        response.raise_for_status()
    return response.json()

def get_item(resource, _id, base_url, **params):
    ''' get item from LSS server resource

    :param resource LSS resource such as 'labs', 'reservations' etc.
    :param _id  id of resource item
    :param base_url url of LSS server e.g. 'http://web:8000'
    '''
    get_url = base_url + "/{0}/{1}".format(resource, _id)
    log.info("GET '{}' request: '{}".format(resource, str(get_url)))
    response = requests.get(get_url, params=params)
    log.info("GET '{0}' response: {1} \n".format(resource, response.text))
    response.raise_for_status()
    return response.json()

def patch_item(resource, _id, data, etag, base_url, raise_error=True, **params):
    ''' patch item in LSS server resource

    :param resource LSS resource such as 'labs', 'reservations' etc.
    :param _id  id of resource item to be patched
    :param data optional data as dict, will be sent in JSON format to LSS server
    :param etag etag version string for identifying resource on LSS server
    :param base_url url of LSS server e.g. 'http://web:8000'
    :param raise_error  whether to raise exception in case of request failure
    '''
    url = base_url + "/{0}/{1}".format(resource, _id)
    headers = {'If-Match': etag}
    log.info("PATCH '{}/{}' request: '{}".format(resource, _id, data))
    response = requests.patch(url, json=data, headers=headers, params=params)
    log.info("PATCH {0} response: {1} \n".format(resource, response.text))
    if raise_error:
        response.raise_for_status()
    return response.json()

def delete_item(resource, _id, data, etag, base_url, raise_error=True, force_flag=False, **params):
    ''' delete item from LSS server resource

    :param resource LSS resource such as 'labs', 'reservations' etc.
    :param _id  id of resource item to be deleted
    :param data optional data as dict, will be sent in JSON format to LSS server
    :param etag etag version string for identifying resource on LSS server
    :param base_url url of LSS server e.g. 'http://web:8000'
    :param raise_error  whether to raise exception in case of request failure
    :param force_flag   force delete action that will be appended to request url
    '''
    force_str = ""
    if force_flag:
        force_str = "?force"
    url = base_url + "/{0}/{1}{2}".format(resource, _id, force_str)
    headers = {'If-Match': etag}
    log.info("DELETE '{}/{}' request: '{}', url: '{}' _id: '{}', _etag: '{}'".format(resource, _id, data, url, _id, etag))
    response = requests.delete(url, json=data, headers=headers, params=params)
    log.info("DELETE {} response status_code: '{}' rsp: '{}'\n".format(resource, response.status_code, response))
    if raise_error:
        response.raise_for_status()
    return response

def get_labs(query, lab_pool_url, labs_data=None):
    ''' retrieve data about labs from LSS server '''
    embedded_str = '&embedded={"states":1,"reservation":1,"previously_reverted_state":1}'
    query += embedded_str
    log.info("get_labs(): " + query)

    req = requests.get(query)
    req.raise_for_status()
    rspjson = load_json_content(req.content)
    rsplinks = rspjson['_links']
    if not labs_data:
        labs_data = []
    labs_data.append(rspjson)

    if 'next' in rsplinks:
        next_href = rsplinks['next']['href']
        next_query = lab_pool_url + "/" + next_href
        log.info("Next page address: ")
        log.info(next_query)
        get_labs(next_query, lab_pool_url, labs_data)

    log.debug('Dumping lab data:\n%s\n' % (json.dumps(labs_data, indent=4, sort_keys=True)))
    return labs_data

