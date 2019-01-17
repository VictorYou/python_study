'''LSS API

Module is based on eve (http://python-eve.org) to provide REST interface for LSS server.

According to eve 'settings.py' contain the basic definitions of LSS server application.
See https://eve.readthedocs.io/en/latest/config.html for full documentation.
'''

import flask
from eve import Eve
from eve.methods.patch import patch_internal
from eve.methods.get import get_internal
import eve_swagger
import bson
from wsgiref.handlers import format_date_time
import labrequest_tasks
import snapshot_tasks
import os
import time
import re
import logging
import json
from datetime import datetime, timedelta

# set environment variable PYDOC_RUN to some value before running pydoc
if os.getenv('PYDOC_RUN') is None:
    app = Eve()  # defaults to settings.py
    app.register_blueprint(eve_swagger.swagger)  # required. See http://swagger.io/specification/#infoObject for details.
    logger = app.logger
    logger.addHandler(logging.StreamHandler())

    FINAL_LAB_STATES = ['ready', 'state_operation_failed']

    if os.getenv('STATE_SERVICE_API_LOG_LEVEL'):
        logger.setLevel(logging.getLevelName(os.getenv('STATE_SERVICE_API_LOG_LEVEL')))
    logger.debug('logger: %s app.debug=%s' % (logger, app.debug))

    LAB_WHITE_LIST = os.getenv('STATE_SERVICE_LAB_WHITE_LIST', '').split()
    LAB_WHITE_LIST += ["DummySprint0{0}".format(a) for a in xrange(1, 6)]
    logger.debug('Startup: LAB_WHITE_LIST: %s' % (LAB_WHITE_LIST))

    # These params are for testing purposes. STATE_SERVICE_TESTING_ENABLED means that storage API will not be used
    STATE_SERVICE_TESTING_ENABLED = True if os.getenv('STATE_SERVICE_TESTING_ENABLED', "") == "yes" else False

    @app.route('/suts', methods=['POST'])
    def route_add_a_sut():
        logger.warning("to add a sut")
        response, last_modified, etag, status = _labrequests_update_expire_after(labrequest_id)
        return json.dumps(response, cls=app.data.json_encoder_class), status

    @app.route('/labrequests/<labrequest_id>/keepalive', methods=['PATCH'])  # TODO: CORS doesn't seem to work to this
    def route_labrequest_keepalive(labrequest_id):
        if os.getenv('STATE_SERVICE_API_DISABLE_TASKS'):
            logger.warning("STATE_SERVICE_API_DISABLE_TASKS defined, not sending Celery tasks")
        else:
            labrequest_tasks.process_labrequests.delay()
        response, last_modified, etag, status = _labrequests_update_expire_after(labrequest_id)
        return json.dumps(response, cls=app.data.json_encoder_class), status

#    @app.route('/states/<state_id>/revert', methods=['PATCH'])  # TODO: CORS doesn't seem to work to this
#    def route_state_revert(state_id):
#        try:
#            # NOTE! get_internal returns: response, last_modified, etag, status, headers
#            #       response, status and headers seem ok, but etag and last_modified are None.
#            response, last_modified, etag, status, headers = get_internal('states', _id = state_id)
#            states = response.get('_items')
#            logger.debug('status: %s states: %s' % (status, states))
#            if not states or status >= 400:
#                return json.dumps({"_status": "ERR",
#                                   "_issues": "states/{}/revert not found".format(state_id)}), 404
#            lab_id = str(states[0]['lab'])
#            lab = _get_internal_item('labs', _id = lab_id)
#            logger.debug('Lab: %s for id=%s' % (lab, lab_id))
#            _update_with_retry('labs', lab_id, {'status': "queued_for_revert"})
#            if os.getenv('STATE_SERVICE_API_DISABLE_TASKS'):
#                logger.warning("STATE_SERVICE_API_DISABLE_TASKS defined, not sending Celery task \"snapshot_tasks.revert_to_snapshot.delay(lab_id={}, state_id={})\"".format(lab_id, state_id))
#            else:
#                logger.debug('****** STATE_SERVICE_TESTING_ENABLED: %s' % (STATE_SERVICE_TESTING_ENABLED))
#                lab_name = lab['lab_name']
#                # get lab_white_list from DB or from LAB_WHITE_LIST
#                lab_white_list_response = _get_internal_item('config', 'LAB_WHITE_LIST', 'name', default='')
#                lab_white_list = lab_white_list_response['value'].split() if lab_white_list_response != '' else None
#                logger.debug('****** lab white list from DB: %s ******' % (lab_white_list))
#                lab_white_list = LAB_WHITE_LIST if lab_white_list is None else lab_white_list
#
#                logger.debug('****** lab=%s is in LAB_WHITE_LIST: %s? %s' % (lab_name, lab_white_list, lab_name in lab_white_list))
#                lab_info = dict(lab_name=lab_name, reservation=str(lab.get('reservation'))) 
#                logger.debug('route_state_revert(): lab_info = %s' % (lab_info))
#                logger.debug('route_state_revert(): lab_info[reservation] = %s [%s]' % (lab_info['reservation'], type(lab_info['reservation'])))
#                snapshot_tasks.revert_to_snapshot.delay(
#                    lab_id=lab_id, 
#                    lab_info=lab_info,
#                    state_id=state_id, 
#                    lab_whitelisted=(lab_name in lab_white_list), 
#                    testing_enabled=STATE_SERVICE_TESTING_ENABLED)
#            logger.exception(e)
#            logger.error("Failed to process state revert request. Check above traceback for details.")
#            return json.dumps({"_status": "ERR",
#                               "_issues": {"exception": e.message}}), 500
#        return json.dumps({"_status": "OK"}), 202

