'''functions for admin actions in LSS server
'''

import logging
import requests
import json
import os
import dcapi
import re
from .globals import *
from .utils import _print_out, _print_out_and_log, _format_string, _formulate_admin_server_access_str, load_json_content, _gen_unit_mock
from .dict_builder import DictionaryBuilder
from .info import show_item, resolve_status_from_response
import rest_client
from .lab_request import _check_lab_reservation_status

log = logging.getLogger(__name__)

DC_STORAGE_LAB_TYPE_MAP = {
    "sprintlab": 'sprint',
    "vsp": 'vsprint',
    "vosp": 'vosp',
    "clab": 'cloud',
    "dummysprint": "other",
}

def admin_patch_item(href, param_list, service_url=None, username=None, **kwargs):
    """   Patches 'labs|states|reservations' item as JSON or text for given href.

    """
    log.debug('admin_patch_item(href=%s, param_list=%s, service_url=%s, username=%s, kwargs=%s)' 
                %
                (href, param_list, service_url, username, kwargs))
    exit_code = 0
    message = ""
    status = "ERROR"
    status_str = ""
    issues = ""
    resource, _id = href.split("/")

    try:
        exit_code, message = _check_admin_operation_credentials(username)
        if exit_code == 0:
            response = rest_client.get_item(resource, _id, service_url)
            _id = response['_id']
            _etag = response['_etag']
            status, issues = _modify_item_data(resource, _id, _etag, service_url, param_list)
            if status in 'OK':
                show_item(href, service_url, **kwargs)
            else:
                exit_code = 1

            status_str = status + issues
            message = "\n *** Operation 'admin-patch-item' ({} '{}') status: {}.\n".format(href, param_list,
                                                                                         _format_string(status_str, status, True))
    except requests.exceptions.HTTPError as e:
        exit_code = 1
        if e.response.status_code == 404:
            log.exception(e)
            message = " ### ERROR: item not found '{}'".format(href)
        else:
            message = " ### ERROR: '{}'".format(e.message)
            raise e
    except Exception as e:
        log.exception(e)
        message = " ### ERROR: '{}'".format(e.message)
        exit_code = 1
        raise e
    finally:
        message += " Exit code: '{}'".format(exit_code)
        _print_out(message, kwargs['output_file'])
    return exit_code

def _modify_item_data(resource, _id, _etag, base_url, param_list):
    status, modify_data, message = _resolve_and_validate_json_data(param_list)
    if status in 'OK':
        log.info("rest_client.patch_item() PATCH data: {}".format(modify_data))
        response = rest_client.patch_item(resource, _id, modify_data, _etag, base_url, False)
        status = response['_status']
        message = _resolve_issues_from_response(response)
    return (status, message)

def _resolve_and_validate_json_data(param_list):
    status = "OK"
    message = ""
    data_value = {}
    json_str_value = ""
    try:
        if '=' in param_list:
            csv_list = param_list.split(',')
            for csv_val in csv_list:
                name, value = csv_val.split('=')
                json_str_value += "\"%s\": \"%s\" , " % (name, value)
        else:
            json_str_value += param_list + " , "
            json_str_value = json_str_value.replace('\'', '"')
        json_str_value = re.sub(' , $', '', json_str_value)
        if '{' not in json_str_value:
            json_str_value = "{" + json_str_value + "}"
        log.info("_resolve_and_validate_data(param_list): validate json: '{}'".format(json_str_value))
        data_value = json.loads(json_str_value)
    except Exception as e:
        status = "ERROR"
        log.exception(e)
        message = " ### JSON data validation failed. '{}' {}".format(json_str_value, e.message)
    return (status, data_value, message)

def _resolve_issues_from_response(response):
    issues_txt = ""
    issues = response.get('_issues')
    if issues is not None:
        issues_txt = ": " + str(issues)
        issues_txt = re.sub("u'", '\'', issues_txt)
    return issues_txt

