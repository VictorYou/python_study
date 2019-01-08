'''Definition of Celery task for handling snapshot in DCSA API
'''

from tasks import app
from celery import exceptions
from celery.utils.log import get_task_logger
import requests
import dcstorage
import dcapi
import os
import random
import time

STATE_REST_API_URL = "http://web:8000"
#STORAGE_API_URL = "http://tredcsa.netact.nsn-rdnet.net/rest/api/v2"
STORAGE_API_URL = "http://10.91.228.255/rest/api/v2"

# STATE_SERVICE_RANDOM_FAILING env variable will cause random failures with take snapshot and snapshot revert
STATE_SERVICE_RANDOM_FAILING = True if os.getenv('STATE_SERVICE_RANDOM_FAILING', "") == "yes" else False

if os.getenv('PYDOC_RUN') is None:
    log = get_task_logger(__name__)
    proxies = {
      "no_proxy": "web,127.0.0.1,localhost,localhost.localdomain"
    }

    @app.task(bind=True)
    def take_snapshot(self, lab_id, state_id, state_etag, testing_enabled=False, lab_whitelisted=False):
        log.info("**** Request {0}: take_snapshot starts ****".format(self.request.id))
        lab = _get_item('labs', lab_id)
        lab_name = lab['lab_name']
        status = "state_operation_failed"
        try:
            _change_lab_status(lab_id, "preserving_state")
            expected_state = "queued"
            _raise_if_state_not_valid(expected_state, lab, state_id, testing_enabled, lab_whitelisted)
            event_id, snapshot_id, state_etag = _take_snapshot(lab_name, state_etag, state_id)
            status = "ready"
        except Exception as e:
            log.exception(e)
            raise
        finally:
            _change_lab_status(lab_id, status)
        log.info("**** Request {0}: take_snapshot ends ****".format(self.request.id))
        return {"snapshot_id": snapshot_id, "event_id": event_id}

    @app.task(bind=True)
    def revert_to_snapshot(self, lab_id, lab_info, state_id, testing_enabled=False, lab_whitelisted=False, dont_do_revert=False):
        log.info("**** Request {0}: revert_to_snapshot starts ****".format(self.request.id))
        lab_name = lab_info['lab_name']
        status = "state_operation_failed"
        try:
            lab_etag = _change_lab_status(lab_id, "reverting_state")
            expected_state = "available"
            _raise_if_state_not_valid(expected_state, lab_info, state_id, testing_enabled, lab_whitelisted)
            snapshot_id = _get_item('states', state_id)["snapshot_id"]
            event_id = _execute_snapshot_revert(lab_name, lab_id, lab_etag, state_id, snapshot_id, testing_enabled, dont_do_revert)
            status = "ready"
        except Exception as e:
            log.exception(e)
            raise
        finally:
            _change_lab_status(lab_id, status)
        log.info("**** Request {0}: revert_to_snapshot ends ****".format(self.request.id))
        return {"event_id": event_id}

def _execute_snapshot_revert(lab_name, lab_id, lab_etag, state_id, snapshot_id, testing_enabled, dont_do_revert):
    from paramiko.ssh_exception import SSHException
    try:
        step = 'powering off lab'
        _ensure_poweroff(lab_name, testing_enabled)
        step = 'reverting snapshot'
        event_id = _revert_storage_snapshot(lab_name, snapshot_id, testing_enabled or dont_do_revert)
        step = 'powering on lab'
        _ensure_poweron(lab_name, testing_enabled)

        _patch_lab(lab_id, {"previously_reverted_state": state_id}, lab_etag)
    except SSHException as sshex:
        log.error('revert_to_snapshot(): Error during %s: %s', step, sshex)
        raise
    return event_id

def _take_snapshot(lab_name, state_etag, state_id):
    state_etag = _change_state(state_id, state_etag, "creating")
    try:
        snapshot_id, event_id = _take_storage_snapshot(lab_name)
    except:
        _change_state(state_id, state_etag, "failed")
        raise
    state_etag = _change_state(state_id, state_etag, "available", snapshot_id=snapshot_id)
    return event_id, snapshot_id, state_etag