def post_POST_states_trigger_take_snapshot(_request, response):
    """Triggers snapshot creation for each new state object.

       To import existing snapshots (i.e. skip snapshot creation), provide 'snapshot_id=<id as in DCStorageAPI>' and 'snapshot_status=available' in the payload.

       To disable snapshot creation set environment variable STATE_SERVICE_API_DISABLE_TASKS=yes.
    """
    # TODO: change lab status before snapshot task picks this?
    if response.status_code == 201:
        response_data = json.loads(response.data)
        if isinstance(flask.request.json, list):
            for index, state in enumerate(flask.request.json):
                lab = str(state['lab'])
                state_id = response_data['_items'][index]['_id']
                state_etag = response_data['_items'][index]['_etag']
                _trigger_snapshot_if_needed(lab, state, state_etag, state_id)
        else:
            state = flask.request.json
            lab = str(state['lab'])
            state_id = response_data['_id']
            state_etag = response_data['_etag']
            _trigger_snapshot_if_needed(lab, state, state_etag, state_id)
    else:
        logger.warning("Not triggering snapshot for failed state creation\n")


def pre_DELETE_reservations_validation(_request, lookup):
    """Validates that reservation can be removed. Not enabled in batch DELETE.

    validations:
        - lab must be in final state

    to skip validation, use 'force' url argument.
    """
    if "force" in flask.request.args:
        logging.info("Validation skipped due to 'force' argument")
    else:
        reservation_id = lookup.get('_id')
        if reservation_id:
            logging.info("Validating removal of reservation: {}".format(reservation_id))
            lab_data = app.data.driver.db['labs'].find_one({'reservation': bson.ObjectId(reservation_id)})
            lab_status = lab_data.get("status")
            logging.debug("lab: {0}, status: {1}".format(lab_data['_id'], lab_status))
            logging.debug("FINAL_LAB_STATES={}".format(FINAL_LAB_STATES))
            if lab_status not in FINAL_LAB_STATES:
                message = "Reservation can not be removed because lab is not in final state. lab.status={0}, must be one of {1}".format(lab_status, FINAL_LAB_STATES)
                logging.error(message)
                flask.abort(422, description=message)
            app.data.driver.db['labs'].update_one({'_id': lab_data['_id']}, {'$unset' :{"reservation":""}})
        else:
            logging.info("Validation skipped due to batch delete")


def pre_DELETE_labs_validation(_request, lookup):
    """Validates that lab can be removed. Not enabled in batch DELETE.

    validations:
        - lab must be in final state

    to skip validation, use 'force' url argument.
    """
    if "force" in flask.request.args:
        logging.info("Validation skipped due to 'force' argument")
    else:
        labid = lookup.get('_id')
        if labid:
            labdata = app.data.find_one_raw('labs', bson.ObjectId(labid))
            lab_status = labdata.get('status')
            logging.info("status: {}".format(lab_status))
            if lab_status not in FINAL_LAB_STATES:
                message = "Lab can not be removed because lab is not in final state. lab.status={0}, must be one of {1}".format(lab_status, FINAL_LAB_STATES)
                logging.error(message)
                flask.abort(422, description=message)
        else:
            logging.info("Validation skipped due to batch delete")