def admin_migrate_snapshots(lab_names, admin_server_username, admin_server_password,
                            admin_server_host, admin_server_port, service_url=None, username=None, **kwargs):
    """   Migrates existing snapshots of given Data Center lab into Lab State Service.
       - creates a lab if it does not exist in Lab State Service
       - creates new snapshots for the lab and sets 'snapshot_status' to 'ready'
       - deletes snapshot(s) if it does not exist any more in DC
       - does nothing if snapshot already exists in Lab State Service for given lab
    """
    storage_api_url = kwargs['dcapi_service_url']

    log.info("CMD line params: {0}:'{1}'".format("lab_name", lab_names))

    exit_code = 0
    message = ""
    lab_status = "ready"
    message = "\nOperation 'admin-migrate-snapshots' status:\n"
    message = message + '-' * len(message) + "\n"

    exit_code, message = _check_admin_operation_credentials(username)
    if exit_code == 0:
        for lab_name in lab_names:
            message = message + "\n  {}\n".format(lab_name)
            try:
                lab_id, existing_snapshots, msg = _check_if_lab_exists_in_state_service(lab_name, service_url)
                status, lab_type, msg = _resolve_lab_type(lab_name)
                if status == 0:
                    status, snapshot_data, msg = _resolve_snapshot_data_from_dc_lab(lab_name,
                                                                                    admin_server_username,
                                                                                    admin_server_password,
                                                                                    admin_server_host,
                                                                                    admin_server_port,
                                                                                    storage_api_url)
                    if status == 0:
                        log.info("Snapshot data: '{}'\n".format(snapshot_data))
                        sync_lab_data = [lab_name, lab_id, lab_type, lab_status, snapshot_data]
                        log.info("Sync lab data: '{}'\n".format(sync_lab_data))
                        status, msg = _sync_lab_into_state_service(sync_lab_data, existing_snapshots, service_url)
                if status is not 0:
                    exit_code = 1
                msg = "\n".join(("\t") + i for i in msg.splitlines())
                message = message + msg + "\n"
            except Exception as e:
                exit_code = 1
                log.exception(e)
                message = message + "\t### ERROR: '{}'".format(e.message)
    _print_out_and_log(exit_code, message, kwargs['output_file'])
    return exit_code

def admin_remove_snapshots(lab_name, snapshot_ids, force_removal_flag, service_url=None, username=None, **kwargs):
    """
    Operation reserves the given lab and removes given snapshot(s) from Lab State Service and Data Center (DC) Storage.
    When '--force' option is used, removing will happen in all cases.

    Pre-requisites without '-force' option:
      - lab must be FREE and ready/failed state (client)
      - snapshot must be available/failed state (server)

    """
    log.info("CMD line params: {0}:'{1}'".format("lab_name", lab_name, "snapshot_ids", snapshot_ids))

    exit_code = 0
    message = ""
    try:
        exit_code, message = _check_admin_operation_credentials(username)
        if exit_code == 0:
            if _confirmation_for_deletion(force_removal_flag, CONFIRM_QUESTION_FOR_REMOVE_SNAPSHOTS):
                exit_code, message = _reserve_lab_and_delete_snapshots(lab_name, snapshot_ids, username, force_removal_flag, service_url)
            else:
                exit_code = 1
                message = CONFIRM_QUESTION_OPERATION_CANCELLED
    except Exception as e:
        exit_code = 1
        log.exception(e)
        message = " ### ERROR: '{}' {}".format(e.message, e.text)
        raise e
    finally:
        message += " Exit code: '{}'".format(exit_code)
        _print_out(message, kwargs['output_file'])
    return exit_code

def _confirmation_for_deletion(force_removal_flag, query_text, right_answer=CONFIRM_QUESTION_RIGHT_ANSWER):
    continue_flag = False
    if force_removal_flag is False:
        confirm = raw_input(query_text)
        if confirm == right_answer:
            continue_flag = True
    else:
        continue_flag = True
    return continue_flag

def admin_add_lab(lab_name, lab_status, lab_type=None, service_url=None, username=None, **kwargs):
    """   Adds given lab into Lab State Service.
    """
    log.info("CMD line params: {}:'{}', {}:'{}'".format("lab_name", lab_name,
                                                        "lab_type", lab_type))
    exit_code = 0
    message = ""
    try:
        exit_code, message = _check_admin_operation_credentials(username)
        if exit_code == 0:
            lab_id, snapshot_dict, message = _check_if_lab_exists_in_state_service(lab_name, service_url)
            if lab_id is None:
                data = {'lab_name': lab_name, 'status': lab_status}
                if lab_type is not None:
                    data.update({'lab_type': lab_type})
                response = rest_client.post_resource('labs', data, service_url)
                lab_id = response.get('_id')
                message = "Lab '{}'(_id: 'labs/{}') added into Lab State Service\n".format(lab_name, lab_id)
            else:
                message = " ### ERROR: Lab '{}' (_id: 'labs/{}') already exists in Lab State Service\n".format(lab_name, lab_id)
                exit_code = 1
    except Exception as e:
        exit_code = 1
        log.exception(e)
        message = " ### ERROR: '{}'".format(e.message)
        raise e
    finally:
        message += "Exit code: '{}'".format(exit_code)
        _print_out(message, kwargs['output_file'])
    return exit_code


