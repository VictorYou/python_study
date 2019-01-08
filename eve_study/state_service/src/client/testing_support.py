'''utils for creating test data in LSS server
'''

import logging
import requests
import time
import json
import sys
import os
import random
import re
from .rest_client import *
from .globals import *
from .dict_builder import DictionaryBuilder
from .utils import _print_out, _print_out_and_log, _format_string, load_json_content, _gen_unit_mock
from .admin import _check_admin_operation_credentials
from .lab_request import _check_lab_reservation_status

log = logging.getLogger(__name__)

def create_test_labs(lab_id=None, service_url=None, username=None, **kwargs):
    """   Creates some test labs, states and reservations into database.
    """
    _test_setup(service_url)

def create_test_snapshots(lab_name, count, service_url=None, username=None, **kwargs):
    """   Creates some test snapshots for given lab.
    """
    log.debug("CMD line params: [{}:'{}'] ".format("lab_name", lab_name))

    exit_code = 0
    status = "OK"
    status_col = AsciiColors.OKBLACK
    message = ""
    ss_message = ""
    where = "&where={\"lab_name\":\"%s\"}" % lab_name
    query = "%s/labs?%s" % (service_url, where)
    BUILD_ID_PREFIX = "netact/product/99.17.03.0."
    SNAP_STATUS = "available"

    try:
        exit_code, message = _check_admin_operation_credentials(username)
        if exit_code == 0:
            lab_data = get_labs(query, service_url)
            if lab_data[0]['_items']:
                lab_id = lab_data[0]['_items'][0]['_id']
                for i in range(count):
                    build = BUILD_ID_PREFIX + str(random.randint(0, 9999))
                    ss_id = str(random.randint(0, 9999))
                    state_data = {"lab": lab_id,
                                  "build": {"id": build},
                                  "snapshot_status": SNAP_STATUS,
                                  "snapshot_id": ss_id}
                    log.info("create_test_snapshot() POST data: {}".format(state_data))
                    response = post_resource('states', state_data, service_url, False)
                    post_status = response['_status']
                    col = AsciiColors.OKBLACK
                    issues_txt = ""
                    issues = response.get('_issues')
                    if issues is not None:
                        exit_code = 1
                        status = "ERROR"
                        status_col = AsciiColors.FAIL
                        issues_txt = ": " + str(issues)
                        issues_txt = re.sub("u'", '\'', issues_txt)
                        col = status_col
                        issues_txt = _format_string(issues_txt, col, True)
                    ss_message += "\t" + SNAPSHOT_FORMAT % (build, ss_id,
                                                            _format_string(post_status, col, True) +
                                                            issues_txt)
                message = "\n *** Operation 'create-test-snapshots' for '{}' status: {}.\n".format(lab_name,
                                                                                                   _format_string(status, status_col, True))
                message += ss_message
            else:
                message = "\n ### ERROR: Lab '{}' does not exist!\n".format(lab_name)
                exit_code = 1
    except Exception as e:
        log.exception(e)
        message = " ### ERROR: '{}'".format(e.message)
        exit_code = 1
        raise e
    finally:
        message += " Exit code: '{}'".format(exit_code)
        _print_out(message, kwargs['output_file'])
    return exit_code

def _test_setup(base_url, labs=None):
    """Create labs, states and reservations.
    :param labs: [ (<lab_name:string>, <lab_type:string>, <lab_status:string>, <state.build.id:string>, <state.snapshot_status:string>, <state.snapshot_id:string>, <reservation:boolean>), ... ]
    """
    if not labs:
        labs = [("SprintLab" + str(random.randint(0, 9999)), "sprint", "ready", [("cm_n17-5/system/3426")], "available", "3456", False),
                ##("SprintLab7777", "sprint", "ready", [("test7777")], "available", "777", False),
                ##("SprintLab8888", "sprint", "ready", [("test8888")], "ready", "888", False),
                ##("SprintLab9999", "sprint", "ready", [("test9999")], "available", "999", False),
                ("SprintLab" + str(random.randint(0, 9999)), "other", "ready", [("cm_n17-2/system/6762")], "available", "456", False),
                ("CloudLab" + str(random.randint(0, 9999)), None, "reverting_state", [("netact/product/99.17.03.0.166")], "available", "56", False),
                ("CloudLab" + str(random.randint(0, 9999)), "cloud", "ready", [("netact/product/99.17.03.0.123")], "available", "956", False),
                ("vSprint" + str(random.randint(0, 9999)), "vsprint", "state_operation_failed", ["netact/product/99.17.03.0.003", "netact/product/99.17.03.0.022", "netact/product/99.17.03.0.145"], "available", "8456", True),
                ("vSprint" + str(random.randint(0, 9999)), "vsprint", "reverting_state", ["netact/product/99.17.03.0.004", "netact/product/99.17.03.0.424", "netact/product/99.17.03.0.645"], "available", "7456", True),
                ("SprintLab" + str(random.randint(0, 9999)), "vsprint", "ready", ["netact/product/99.17.03.0.303", "netact/product/99.17.03.0.522", "netact/product/99.17.03.0.645"], "available", "22456", False),
                ("vSprint" + str(random.randint(0, 9999)), "vsprint", "ready", [("netact/product/99.17.03.0.112")], "available", "113456", False)]
    labs_url = "{}/{}".format(base_url, 'labs')
    states_url = "{}/{}".format(base_url, 'states')
    reservations_url = "{}/{}".format(base_url, 'reservations')
    for lab, _type, lab_status, builds, ss_status, ss_id, reserved in labs:
        data = {'lab_name': lab, 'status': lab_status}
        if _type is not None:
            data.update({'lab_type': _type})
        response = requests.post(labs_url, json=data)
        log.info("POST {0} response: {1}".format(labs_url, response.text))
        response.raise_for_status()
        lab_id = str(response.json()['_id'])
        for build in builds:
            state_data = {"lab": lab_id,
                          "build": {"id": build},
                          "snapshot_status": ss_status, "snapshot_id": ss_id,
                          "admin_server_access.username": ADMIN_SERVER_ACCESS_USERNAME_DEFAULT,
                          "admin_server_access.password": ADMIN_SERVER_ACCESS_PASSWORD_DEFAULT,
                          "admin_server_access.host": ADMIN_SERVER_ACCESS_HOST_DEFAULT_FORM.format(lab, ADMIN_SERVER_ACCESS_HOST_NETWORK_DEFAULT),
                          "admin_server_access.port": ADMIN_SERVER_ACCESS_PORT_DEFAULT,
                          "admin_server_access.protocol": ADMIN_SERVER_ACCESS_PROTOCOL_DEFAULT}
            log.info("POST {0} request: {1}".format(states_url, state_data))
            response = requests.post(states_url, json=state_data)
            log.info("POST {0} response: {1}".format(states_url, response.text))
            response.raise_for_status()
        if reserved:
            res_data = {"lab": lab_id, "username": "testuser"}
            response = requests.post(reservations_url, json=res_data)
            response.raise_for_status()

