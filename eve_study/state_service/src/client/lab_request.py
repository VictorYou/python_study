'''LSS client-side functions for lab reservation
'''

import logging
import requests
import time
import datetime
import json
import sys
import os
import random
from .dict_builder import DictionaryBuilder
import re

from .globals import *
from .utils import count_seconds, create_tag_string, _print_out, _print_out_and_log, _format_string, _formulate_admin_server_access_str, load_json_content
import rest_client as rest

log = logging.getLogger(__name__)

FINAL_LAB_STATES = ['ready', 'state_operation_failed', 'no_matching_state']
FAILED_LAB_STATES = ['state_operation_failed', 'no_matching_state']
LABREQUEST_ERROR_STATES = ['error', 'no_matching_state']

FINAL_SNAPSHOT_STATUSES = ['available', 'failed']
NOT_INHERITED_STATE_FIELDS = ['snapshot_status', 'snapshot_id']

def request_lab(service_url=None, username=None, state_search_query=None, lab_search_query=None, message=None,
                lab_reservation_wait_time=None, lab_reservation_duration=None,
                lab_revert_wait_time=None,
                lab_reservation_tag=None,
                **kwargs):
    """   Allocates lab from lab state service according to given search query.
    """
    lab_reservation_tag_template = lab_reservation_tag
    lab_search_query_str = lab_search_query if lab_search_query is not None else ''
    lab_reservation_tag = create_tag_string(lab_reservation_tag, 
        dict(username=username,
            state_search_query=state_search_query, lab_search_query=lab_search_query_str, 
            message=message,))

    log.info("CMD line params: username: '%s'," +
             " query: '%s', lab_search_query: '%s'," +
             "\n\t message: '%s', " +
             "\n\t wait_time: '%s', revert_wait_time: '%s', duration: '%s'" +
             "\n\t lab_reservation_tag: '%s' from tag template: '%s'",
            username, state_search_query, lab_search_query, message,
            lab_reservation_wait_time, lab_revert_wait_time, lab_reservation_duration,
            lab_reservation_tag, lab_reservation_tag_template)

    lab_reservation_wait_time = count_seconds(lab_reservation_wait_time)
    lab_reservation_duration = count_seconds(lab_reservation_duration)
    log.debug('''After conversion to seconds: 'lab_reservation_wait_time' is %s and 'lab_reservation_duration' is %s''',
        lab_reservation_wait_time, lab_reservation_duration) 

    exit_code = 0
    try:
        lab_name, lab_status, status_message, timeout_triggered = _request_lab(
            username,
            state_search_query, lab_search_query, message,
            lab_reservation_wait_time,
            lab_reservation_duration,
            lab_revert_wait_time,
            lab_reservation_tag,
            service_url)

        log.debug('Result of lab request: lab_status=%s timeout_triggered=%s lab_name=%s' % 
            (lab_status, timeout_triggered, lab_name))
        if lab_status in LABREQUEST_ERROR_STATES or lab_status in FAILED_LAB_STATES or timeout_triggered:
            log.warning('request_lab() FAILED')
            exit_code = 1

        message = "LAB: {} {}".format(lab_name, status_message)
    except requests.exceptions.HTTPError as e:
        exit_code = 1
        message = " ### ERROR: '{}'".format(e.message)
        log.exception(e)
        raise
    finally:
        _print_out_and_log(exit_code, message, kwargs['output_file'])

    return exit_code

def release_lab(service_url=None, username=None, lab_name=None, force_release=False, **kwargs):
    """   Releases given lab in lab state service.
    """
    log.info(("CMD line params: username:'{}'," +
              " labName:'{}'").format(username, lab_name))

    exit_code = 0
    message = ''
    try:
        status_ok, lab_id, reservation_id, reservation_etag, err_message, previously_reverted_state = _check_lab_reservation_status(username, lab_name, service_url)
        if status_ok:
            rest.delete_item('reservations', reservation_id,
                         None, reservation_etag, service_url, force_flag = force_release)
            message = "Released lab: '{}' ({})".format(lab_name, lab_id)
        else:
            exit_code = 1
            message = err_message
    except requests.exceptions.HTTPError as e:
        exit_code = 1
        log.exception(e)
        if e.response.status_code == 422:
            message = " ### ERROR: Precondition failure in removing 'reservations/{}'! Check the 'status' of the lab. ".format(reservation_id)
        else:
            message = " ### ERROR: '{}'".format(e.message)
            raise e
    except requests.exceptions.RequestException as e:
        exit_code = 1
        log.debug('''Exception e='%s' is %s''' % (e, type(e)))
        message = " ### ERROR: '{}'".format(e.message)
        log.exception(e)
        raise e
    finally:
        _print_out_and_log(exit_code, message, kwargs['output_file'])

    return exit_code