def admin_remove_labs(lab_names, force_removal_flag, service_url=None, username=None, output_file='STDOUT', **kwargs):
    """   Removes given labs from Lab State Service.
    """
    log.info("CMD line params: {0}:'{1}'".format("lab_names", lab_names))

    exit_code = 0
    message = ""
    status_dict = {}
    index = 1000

    try:
        exit_code, message = _check_admin_operation_credentials(username)
        log.debug('user check for %s was %s (msg: %s)', username, exit_code, message)
        if exit_code == 0:
            if _confirmation_for_deletion(force_removal_flag, CONFIRM_QUESTION_FOR_REMOVE_LABS):
                for lab_name in lab_names:
                    status_ok, status_message = _reserve_lab_and_delete(lab_name, username, force_removal_flag, service_url)
                    if not status_ok:
                        exit_code = 1
                    status_dict[index] = {}
                    status_dict[index][lab_name] = {}
                    status_dict[index][lab_name]['status_ok'] = status_ok
                    status_dict[index][lab_name]['msg'] = status_message
                    index += 1

                message = _formulate_status_dict_for_printing('admin-remove-lab', status_dict, REMOVED_TXT)
            else:
                exit_code = 1
                message = CONFIRM_QUESTION_OPERATION_CANCELLED
    except Exception as e:
        exit_code = 1
        log.exception(e)
        message = " ### ERROR: '{}'".format(e.message)
        raise e
    finally:
        message += " Exit code: '{}'".format(exit_code)
        _print_out(message, output_file)
    return exit_code

def _reserve_lab_and_delete(lab_name, username, force_removal_flag, lab_pool_url):
    status_ok = False
    removal_status_ok, lab_id, lab_etag, snaps_dict, status_message = _check_lab_status_for_removal(lab_name, force_removal_flag, lab_pool_url)
    log.debug('_check_lab_status_for_removal returned: removal_status_ok=%s, lab_id=%s, lab_etag=%s, snaps_dict=%s, status_message=%s',
        removal_status_ok, lab_id, lab_etag, snaps_dict, status_message)
    if removal_status_ok:
        try:
            if force_removal_flag is False:
                reserve_lab_data = {"lab": lab_id,
                                    "username": username,
                                    "message": RESERVE_LAB_FOR_DELETION_MESSAGE}
                response = rest_client.post_resource('reservations', reserve_lab_data, lab_pool_url, True)
                status_ok, status_message = resolve_status_from_response(response)
            if status_ok is True or force_removal_flag is True:
                response = rest_client.delete_item('labs', lab_id, None, lab_etag, lab_pool_url, force_flag = force_removal_flag)
                status_ok = True
        except Exception as e:
            log.exception(e)
            status_message = " ### ERROR: '{}'".format(e.message)
            status_ok = False
    return status_ok, status_message

def _reserve_lab_and_delete_snapshots(lab_name, snapshot_ids, username, force_removal_flag, lab_pool_url):
    status = 0
    status_dict = {}
    status_ok, lab_id, lab_etag, snaps_dict, status_message = _check_lab_status_for_removal(lab_name, force_removal_flag, lab_pool_url, ERROR_TXT)
    if status_ok:
        try:
            if force_removal_flag is False:
                reserve_lab_data = {"lab": lab_id,
                                    "username": username,
                                    "message": RESERVE_LAB_FOR_SNAPSHOT_DELETION_MESSAGE}
                response = rest_client.post_resource('reservations', reserve_lab_data, lab_pool_url, True)
                status_ok, status_message = resolve_status_from_response(response)
            if status_ok is True or force_removal_flag is True:
                index = 1000
                for snapshot_id in snapshot_ids:
                    snap_status_ok = False
                    snap_status_message = ""
                    if snapshot_id in snaps_dict:
                        snap_id = snaps_dict[snapshot_id]['_id']
                        snap_etag = snaps_dict[snapshot_id]['_etag']
                        try:
                            response = rest_client.delete_item('states', snap_id,
                                                    None, snap_etag, lab_pool_url, True,
                                                    force_removal_flag)
                            snap_status_ok = True
                        except requests.exceptions.HTTPError as e:
                            status = 1
                            if e.response.status_code == 404:
                                log.exception(e)
                                snap_status_message = ERROR_TXT_SNAPSHOT_DOES_NOT_EXIST_IN_LAB
                            elif e.response.status_code == 412:
                                log.exception(e)
                                snap_status_message = str(e) + ' ' + e.response.text
                        except Exception as e:
                            log.exception(e)
                            snap_status_message = ERROR_TXT + str(e)
                    else:
                        status = 1
                        snap_status_message = ERROR_TXT_SNAPSHOT_DOES_NOT_EXIST_IN_LAB
                    status_dict[index] = {}
                    status_dict[index][snapshot_id] = {}
                    status_dict[index][snapshot_id]['status_ok'] = snap_status_ok
                    status_dict[index][snapshot_id]['msg'] = snap_status_message
                    index += 1
                status_message = _formulate_status_dict_for_printing('admin-remove-snapshots', status_dict, REMOVED_TXT, lab_name)
        except Exception as e:
            log.exception(e)
            status_message = ERROR_TXT + "'{}'".format(e.message)
            status = 1
    else:
        status = 1
    return status, status_message

