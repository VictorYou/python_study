import requests
import random
import logging

log = logging.getLogger(__name__)

STATE_REST_API_URL = "http://localhost:8000"

def get_lab_id_by_name(lab_name):
    return get_resources('labs', where='lab_name=={}'.format(lab_name))['_items'][0]

def test_setup(labs=None, snapshots_status="available", lab_status="ready"):
    """Create labs, states and reservations.
    :param labs: [ (<lab_name:string>, <lab_type:string>, <state.build.id:string>, <reservation:boolean>[, <additional_options:dict>]), ]
    """
    if not labs:
        labs = [("testlab-1", "sprint", "netact-1", False),
                ("testlab-2", "sprint", "netact-2", False),
                ("testlab-3", "cloud", "netact-1", False)]
    labs_url = "{}/{}".format(STATE_REST_API_URL, 'labs')
    states_url = "{}/{}".format(STATE_REST_API_URL, 'states')
    reservations_url = "{}/{}".format(STATE_REST_API_URL, 'reservations')
    for lab_entry in labs:
        lab, _type, build, reserved = lab_entry[:4]
        more_settings = dict(
            # if there should be any default settings for lab, put them HERE
        )
        more_settings.update(lab_entry[4] if list(lab_entry[4:5]) != [] else {})
        lab_data = {'lab_name': lab,
                    'lab_type': _type,
                    'status': lab_status}
        response = requests.post(labs_url, json=lab_data)
        response.raise_for_status()
        lab_id = str(response.json()['_id'])
        state_data = {"lab": lab_id,
                      "build": {"id": build},
                      "snapshot_status": snapshots_status,
                      "snapshot_id": str(random.randrange(0, 999999))}
        response = requests.post(states_url, json=state_data)
        response.raise_for_status()
        if reserved:
            res_data = {"lab": lab_id, "username": "testuser"}
            response = requests.post(reservations_url, json=res_data)
            response.raise_for_status()


def post_labrequest(username, state_search_query, message=None, lab_search_query=None, duration=300, tag=None):
    if not message:
        message = "message"
    data = {'username': username,
            'state_search_query': state_search_query,
            'message': message,
            'lab_reservation_time': str(duration),}
    if lab_search_query:
        data.update({'lab_search_query': lab_search_query})
    if tag:
        data.update({'tag': tag})
    log.debug(data)
    return post_item('labrequests', data).json()


def get_item(resource, _id, **params):
    get_url = STATE_REST_API_URL + "/{0}/{1}".format(resource, _id)
    response = requests.get(get_url, params=params)
    log.debug("response: {}".format(response.text))
    response.raise_for_status()
    return response.json()


def get_resources(resource, **params):
    get_url = STATE_REST_API_URL + "/{0}/".format(resource)
    response = requests.get(get_url, params=params)
    log.debug("response: {}".format(response.text))
    response.raise_for_status()
    return response.json()


def delete_item(resource, item_id, force=False):
    if force:
        force_str = "?force"
    else:
        force_str = ""
    url = STATE_REST_API_URL + "/{0}/{1}{2}".format(resource, item_id, force_str)
    item = get_item(resource, item_id)
    headers = {'If-Match': item['_etag']}
    response = requests.delete(url, headers=headers)
    log.debug("response: {}".format(response.text))
    response.raise_for_status()
    return response


def patch_item(resource, item_id, data):
    url = STATE_REST_API_URL + "/{0}/{1}".format(resource, item_id)
    item = get_item(resource, item_id)
    headers = {'If-Match': item['_etag']}
    response = requests.patch(url, headers=headers, json=data)
    log.debug("response: {}".format(response.text))
    response.raise_for_status()
    return response


def post_item(resource, data):
    url = STATE_REST_API_URL + "/{0}".format(resource)
    response = requests.post(url, json=data)
    log.debug("response: {}".format(response.text))
    response.raise_for_status()
    return response