def change_lab_reservation(service_url=None, username=None, lab_name=None, duration=None, **kwargs):
    ''' Changing the reservation of the lab:
        :param duration 
            * first alternative: numeric value
                with +|- time in seconds for lab reservation time to be added or reduced
                plain number set the duration of the reservation
            * second alternative: date or date + hour and minutes
                time in datetime format when lab reservation should expire 
    '''
    log.info('Changing lab reservation: lab=%s duration=%s' % (lab_name, duration))
    # fetch lab
    lab = rest.get_item('labs', lab_name, service_url)
    reservation_id = lab['reservation']
    log.debug('Lab: %s Reservation: %s' % (lab['lab_name'], reservation_id))
    reservation = rest.get_item('reservations', lab['reservation'], service_url)
    log.debug('Reservation: %s' % (reservation))

    updates = _parse_duration_input(duration)
    if updates is None:
        log.error('Invalid duration value; %s', duration)
        return 255
    log.debug('Updates: %s Duration: %s ExpireAt: %s', updates, updates.get('duration'), updates.get('ExpireAt'))

    resp = rest.patch_item('reservations', reservation_id, updates, reservation['_etag'], service_url, raise_error=False)
    log.debug('RESPONSE: %s', resp)
    if resp['_status'] == 'ERR':
        error = resp.get('_error')
        if error is not None:
            log.error('HTTP %u %s', error['code'], error['message'])
            return error['code']
        else:
            issues = resp.get('_issues','')
            for issue, mess in issues.items():
                log.error('%s:\t%s', issue, mess)
            return 255
    return 0

def  _parse_duration_input(duration_string):
    ''' return duration and expireAt values that will be sent to server '''
    for datetime_pattern in ('%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S'):
        try:
            tstamp_epoch = time.mktime(time.strptime(duration_string, datetime_pattern))
            # convert to UTC
            tstamp_gm = time.gmtime(tstamp_epoch)
            log.info('UTC time for reservation expiration: %s', tstamp_gm)
            return {'expireAt': time.strftime('%a, %d %b %Y %H:%M:%S GMT', tstamp_gm)}
        except ValueError as ve:
            log.debug('datetime pattern %s does not match input %s', datetime_pattern, duration_string)
            tstamp = None
    # no match for date format: return duration_string 
    duration_string = duration_string.strip()
    duration = count_seconds(duration_string)
    log.debug('*** duration_string: %s duration: %s', duration_string, duration)
    if duration is not None:
        return {'duration': ('+' if duration_string[0] == '+' else '') + str(duration)}