def _check_lab_status_for_removal(lab_name, force_removal_flag, base_url, prefix_str=""):
    removal_status_ok = False
    lab_id = ""
    message = ""
    snaps_dict = {}
    lab_etag = None
    query = "%s/labs?where={\"lab_name\":\"%s\"}" % (base_url, lab_name)
    data = rest_client.get_labs(query, base_url)
    log.debug('rest_client.get_labs(query=%s) returned: %s', query, data)
    if len(data[0]['_items']) > 0:
        lab_data = data[0]['_items'][0]
        lab_id = lab_data['_id']
        lab_etag = lab_data['_etag']
        if lab_data.get('states'):
            for state in lab_data['states']:
                if (state.get('snapshot_id')):
                    snapshot_id = state['snapshot_id']
                    snaps_dict[snapshot_id] = {}
                    snaps_dict[snapshot_id]['_id'] = state['_id']
                    snaps_dict[snapshot_id]['_etag'] = state['_etag']
        if force_removal_flag is False:
            if lab_data.get('reservation'):
                reservation_username = lab_data['reservation']['username']
                reservation_message = ""
                if 'message' in lab_data['reservation']:
                    reservation_message = "Message: '" + lab_data['reservation']['message'] + "'"
                message = "Lab is currently reserved by '{}'! {}".format(reservation_username, reservation_message)
            else:
                removal_status_ok = True
        else:
            removal_status_ok = True
            message = " *** INFO: '{}' is ready for removal: FORCE FLAG given. ".format(lab_name)
    else:
        message = "Lab does not exist in Lab State Service! "

    message = prefix_str + message
    log.info("{}".format(message))
    return removal_status_ok, lab_id, lab_etag, snaps_dict, message

def admin_reserve_labs(lab_names, user_message, force_reservation_flag, service_url=None, username=None, **kwargs):
    """
    Reserves given labs from Lab State Service for 'admin'.
       - if 'message' is not given, default text will be used.
       - if 'force-reservation-flag' is 'True',
            - then existing reservation will be removed
            - new reservation will be created for 'admin'
    """
    log.info("CMD line params: labs:'{}' , msg: '{}'".format(lab_names, user_message))

    exit_code = 0
    message = ""
    status_dict = {}
    index = 1000

    try:
        exit_code, message = _check_admin_operation_credentials(username)
        if exit_code == 0:
            for lab_name in lab_names:
                status_ok, status_message = _admin_reserve_lab(lab_name, username, user_message, force_reservation_flag, service_url)
                if not status_ok:
                    exit_code = 1
                status_dict[index] = {}
                status_dict[index][lab_name] = {}
                status_dict[index][lab_name]['status_ok'] = status_ok
                status_dict[index][lab_name]['msg'] = status_message
                index += 1

            message = _formulate_status_dict_for_printing('admin-reserve-lab', status_dict, RESERVED_TXT)
    except Exception as e:
        exit_code = 1
        log.exception(e)
        message = " ### ERROR: '{}'".format(e.message)
        raise
    finally:
        message += " Exit code: '{}'".format(exit_code)
        _print_out(message, kwargs['output_file'])
    return exit_code