def _raise_if_state_not_valid(expected_state, lab_info, state_id, testing_enabled, lab_whitelisted):
    lab_name = lab_info['lab_name']
    log.info("Snapshot validation for lab=%s and state=%s [expected %s]" % (lab_name, state_id, expected_state))
    log.info("Lab is white listed? %s" % (lab_whitelisted))
    log.info("STATE_SERVICE_TESTING_ENABLED: {}".format(testing_enabled))
    if not (lab_whitelisted or testing_enabled):
        raise exceptions.TaskError("Lab cannot be used for reverting snapshots")
    if not _state_is_expected(state_id, expected_state):
        raise exceptions.InvalidTaskError("State %s is not expected %s" % (state_id, expected_state))
    if not lab_info.get('reservation'):
        raise exceptions.InvalidTaskError("Lab %s is not reserved" % (lab_name))
    log.info("Snapshot validation OK")

def _change_state(state_id, etag, trg, snapshot_id=None):
    src = _get_snapshot_status(state_id)
    if src == "queued" and trg == "creating":
        return _patch_snapshot_status(state_id, {"snapshot_status" : trg}, etag)
    elif src == "creating" and trg == "available":
        if snapshot_id is not None:
            return _patch_snapshot_status(state_id, {"snapshot_status" : trg, "snapshot_id" : snapshot_id}, etag)
        else:
            log.error("Snapshot id missing!")
            raise exceptions.TaskError
    elif src == "creating" and trg == "failed":
        return _patch_snapshot_status(state_id, {"snapshot_status" : trg}, etag)
    else:
        log.error("Transition to state {0} not supported when current state is {1}".format(trg, src))
        raise exceptions.TaskError

def _change_lab_status(lab_id, trg):
    src, etag = _get_lab_status(lab_id)
    if (src == "queued_for_revert" or src == "state_operation_failed") and trg == "reverting_state":
        return _patch_lab(lab_id, {"status": trg}, etag)
    elif (src == "initializing" or src == "queued_for_initialization" or src == "ready" or src == "state_operation_failed") and trg == "preserving_state":
        return _patch_lab(lab_id, {"status": trg}, etag)
    elif (src == "reverting_state" or src == "preserving_state") and trg == "ready":
        return _patch_lab(lab_id, {"status": trg}, etag)
    elif (src == "reverting_state" or src == "preserving_state") and trg == "state_operation_failed":
        return _patch_lab(lab_id, {"status": trg}, etag)
    elif src == "state_operation_failed" and trg == "state_operation_failed":
        return etag
    else:
        log.error("Transition to state {0} not supported when current state is {1}".format(trg, src))
        raise exceptions.TaskError

def _patch_snapshot_status(state_id, patch_json, etag):
    patch_url = STATE_REST_API_URL + "/states/{0}".format(state_id)
    headers = {"If-Match": etag}
    s = requests.Session()
    a = requests.adapters.HTTPAdapter(max_retries=3)
    s.mount(STATE_REST_API_URL, a)
    resp = s.patch(patch_url, data=patch_json, headers=headers, proxies=proxies)
    resp.raise_for_status()
    log.info("PATCH response: {0}".format(resp.text))
    return resp.json()["_etag"]

def _patch_lab(lab_id, patch_json, etag):
    patch_url = STATE_REST_API_URL + "/labs/{0}".format(lab_id)
    headers = {"If-Match": etag}
    s = requests.Session()
    a = requests.adapters.HTTPAdapter(max_retries=3)
    s.mount(STATE_REST_API_URL, a)
    resp = s.patch(patch_url, data=patch_json, headers=headers, proxies=proxies)
    resp.raise_for_status()
    log.info("PATCH response: {0}".format(resp.text))
    return resp.json()["_etag"]

def _get_lab_status(lab_id):
    lab_data = _get_item('labs', lab_id)
    return lab_data["status"], lab_data["_etag"]