def preserve_state(service_url=None, username=None, lab_name=None, snapshot_wait_time=None, **kwargs):
    """   Preserves the lab state by triggering a snapshot operation in given lab.
      - New 'state'-item is based on 'previously_reverted_state' of the lab.
      - 'state'-item changes can be provided using optional attributes '-a|-d|-s'
      - 'state'-item schema can be seen with 'show-schema' operation
    """
    SET_ATTRIBUTE_LIST = kwargs['set_attribute_list']
    DELETE_ATTRIBUTE_LIST = kwargs['delete_attribute_list']
    APPEND_TO_LIST_LIST = kwargs['append_to_list_list']
    TRIGGER_AND_EXIT = kwargs['trigger_and_exit']

    message = ""
    log.info(("CMD line params 'preserve_state' : username:'{}'," +
              " labName:'{}' WAIT_TIME: '{}' SET_ATTR_LIST: '{}' DELETE_ATTR_LIST: '{}' APPEND_TO_LIST_LIST: '{}' TRIGGER_AND_EXIT: '{}'").
             format(username,
                    lab_name, snapshot_wait_time,
                    SET_ATTRIBUTE_LIST,
                    DELETE_ATTRIBUTE_LIST,
                    APPEND_TO_LIST_LIST,
                    TRIGGER_AND_EXIT))
    exit_code = 0
    try:
        status_ok, lab_id, reservation_id, reservation_etag, err_message, previously_reverted_state = _check_lab_reservation_status(username, lab_name, service_url)
        if status_ok:
            if previously_reverted_state:
                status_ok, build_id, _id, err_message = _preserve_state_operation(lab_id,
                                                                                  previously_reverted_state,
                                                                                  snapshot_wait_time,
                                                                                  SET_ATTRIBUTE_LIST,
                                                                                  DELETE_ATTRIBUTE_LIST,
                                                                                  APPEND_TO_LIST_LIST,
                                                                                  TRIGGER_AND_EXIT,
                                                                                  service_url)
                if status_ok:
                    message = "Snapshot taken from lab: '{}', build.id= '{}' (state_id: {})".format(lab_name, build_id, _id)
                    if TRIGGER_AND_EXIT:
                        message = "Snapshot operation has been triggered in lab: '{}', build.id= '{}' (state_id: {})".format(lab_name, build_id, _id)
                else:
                    exit_code = 1
                    message = " ### ERROR: '{}'".format(err_message)
            else:
                message = " ### ERROR: 'Previously reverted state' is missing!!\n\t\t Check that lab is reserved using 'request-lab' operation!".format(lab_name)
                exit_code = 1
        else:
            message = err_message
            exit_code = 1

    except ValueError as e:
        exit_code = 1
        log.debug('''Exception e='%s' is %s''' % (e, type(e)))
        message = " ### ERROR: '{}'".format(e.message)
        log.exception(e)
        raise e
    finally:
        _print_out_and_log(exit_code, message, kwargs['output_file'])

    return exit_code

def _request_lab(username, state_search_query, lab_search_query, message,
                lab_reservation_wait_time, lab_reservation_duration, lab_revert_wait_time, lab_reservation_tag, base_url):
    ''' create and handle request for reserving lab '''
    # TODO handle sleeping dynamically
    sleep_time = 2
    timeout_triggered = True
    request_lab_operation_err_text = " ### ERROR in 'request-lab' operation"

    labrequest_id = _create_labrequest(username, state_search_query, lab_search_query, message, base_url, lab_reservation_duration, lab_reservation_tag)

    # differ b/w two phases: 1) reserve some lab 2) wait for restoring snapshot
    # Phase 1 - try to reserve lab
    starttime = time.time()
    lab_id, labrequest_status, labrequest_etag, timeout_triggered = \
        _wait_for_lab_reservation(labrequest_id, lab_reservation_wait_time, starttime, base_url, state_search_query)
    log.debug('Reservation phase result: lab_id=%s, labrequest_status=%s, labrequest_etag=%s, timeout_triggered=%s' % \
        (lab_id, labrequest_status, labrequest_etag, timeout_triggered))

    # Phase 2 - try to revert lab
    if lab_id is not None:
        log.info('Lab reservation succeeded: %s' % (lab_id))
        starttime = time.time()
        return _wait_for_lab_revert(lab_id, labrequest_id, lab_revert_wait_time, starttime, base_url, labrequest_etag)
    else:
        lab_id = '<none>'
    return lab_id, labrequest_status, labrequest_etag, timeout_triggered

def _create_labrequest(username, state_search_query, lab_search_query, message, base_url, lab_reservation_duration, lab_reservation_tag):
    ''' create request for reserving lab to REST interface base_url '''
    labrequest_fields = {'username': username,
                         'message': message,
                         'state_search_query': state_search_query}
    log.debug('labrequest_fields: %s' % (labrequest_fields))
    if lab_search_query:
        labrequest_fields.update({'lab_search_query': lab_search_query})
    log.debug('labrequest_fields: %s' % (labrequest_fields))
    if lab_reservation_duration:
        log.debug('lab_reservation_duration: %s' % (lab_reservation_duration))
        labrequest_fields.update({'lab_reservation_time': str(lab_reservation_duration)})
    if lab_reservation_tag:
        labrequest_fields.update({'tag': re.sub(r'["{} ]', '', lab_reservation_tag)})
    log.debug('labrequest_fields: %s' % (labrequest_fields))

    response_data = rest.post_resource('labrequests', labrequest_fields, base_url)
    return response_data['_id']