def _admin_reserve_lab(lab_name, username, user_message, force_reservation_flag, lab_pool_url):
    status_ok = False
    reservation_status_ok = True
    reservation_id = None
    try:
        reservation_exists, lab_id, reservation_id, reservation_etag, status_message, not_used_var = _check_lab_reservation_status(username, lab_name, lab_pool_url)
        if lab_id == "" or (force_reservation_flag is False and reservation_id):
            status_message = status_message
        else:
            if reservation_id:
                reservation_status_ok, status_message = _remove_reservation_when_needed(reservation_id,
                                                                                        reservation_etag,
                                                                                        force_reservation_flag,
                                                                                        lab_pool_url)
            if reservation_status_ok:
                reserve_lab_data = {"lab": lab_id,
                                    "username": username,
                                    "message": user_message}
                response = rest_client.post_resource('reservations', reserve_lab_data, lab_pool_url, True)
                status_ok, status_message = resolve_status_from_response(response)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 422:
            status_message = " ### ERROR: Precondition failure in removing 'reservations/{}'! Check the 'status' of the lab. ".format(reservation_id)
        else:
            status_message = " ### ERROR: Removing 'reservations/{}' failed! Check the 'status' of the lab. ".format(reservation_id, e.response.text)
        log.exception(e)
    except Exception as e:
        log.exception(e)
        status_message = " ### ERROR: '{}'".format(e.message)
        status_ok = False
    return status_ok, status_message

def _remove_reservation_when_needed(reservation_id, reservation_etag, force_reservation_flag, lab_pool_url):
    status_ok = False
    status_message = ""
    if force_reservation_flag:
        try:
            rest_client.delete_item('reservations', reservation_id,
                         None, reservation_etag, lab_pool_url, True, force_reservation_flag)
            status_ok = True
        except Exception as e:
            log.exception(e)
            status_message = " ### ERROR: '{}'".format(e.message)
    else:
        status_ok = True
    return status_ok, status_message

def admin_data_backup(lab_name, service_url=None, username=None, **kwargs):
    """   Executes backup procedure from Lab State Service.
    """
    log.info("CMD line params: {0}:'{1}'".format("lab_name", lab_name))

    exit_code = 0
    message = ""
    try:
        message = message + "Executing data back-up procedure '{}' from Lab State Service\n".format(lab_name)
    except Exception as e:
        exit_code = 1
        log.exception(e)
        message = " ### ERROR: '{}'".format(e.message)
        raise e
    finally:
        _print_out_and_log(exit_code, message, kwargs['output_file'])
    return exit_code


def admin_data_restore(lab_name, service_url=None, username=None, **kwargs):
    """   Executes data restore procedure for Lab State Service.
    """
    log.info("CMD line params: {0}:'{1}'".format("lab_name", lab_name))

    exit_code = 0
    message = ""
    try:
        message = message + "Executes data restore procedure '{}' for Lab State Service\n".format(lab_name)
    except Exception as e:
        exit_code = 1
        log.exception(e)
        message = " ### ERROR: '{}'".format(e.message)
        raise e
    finally:
        _print_out_and_log(exit_code, message, kwargs['output_file'])
    return exit_code


def show_admin_server_access_data(lab_name, snapshot_id, output_format, service_url=None, username=None, **kwargs):
    """   Shows given snapshot access control parameters.
    """
    log.info("CMD line params: {}:'{}', {}:'{}'".format("lab_name", lab_name, "snapshot_id", snapshot_id))

    exit_code = 0
    message = ""
    #query = "%s/labs?where={\"lab_name\":\"%s\"}" % (service_url, lab_name)
    where = ""
    if lab_name:
        where = "&where={\"lab_name\":\"%s\"}" % lab_name

    query = "%s/labs?%s" % (service_url, where)

    try:
        lab_data = rest_client.get_labs(query, service_url)
        status_ok, message = _resolve_admin_server_access_params(lab_name, snapshot_id, lab_data, output_format)
        if not status_ok:
            exit_code = 1
    except Exception as e:
        exit_code = 1
        log.exception(e)
        message = " ### ERROR: '{}'".format(e.message)
        raise e
    finally:
        show_exit_code_in_stdout = True
        if "JSON" in output_format:
            show_exit_code_in_stdout = False
        _print_out_and_log(exit_code, message, kwargs['output_file'], show_exit_code_in_stdout)
    return exit_code