def _trigger_snapshot_if_needed(lab, state, state_etag, state_id):
    if "snapshot_id" in state and "snapshot_status" in state:
        logger.warning("snapshot_id and snapshot_status given, not triggering take snapshot task")
    elif os.getenv('STATE_SERVICE_API_DISABLE_TASKS'):
        logger.warning("STATE_SERVICE_API_DISABLE_TASKS defined, not sending Celery task \"snapshot_tasks.take_snapshot.delay(lab_id={}, state_id={}, state_etag={})\"".format(lab, state_id, state_etag))
    else:
        logger.info("Triggering snapshot task for lab: {0}\nstate: {1}".format(lab, state_id))
        snapshot_tasks.take_snapshot.delay(lab_id=lab, state_id=state_id, state_etag=state_etag)

def post_POST_labrequests_add_expiry_time(_request, response):
    """Adds expireAt in labrequest.

    NOTE! labrequests will be automatically deleted if keepalive is not called by the client."""
    if response.status_code == 201:
        response_data = json.loads(response.data)
        labrequest_id = response_data['_id']
        _labrequests_set_expire_after(labrequest_id)
    else:
        logger.warning("Not adding 'expireAt' for failed labrequests creation")


def _labrequests_set_expire_after(labrequest_id, minutes=1):
    expire_at = _datetime_to_rfc1123(datetime.now() + timedelta(minutes=minutes))
    response, last_modified, etag, status = patch_internal('labrequests',
                                                           payload={'expireAt': expire_at},
                                                           concurrency_check=False,
                                                           skip_validation=True,
                                                           _id=labrequest_id)
    return response, last_modified, etag, status


def _labrequests_update_expire_after(labrequest_id, minutes=1):
    expire_at = _datetime_to_rfc1123(datetime.now() + timedelta(minutes=minutes))
    return _update_with_retry('labrequests', labrequest_id, {'expireAt': expire_at}, skip_validation=True)

def _datetime_to_rfc1123(dt):
    return format_date_time(
        time.mktime(dt.timetuple()))

def _update_with_retry(resource, item_id, patch_data, max_retries=50, skip_validation=False):
    item = _get_internal_item(resource, item_id)
    retries = 1
    response, last_modified, etag, status = None, None, None, None
    if item:
        while retries <= max_retries:
            item_etag = item.get('_etag')
            try:
                new_environ = flask.request.environ
                new_environ['HTTP_IF_MATCH'] = item_etag
                with app.request_context(new_environ):
                    logger.info("Updating item {} with {}".format(item_id, patch_data))
                    response, last_modified, etag, status = patch_internal(resource,
                                                                           payload=patch_data,
                                                                           concurrency_check=True,
                                                                           skip_validation=skip_validation,
                                                                           _id=item_id)
                    break
            except Exception as e:
                if "Precondition Failed" in str(e):
                    logger.warning("Retrying {0}/{1} due to {2}\netag: {3}".format(retries, max_retries, e, item_etag))
                    time.sleep(0.01)
                else:
                    break
            retries += 1
            item = _get_internal_item(resource, item_id)
        return response, last_modified, etag, status
    else:
        return {"_status": "ERR", "_issues": "{} Not Found in {}".format(item_id, resource)}, None, None, 404


def _get_internal_item(resource, _id = None, _id_field = None, default = None):
    # NOTE! get_internal returns: response, last_modified, etag, status, headers
    #       response, status and headers seem ok, but etag and last_modified are None.
    lookup = {'_id': _id} if _id is not None else {}
    lookup = {_id_field : _id} if _id_field is not None else lookup
    logger.debug('Calling get_internal(resource=%s, lookup=%s)' % (resource, lookup))
    response, last_modified, etag, status, headers = get_internal(resource, **lookup)
    logger.debug('Calling get_internal returned: response=%s, last_modified=%s, etag=%s, status=%s, headers=%s' % (str(response)[:11], last_modified, etag, status, headers))
    items = response.get('_items')
    return items[0] if len(items) > 0 else default

def on_inserted_states_create_cross_reference_to_lab(states):
    """Creates cross reference in a lab object"""
    # TODO: make this thread safe. possibly with REST + _etag + retries
    for state in states:
        lab_id = state.get('lab')
        lab = app.data.find_one_raw('labs', lab_id)
        state_id = state['_id']
        if "states" in lab.keys():
            lab_states = lab['states']
            lab_states.append(state_id)
        else:
            lab_states = [state_id]
        app.data.update('labs', lab_id, {'states': lab_states}, lab)


def on_delete_states_remove_cross_reference_from_lab(state):
    """Removes cross reference from a lab object"""
    # TODO: make this thread safe. possibly with REST + _etag + retries
    lab_id = state.get('lab')
    state_id = state['_id']
    if lab_id:
        lab = app.data.find_one_raw('labs', lab_id)
        logger.info("Removing state {} from lab {}".format(state['_id'], lab_id))
        states = lab.get('states')
        if states and state_id in states:
            states.remove(state_id)
        app.data.update('labs', lab_id, {'states': states}, lab)