def _wait_for_lab_reservation(labrequest_id, lab_reservation_wait_time, starttime, base_url, state_search_query, sleep_time = 2):
    request_lab_operation_err_text = " ### ERROR in 'request-lab' operation"
    timeout_triggered = True
    lab_id, labrequest_status, labrequest_etag = None, 'pending', None
    while (( int(time.time() - starttime) < int(lab_reservation_wait_time) 
             or (int(lab_reservation_wait_time) == 0 and labrequest_status == 'pending') 
           ) and lab_id is None):
        labrequest_status, labrequest_etag, lab_id = _get_labrequest_data(labrequest_id, base_url)
        log.debug('*** PHASE 1 LOOP: Lab Reservation - %u < %u labrequest_status=%s' % (int(time.time() - starttime), int(lab_reservation_wait_time), labrequest_status))
        log.debug('CHECK: labrequest_status=%s in LABREQUEST_ERROR_STATES=%s lab_id="%s"' % (labrequest_status, LABREQUEST_ERROR_STATES, lab_id))
        if labrequest_status in LABREQUEST_ERROR_STATES:
            status_message = request_lab_operation_err_text + ", check query '{}'".format(state_search_query)
            timeout_triggered = False
            return None, labrequest_status, status_message, timeout_triggered
        elif lab_id is None:
            rest.patch_item('labrequests', labrequest_id +
                        "/keepalive", None, labrequest_etag, base_url)
            time.sleep(sleep_time)
        else:
            timeout_triggered = False
    log.debug('_wait_for_lab_reservation() LOOP 1 Exit: lab_id=%s' % (lab_id))

    if timeout_triggered:
        log.debug('timeout_triggered: lab_reservation_wait_time=%s state: %s' % (lab_reservation_wait_time, labrequest_status))
        status_message = request_lab_operation_err_text + ", timeout '{}' secs expired: '{}'".format(lab_reservation_wait_time,
                                                                                                     labrequest_status)
        return lab_id, labrequest_status, status_message, timeout_triggered
    return lab_id, labrequest_status, labrequest_etag, timeout_triggered

def _wait_for_lab_revert(lab_id, labrequest_id, lab_revert_wait_time, starttime, base_url, labrequest_etag, sleep_time = 2):
    request_lab_operation_err_text = " ### ERROR in 'request-lab' operation"
    timeout_triggered = True
    lab_status = ""
    status_message = ""
    while int(time.time() - starttime) < int(lab_revert_wait_time):
        log.debug('*** PHASE 2 LOOP: Waiting for Snapshot Revert - %u < %u' % (int(time.time() - starttime), int(lab_revert_wait_time)))
        lab_name, lab_status, lab_in_final_state = _check_if_lab_is_in_final_state(lab_id, base_url)
        log.debug('CHECK: %s in FINAL_LAB_STATES=%s is %s ???' % (lab_status, FINAL_LAB_STATES, lab_in_final_state))
        if lab_in_final_state:
            timeout_triggered = False
            log.debug('_wait_for_lab_revert(): CHECK: %s in FAILED_LAB_STATES=%s' % (lab_status, FAILED_LAB_STATES))
            if lab_status in FAILED_LAB_STATES:
                status_message = request_lab_operation_err_text + ", reverting snapshot failed '{}'".format(lab_status)
            break
        rest.patch_item('labrequests', labrequest_id +
                    "/keepalive", None, labrequest_etag, base_url)
        time.sleep(sleep_time)

    if timeout_triggered:
        log.debug('timeout_triggered: %s state: %s' % (lab_revert_wait_time, lab_status))
        status_message = request_lab_operation_err_text + ", timeout '{}' secs expired: '{}'".format(lab_revert_wait_time,
                                                                                                     lab_status)
    log.debug('_wait_for_lab_revert() RETURN: lab_name=%s, lab_status=%s, status_message=%s, timeout_triggered=%s' %\
        (lab_name, lab_status, status_message, timeout_triggered))
    return lab_name, lab_status, status_message, timeout_triggered