def _resolve_admin_server_access_params(lab_name, snapshot_id, lab_data, output_format="ASCII"):
    status_ok = False
    message = ""
    labs_data = ""
    header_str = ""
    log.info("_resolve_admin_server_access_params({}, {})".format(lab_name, snapshot_id))
    log.info("      lab_data: '{}'  ".format(lab_data))
    labs = lab_data[0].get('_items')
    if labs:
        if lab_name:
            states = labs[0].get('states')
            status_ok, message, header_str = _formulate_admin_server_access_data(states, lab_name, snapshot_id, output_format)
            if "ASCII" in output_format:
                message = "\n\n{}:\n{}\n".format(lab_name, message)
            elif "CSV" in output_format:
                message = "{}\n{}\n".format(header_str, message)
            elif "JSON" in output_format:
                if status_ok:
                    message = "{{\"lab_name\": \"{}\", \"{}\": {}}}".format(lab_name, ADMIN_SERVER_ACCESS_PARAMETER_NAME, message)
                message = re.sub(r'\n', '', message)
                load_json_content(message)
        elif lab_name is None:
            for lab in labs:
                states = lab.get('states')
                lab_name_data = lab.get('lab_name')
                status_ok, lab_data, header_str = _formulate_admin_server_access_data(states, lab_name_data, snapshot_id, output_format)
                if "ASCII" in output_format:
                    labs_data += "\n\n{}:\n{}".format(lab_name_data, lab_data)
                elif "JSON" in output_format:
                    labs_data += "{{\"lab_name\": \"{}\", \"{}\": {}}},".format(lab_name_data, ADMIN_SERVER_ACCESS_PARAMETER_NAME, lab_data)
                elif "CSV" in output_format:
                    labs_data += lab_data

            if "CSV" in output_format:
                message = "{}\n{}".format(header_str, labs_data)
            elif "JSON" in output_format:
                labs_data = "{{\"{}\": [{}]}}".format("_items", labs_data)
                labs_data = re.sub(r'},]', '}]', labs_data)
                labs_data = re.sub(r'\n', '', labs_data)
                load_json_content(labs_data)
                message = labs_data
            else:
                message = labs_data
    else:
        status_ok = False
        message = ERROR_TXT_NOT_ANY_LABS
        if "JSON" in output_format:
            message = "{{\"{}\": \"{}\", \"{}\": \"{}\"}}".format("status", "Failed", "error_text", message)
            load_json_content(message)

    if lab_name and len(labs) == 0:
        status_ok = False
        message = ERROR_TXT_LAB_DOES_NOT_EXIST.format(lab_name)
        if "JSON" in output_format:
            message = "{{\"{}\": \"{}\", \"{}\": \"{}\"}}".format("status", "Failed", "error_text", message)
            load_json_content(message)

    return (status_ok, message)

def _formulate_admin_server_access_data(states, lab_name, snapshot_id, output_format):
    status_ok = False
    message = ""
    header_str = ""
    data_str = ""

    if lab_name and snapshot_id and (states is None or len(states) == 0):
        message = ERROR_TXT_SNAPSHOT_WITH_BUILD_ID_DOES_NOT_EXIST_IN_LAB.format(snapshot_id)
        if "JSON" in output_format:
            message = "{{\"{}\": \"{}\", \"{}\": \"{}\"}}".format("status", "Failed", "error_text", message)
    elif states:
        for snapshot in states:
            if 'build' in snapshot and 'id' in snapshot['build']:
                build_id = snapshot['build'].get('id')
                if snapshot_id:
                    if build_id == snapshot_id:
                        log.info("      build_id: '{}'".format(snapshot['build']))
                        status_ok = True
                        data_str, header_str = _formulate_admin_server_access_str(snapshot, output_format, build_id, lab_name)
                        break
                    else:
                        message = ERROR_TXT_SNAPSHOT_WITH_BUILD_ID_DOES_NOT_EXIST_IN_LAB.format(snapshot_id)
                        if "JSON" in output_format:
                            message = "{{\"{}\": \"{}\", \"{}\": \"{}\"}}".format("status", "Failed", "error_text", message)

                else:
                    status_ok = True
                    data_tmp_str, header_str = _formulate_admin_server_access_str(snapshot, output_format, build_id, lab_name)
#                    if data_tmp_str:
                    if "JSON" in output_format:
                        data_tmp_str += ','
                    else:
                        data_tmp_str += '\n'
                    data_str += data_tmp_str
    elif lab_name:
        status_ok = True
        snapshot = ()
        build_id = None
        data_str, header_str = _formulate_admin_server_access_str(snapshot, output_format, build_id, lab_name)
        data_str += "\n";

    if status_ok is True:
        if "CSV" in output_format:
            message = data_str
        elif "JSON" in output_format:
            if snapshot_id:
                message = data_str
            else:
                data_str = re.sub(r',$', '', data_str)
                message = "[{}]".format(data_str)
        else:
            message = data_str

    return (status_ok, message, header_str)