def on_inserted_labreservations_create_cross_reference_to_lab(reservations):
    """Creates cross reference in a lab object"""
    for reservation in reservations:
        logger.debug('inserted reservation: %s', reservation)
        lab_id = reservation.get('lab')
        lab = app.data.find_one_raw('labs', lab_id)
        reservation_id = reservation['_id']
        app.data.update('labs', lab_id, {'reservation': reservation_id}, lab)


def on_delete_reservations_remove_cross_reference_from_lab(reservation):
    """Removes cross reference from a lab object"""
    lab_id = reservation.get('lab')
    if lab_id:
        lab = app.data.find_one_raw('labs', lab_id)
        logger.info("Removing reservation {} from lab {}".format(reservation['_id'], lab_id))
        app.data.update('labs', lab_id, {'reservation': None}, lab)

def on_delete_labs_delete_related_items(lab):
    """Deletes related states and reservations"""
    for state in lab.get('states', []):
        if state:
            app.data.remove('states', {'_id': state})
    reservation = lab.get('reservation')
    if reservation:
        app.data.remove('reservations', {'_id': reservation})

def on_update_reservations_handle_duration(updates, original):
    ''' update fields 'duration' and 'expireAt' of the lab reservation when 
        either of upgrade or expireAt is patched by the client ''' 
    duration_change = updates.get('duration')
    expireAt_new = updates.get('expireAt')
    duration = original.get('duration')
    expireAt = original.get('expireAt')
    if duration_change is not None:
        if duration_change.startswith(('+','-')):
            # update by duration_change, set expireAt := creation time + duration
            if duration is None:
                app.logger.error('previous duration must exist for updating duration')
                flask.abort(422, description = 'previous duration must exist for update')
            duration_seconds = int(duration) + int(duration_change)
        else:
            duration_seconds = int(duration_change)
        updates['expireAt'] = original['_created'] + timedelta(seconds = duration_seconds)
    elif expireAt_new is not None:
        creation_time = original['_created']
        creation_time = datetime(
            creation_time.year,
            creation_time.month,
            creation_time.day,
            creation_time.hour,
            creation_time.minute
        )
        duration_seconds = int((expireAt_new - creation_time).total_seconds())

    if duration_seconds < 0:
        app.logger.error('duration cannot be < 0: %u', duration_seconds)
        flask.abort(422, description = 'duration cannot be < 0')
    updates['duration'] = str(duration_seconds)
    app.logger.debug('Updates to lab reservation: %s', updates)

# set environment variable PYDOC_RUN to some value before running pydoc
if os.getenv('PYDOC_RUN') is None:
    # db event hooks
    app.on_inserted_states += on_inserted_states_create_cross_reference_to_lab
    app.on_inserted_reservations += on_inserted_labreservations_create_cross_reference_to_lab
    app.on_delete_item_states += on_delete_states_remove_cross_reference_from_lab
    app.on_delete_item_reservations += on_delete_reservations_remove_cross_reference_from_lab
    app.on_delete_item_labs += on_delete_labs_delete_related_items
    app.on_update_reservations += on_update_reservations_handle_duration

    # http event hooks
    app.on_post_POST_states += post_POST_states_trigger_take_snapshot
    app.on_post_POST_labrequests += post_POST_labrequests_add_expiry_time
    app.on_pre_DELETE_reservations += pre_DELETE_reservations_validation
    app.on_pre_DELETE_labs += pre_DELETE_labs_validation

    eve_swagger.add_documentation({'paths': {"/labrequests/{labrequestId}/keepalive": {
                                  "patch": {
                                    "summary": "Sets expireAt 1 minute from now",
                                    "responses": {
                                      "200": {
                                        "description": "Accepted"
                                      }
                                    },
                                    "parameters": [
                                      {
                                        "$ref": "#/parameters/Labrequest__id"
                                      }
                                    ],
                                    "tags": ["Labrequest"]
                                  }
                                }
                           }
                 })
    eve_swagger.add_documentation({'paths': {"/states/{stateId}/revert": {
                                  "patch": {
                                    "summary": "Reverts lab to this state",
                                    "responses": {
                                      "200": {
                                        "description": "Accepted"
                                      }
                                    },
                                    "parameters": [
                                      {
                                        "$ref": "#/parameters/State__id"
                                      }
                                    ],
                                    "tags": ["State"]
                                  }
                                }
                           }
                 })

if __name__ == '__main__':   # pragma: no cover
    app.logger.setLevel(logging.DEBUG)
    app.run(host='0.0.0.0', port=5000)