def _get_labrequest_data(labrequest_id, base_url):
    data = rest.get_item('labrequests', labrequest_id, base_url)
    labrequest_status = data.get('status')
    labrequest_etag = data.get('_etag')
    lab_id = data.get('lab')
    return labrequest_status, labrequest_etag, lab_id

def _check_if_lab_is_in_final_state(lab_id, base_url):
    lab_in_final_state = False
    data = rest.get_item('labs', lab_id, base_url)
    lab_name = data.get('lab_name')
    lab_status = data.get('status')
    if lab_status in FINAL_LAB_STATES:
        lab_in_final_state = True
    return lab_name, lab_status, lab_in_final_state

def _check_lab_reservation_status(username, lab_name, lab_pool_url):
    exists = False
    lab_id = ""
    message = ""
    reservation_id = None
    reservation_etag = None
    previously_reverted_state = None
    query = "%s/labs?where={\"lab_name\":\"%s\"}" % (lab_pool_url, lab_name)
    data = rest.get_labs(query, lab_pool_url)
    if len(data[0]['_items']) > 0:
        lab_data = data[0]['_items'][0]
        lab_id = lab_data['_id']
        previously_reverted_state = lab_data.get('previously_reverted_state')
        if lab_data.get('reservation'):
            lab_username = lab_data['reservation']['username']
            reservation_id = lab_data['reservation']['_id']
            reservation_etag = lab_data['reservation']['_etag']
            if lab_username != username:
                message = " ### ERROR: '{}' is currently reserved by another user: '{}'!".format(lab_name, lab_username)
            else:
                exists = True
                message = " *** Lab '{}' reserved by '{}' (labs/{},reservations/{})".format(
                    lab_name, username, lab_id, reservation_id)
        else:
            message = " ### ERROR: '{}' is not currently reserved!".format(lab_name)
    else:
        message = "### ERROR: '{}' does not exist!".format(lab_name)

    log.info("_check_lab_reservation_status({},{}): exists: '{}' lab_id: '{}' res_id:'{}': res_etag:'{}': msg'{}': prev_state:'{}'".format(username, lab_name, exists, lab_id, reservation_id, reservation_etag, message, previously_reverted_state))
    return exists, lab_id, reservation_id, reservation_etag, message, previously_reverted_state

def _preserve_state_operation(lab_id, previously_reverted_state, wait_time,
                              set_attr_list, delete_attr_list,
                              append_to_list_list,
                              trigger_and_exit,
                              base_url):
    err_message = ""
    build_id = ""
    _id = ""
    status_ok = False
    starttime = time.time()
    sleep_time = 2
    state_data = _formulate_new_state(previously_reverted_state,
                                      set_attr_list, delete_attr_list,
                                      append_to_list_list)
    response = rest.post_resource('states', state_data, base_url)
    if trigger_and_exit:
        status_ok = True
    while int(time.time() - starttime) < int(wait_time):
        log.debug(" *** preserve-state post new state waiting '{}'".format(wait_time))
        data = rest.get_item('states', response['_id'], base_url)
        snapshot_status = data.get('snapshot_status')
        _id = data['_id']
        build = data.get('build')
        if build:
            build_id = build['id']
        log.debug(" *** build_id: '{}', snapshot_status: '{}'".format(build_id, snapshot_status))
        if snapshot_status in FINAL_SNAPSHOT_STATUSES:
            if snapshot_status == 'available':
                status_ok = True
            else:
                status_ok = False
                err_message = "Snapshot error!"
            break
        time.sleep(sleep_time)
    return (status_ok, build_id, _id, err_message)

def _formulate_new_state(previously_reverted_state,
                         set_attr_list, delete_attr_list, append_to_list_list):
    log.info(" *** _formulate_new_state(): state: '{}', set: '{}', delete: '{}', append: '{}'".format(
        previously_reverted_state, set_attr_list,
        delete_attr_list, append_to_list_list))

    deleted_fields = NOT_INHERITED_STATE_FIELDS
    if delete_attr_list is not None:
        deleted_fields += delete_attr_list

    new_state = DictionaryBuilder(inherit=previously_reverted_state,
                                  add=set_attr_list,
                                  delete=deleted_fields,
                                  append=append_to_list_list,
                                  exclude_meta=True)
    log.info(" *** _formulate_new_state(): new_state: '{}'".format(new_state.data))
    return new_state.data