def _get_snapshot_status(state_id):
    state_data = _get_item('states', state_id)
    return state_data["snapshot_status"]

def _state_is_expected(state_id, expected_state):
    snapshot_status = _get_item('states', state_id)["snapshot_status"]
    log.info("Expected status = {0}".format(expected_state))
    log.info(("Actual status = {0}".format(snapshot_status)))
    return True if snapshot_status == expected_state else False

def _state_is_queued(state_id):
    snapshot_status = _get_item('states', state_id)["snapshot_status"]
    log.info(("snapshot_status = {0}".format(snapshot_status)))
    return True if snapshot_status == "queued" else False

def _state_is_available(state_id):
    snapshot_status = _get_item('states', state_id)["snapshot_status"]
    log.info(("snapshot_status = {0}".format(snapshot_status)))
    return True if snapshot_status == "available" else False

def _get_item(resource, _id):
    url = STATE_REST_API_URL +"/{0}/{1}".format(resource, _id)
    r = requests.get(url, proxies=proxies)
    log.info("GET : {}".format(r.text))
    r.raise_for_status()
    return r.json()

def _get_dcstorage_client(lab_name):
    auth_data = dcapi.get_lab_auth(lab_name)
    username = auth_data['user']
    password = auth_data['password']
    client = dcstorage.DCSAClient(api_url=STORAGE_API_URL, username=username, password=password)
    return client

def _revert_storage_snapshot(lab_name, snapshot_name, testing_enabled):
    if testing_enabled:
        return _placebo_snapshot_action(lab_name, 'snapshot revert', 'random revert_id...')
    log.debug('_revert_storage_snapshot(lab_name=%s, snapshot_name=%s, testing? %s', lab_name, snapshot_name, testing_enabled)
    client = _get_dcstorage_client(lab_name)
    with dcstorage.WaitEvents(client, timeout=28800):
        online = True
        if "DummySprint" in lab_name or "SprintLab" in lab_name:
            online = False
        response_data = client.revert_to_snapshot(snapshot_name, online=online)
    return response_data.get('eventID')

def _remove_storage_snapshot(lab_name, snapshot_name, testing_enabled):
    if testing_enabled:
        return _placebo_snapshot_action(lab_name, 'remove snapshot', 'random snapshot name')
    client = _get_dcstorage_client(lab_name)
    with dcstorage.WaitEvents(client):
        response_data = client.delete_snapshot(snapshot_name)
    return response_data.get('eventID')

def _take_storage_snapshot(lab_name, testing_enabled):
    if testing_enabled:
        return _placebo_snapshot_action(lab_name, 'take snapshot', 'random snapshot name')
    client = _get_dcstorage_client(lab_name)
    with dcstorage.WaitEvents(client):
        response_data = client.take_snapshot(lab_name)
    snapshot_status = client.get_snapshot_status(lab_name)
    snapshot_name = snapshot_status.get('snapshots')[-1]['name']
    return snapshot_name, response_data.get('eventID')

def _placebo_snapshot_action(lab_name, action, message):
    log.info("STATE_SERVICE_TESTING_ENABLED, returning %s ..." % (message))
    time.sleep(20)
    if STATE_SERVICE_RANDOM_FAILING and random.choice([True, False]):
        raise SystemError("STATE_SERVICE_RANDOM_FAILING parameter caused random error with %s!" % (action))
    return random.randrange(0, 999999)

def _ensure_poweroff(lab_name, testing_enabled):
    if testing_enabled:
        _placebo_power_action('poweroff')
    else:
        log.info('powering off lab %s ...', lab_name)
        dcapi.power_off_lab(lab_name)

def _ensure_poweron(lab_name, testing_enabled):
    if testing_enabled:
        _placebo_power_action('poweroff')
    else:
        log.info('powering on lab %s ...', lab_name)
        dcapi.power_on_lab(lab_name)

def _placebo_power_action(action):
    log.info("STATE_SERVICE_TESTING_ENABLED, faking %s..." % (action))
    time.sleep(5)