def _formulate_status_dict_for_printing(operation, status_dict, operation_text, lab_name=None):
    for_lab = ""
    if lab_name:
        for_lab = "for '{}'".format(lab_name)
    message = "\nOperation '" + operation + "' " + for_lab + " status:\n"
    message = message + '-' * len(message) + "\n\n"
    formating = "\t%-20.20s   %-25.25s            %s\n"
    for i in status_dict:
        for item in status_dict[i]:
            item_txt = item
            if item_txt in '':
                item_txt = "<empty_id>"
            msg = ""
            status_str = str(AsciiColors.BOLD) + str(AsciiColors.REMOVED) + operation_text + str(AsciiColors.ENDC)
            status_ok = status_dict[i][item]['status_ok']
            if status_ok is False:
                status_str = str(AsciiColors.BOLD) + str(AsciiColors.FAIL) + "ERROR"
                msg = status_dict[i][item]['msg'] + str(AsciiColors.ENDC)
            message = message + formating % (item_txt, status_str, msg)
    message += "\n"
    return message

def _check_admin_operation_credentials(username):
    exit_code = 0
    message = ""
    if username != 'admin':
        message = " ### ERROR: User '{}' is not allowed to do the operation!".format(username)
        exit_code = 1
    return exit_code, message


def clear_env_variables():
    var_list = ['https_proxy', 'HTTPS_PROXY', 'http_proxy', 'HTTP_PROXY', 'ftp_proxy', 'FTP_PROXY']
    for var in var_list:
        if var in os.environ:
            del os.environ[var]
    envs = ""
    for var in os.environ:
        envs += " {} = {}\n".format(var, os.environ[var])
    print envs

def _check_if_lab_exists_in_state_service(lab_name, lab_pool_url):
    message = ""
    snapshot_dict = {}
    query = "%s/labs?where={\"lab_name\":\"%s\"}" % (lab_pool_url, lab_name)
    lab_data = rest_client.get_labs(query, lab_pool_url)
    lab_id = None
    if lab_data[0]['_items']:
        lab_id = lab_data[0]['_items'][0]['_id']
        states = lab_data[0]['_items'][0].get('states')
        if states:
            for snap in states:
                if (snap.get('snapshot_id')):
                    snap_id = snap['snapshot_id']
                else:
                    snap_id = snap['_id']
                _id = snap['_id']
                _etag = snap['_etag']
                build_id = None
                if snap.get('build'):
                    build_id = snap.get('build').get('id')
                snapshot_dict[snap_id] = {}
                snapshot_dict[snap_id]['_id'] = _id
                snapshot_dict[snap_id]['_etag'] = _etag
                snapshot_dict[snap_id]['build_id'] = build_id
        log.debug("_check_if_lab_exists_in_state_service({}): existing snapshots '{}'".format(lab_name, snapshot_dict))
        message = "LAB_ID: '{}'".format(lab_id)
    else:
        message = "LAB_NAME '{}' does not exist in Lab State Service".format(lab_name)
    log.info("_check_if_lab_exists_in_state_service({}): lab_id:'{}', msg:'{}'".format(lab_name, lab_id, message))
    return (lab_id, snapshot_dict, message)

def _resolve_lab_type(lab_name):
    status = 1
    lab_type = ""
    message = ""
    lab = re.split(r'\d+', lab_name)[0].lower()
    if lab in DC_STORAGE_LAB_TYPE_MAP:
        lab_type = DC_STORAGE_LAB_TYPE_MAP[lab]
        status = 0
    else:
        supported = "'%s'" % ("' '".join(DC_STORAGE_LAB_TYPE_MAP))
        message = " ### ERROR: Lab name syntax not supported in DCA for '{}'. Supported lab types: {}".format(lab, supported)
    log.info("_resolve_lab_type({}): '{}' --> '{}'".format(lab_name, lab, lab_type))
    return (status, lab_type, message)

def _resolve_snapshot_data_from_dc_lab(lab_name,
                                       admin_server_username, admin_server_password,
                                       admin_server_host, admin_server_port,
                                       storage_api_url):
    status = 0
    message = ""
    snapshot_data = []
    query = "%s/storage/snapshot/%s" % (storage_api_url, lab_name)
    log.info(query)
    req = requests.get(query)
    message = message + req.text
    log.info(storage_api_url + "': {}'".format(message))
    log.debug(_gen_unit_mock(query, req.json()))
    rspjson = load_json_content(req.content)
    if 'snapshots' in rspjson:
        admin_server_host = _get_default_admin_server_host(lab_name)
        for snapshot in rspjson['snapshots']:
            snap_name = snapshot['name']
            snap_comment = snapshot['comment']
            snap_status = "available"
            snapshot_data.append([snap_name, snap_comment, snap_status,
                                  admin_server_username, admin_server_password,
                                  admin_server_host, admin_server_port])
    if 'errormsg' in rspjson:
        status = 1
        message = "### ERROR: Data Center Lab service '{}'".format(rspjson['errormsg'])
    log.info("_resolve_snapshot_data_from_dc_lab({}): snap_data:'{}', msg:'{}'".format(lab_name, snapshot_data, message))
    return (status, snapshot_data, message)

def _get_default_admin_server_host(lab_name):
    admin_server_host = ADMIN_SERVER_ACCESS_HOST_DEFAULT_FORM.format(lab_name,
                                                                     ADMIN_SERVER_ACCESS_HOST_NETWORK_DEFAULT)
    if "CLAB" in lab_name:
        try:
            viis_node = dcapi.get_lab_viis_node(lab_name)
            if viis_node != -1:
                admin_server_host = viis_node + ADMIN_SERVER_ACCESS_HOST_NETWORK_DEFAULT
        except Exception as e:
            log.exception(e)
    log.info("_get_default_admin_server_host({}):  admin_server_host -> '{}'".format(lab_name, admin_server_host))
    return admin_server_host

def _sync_lab_into_state_service(lab_data, existing_snapshots, base_url):
    status = 0
    message = ""
    err_message = ""
    labs_url = "{}/{}".format(base_url, 'labs')
    states_url = "{}/{}".format(base_url, 'states')
    lab_name, lab_id, lab_type, lab_status, snapshot_data = lab_data
    log.info("_sync_lab_into_state_service(): '{}':'{}':'{}':'{}':".format(lab_name, lab_id, lab_type, lab_status, snapshot_data))
    if lab_id is None:
        data = {'lab_name': lab_name, 'status': lab_status}
        if lab_type is not None:
            data.update({'lab_type': lab_type})
        response = requests.post(labs_url, json=data)
        log.info("POST {0} response: {1}".format(labs_url, response.text))
        log.debug(_gen_unit_mock(labs_url, response.json()))
        response.raise_for_status()
        lab_id = str(response.json()['_id'])
    for snapshot in snapshot_data:
        state_data = {"lab": lab_id,
                      "build": {"id": snapshot[1]},
                      "snapshot_status": snapshot[2],
                      "snapshot_id": snapshot[0],
                      "admin_server_access": {"username": snapshot[3], "password": snapshot[4],
                                              "host": snapshot[5], "port": snapshot[6]}}
        if snapshot[0] not in existing_snapshots:
            log.info("POST {0} request: {1}".format(states_url, state_data))
            response = requests.post(states_url, json=state_data)
            rspjson = load_json_content(response.content)
            log.debug(_gen_unit_mock(states_url, response.json()))
            log.info("POST {0} rspjson: {1}".format(states_url, rspjson))
            if '_status' in rspjson:
                status_str = _format_string(rspjson.get('_status'), AsciiColors.OKBLACK, True)
                message = message + SNAPSHOT_FORMAT % (snapshot[1], snapshot[0], status_str)
            else:
                if '_error' in rspjson:
                    err_message = str(rspjson['_error']['message']) + " code: " + str(rspjson['_error']['code'])
                    message = message + SNAPSHOT_FORMAT % (snapshot[1], "*** ERROR ***", err_message)
        else:
            status_str = _format_string("OK", AsciiColors.OKBLACK, True)
            message = message + SNAPSHOT_FORMAT % (snapshot[1], snapshot[0], status_str)
            del existing_snapshots[snapshot[0]]

    message += _remove_additional_snapshots(existing_snapshots, base_url)

    return (status, message)

def _remove_additional_snapshots(existing_snapshots, base_url):
    message = ""
    for snap in existing_snapshots:
        _id = existing_snapshots[snap]['_id']
        _etag = existing_snapshots[snap]['_etag']
        build_id = existing_snapshots[snap]['build_id']
        log.debug("_remove_additional_snapshots(): snapshot_id: '{}' build_id: '{}' _id: '{}' _etag: '{}' base_url: '{}'".format(snap, build_id, _id, _etag, base_url))
        try:
            rest_client.delete_item("states", _id, None, _etag, base_url)
            message += SNAPSHOT_FORMAT % (build_id, snap, _format_string(REMOVED_TXT, AsciiColors.OKBLACK, True))
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                debug_message = " ### ERROR: Unable to delete snapshot: snapshot_id: '{}' err_msg: '{}'".format(snap, e.message)
                log.debug(debug_message)
                message += debug_message
            else:
                log.exception(e)
                raise e
        except Exception as e:
            log.exception(e)
            raise e
    return message

