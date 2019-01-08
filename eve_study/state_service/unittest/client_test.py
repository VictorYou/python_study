# TODO re-factor unit tests and this helper too

import unittest
import client
import sys
import os
import subprocess
from httmock import HTTMock, urlmatch
import mock
import json
import logging
from StringIO import StringIO
import inspect
from requests import exceptions
import time
import datetime
from types import FunctionType
import re

from client_test_helper.request_lab import *

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

username = "tester"
password = "testing"
url = "http://fakeserver/rest/api/v2"

client.lab_pool_url = url

class ClientTests(unittest.TestCase):
    mock_request_lab_OK_json_id = 0
    mock_request_lab_OK_lab_allocated_with_lab_search_query_json_id = 0
    mock_request_lab_NOK_timeout_triggers_json_id = 0
    mock_request_lab_NOK_invalid_query_json_id = 0
    mock_request_lab_NOK_timeout_no_lab_available_json_id = 0
    mock_request_lab_NOK_lab_allocated_snapshot_failed_json_id = 0
    mock_release_lab_OK_json_id = 0
    mock_release_lab_NOK_server_precondition_failure_json_id = 0
    mock_show_labs_OK_paging_json_id = 0
    mock_create_test_labs_OK_json_id = 0
    mock_preserve_state_OK_json_id = 0
    mock_preserve_state_NOK_lab_reserved_by_another_user_json_id = 0
    mock_preserve_state_NOK_snapshot_status_error_json_id = 0
    mock_admin_migrate_snapshots_OK_json_id = 0
    mock_admin_migrate_snapshots_OK_with_admin_server_access_params_json_id = 0
    mock_admin_migrate_snapshots_OK_lab_exists_and_snapshots_exist_json_id = 0
    mock_admin_migrate_snapshots_OK_additional_snapshots_exist_json_id = 0
    mock_admin_migrate_snapshots_OK_additional_snapshots_exist_with_null_snap_id_json_id = 0
    mock_admin_migrate_snapshots_NOK_additional_snapshots_remove_failure_404_json_id = 0
    mock_admin_migrate_snapshots_NOK_additional_snapshots_remove_failure_422_json_id = 0
    mock_admin_migrate_snapshots_NOK_lab_exists_but_name_syntax_not_valid_in_dca_json_id = 0
    mock_admin_remove_labs_OK_one_lab_json_id = 0
    mock_admin_remove_labs_OK_several_labs_all_OK_json_id = 0
    mock_admin_remove_labs_OK_one_lab_no_states_json_id = 0
    mock_admin_remove_labs_NOK_several_labs_one_NOK_json_id = 0
    mock_admin_remove_labs_NOK_one_lab_one_NOK_json_id = 0
    mock_admin_remove_labs_NOK_several_labs_all_NOK_json_id = 0
    mock_admin_remove_labs_NOK_lab_does_not_exist_json_id = 0
    mock_admin_remove_labs_NOK_user_not_allowed_to_remove_json_id = 0
    mock_admin_add_lab_OK_name_given_json_id = 0
    mock_admin_add_lab_OK_name_type_given_json_id = 0
    mock_admin_add_lab_OK_name_type_status_given_json_id = 0
    mock_admin_add_lab_NOK_lab_already_exists_json_id = 0
    mock_admin_add_lab_NOK_invalid_lab_type_json_id = 0
    mock_admin_add_lab_NOK_invalid_lab_status_json_id = 0
    mock_admin_add_lab_NOK_username_not_valid_json_id = 0
    mock_create_test_snapshots_OK_one_snapshot_json_id = 0
    mock_create_test_snapshots_OK_several_snapshots_json_id = 0
    mock_create_test_snapshots_NOK_wrong_username_json_id = 0
    mock_create_test_snapshots_NOK_lab_does_not_exist_json_id = 0
    mock_create_test_snapshots_NOK_some_snapshots_successful_json_id = 0
    mock_create_test_snapshots_NOK_all_snapshots_failed_json_id = 0
    mock_admin_patch_item_OK_csv_one_parameter_json_id = 0
    mock_admin_patch_item_OK_csv_several_parameters_json_id = 0
    mock_admin_patch_item_OK_json_one_parameter_json_id = 0
    mock_admin_patch_item_OK_json_several_parameters_json_id = 0
    mock_admin_patch_item_NOK_wrong_username_json_id = 0
    mock_admin_patch_item_NOK_item_does_not_exist_json_id = 0
    mock_admin_patch_item_NOK_csv_parameter_error_json_id = 0
    mock_admin_patch_item_NOK_json_parameter_error_json_id = 0
    mock_admin_data_backup_OK_json_id = 0
    mock_admin_reserve_labs_OK_one_lab_json_id = 0
    mock_admin_reserve_labs_OK_several_labs_json_id = 0
    mock_admin_reserve_labs_OK_one_lab_with_force_json_id = 0
    mock_admin_reserve_labs_OK_several_labs_with_force_json_id = 0
    mock_admin_reserve_labs_OK_one_lab_reserved_by_admin_with_force_json_id = 0
    mock_admin_reserve_labs_OK_one_lab_reserved_by_other_user_with_force_json_id = 0
    mock_admin_reserve_labs_OK_all_labs_reserved_by_other_user_with_force_json_id = 0
    mock_admin_reserve_labs_NOK_one_lab_json_id = 0
    mock_admin_reserve_labs_NOK_several_labs_one_NOK_json_id = 0
    mock_admin_reserve_labs_NOK_several_labs_all_NOK_json_id = 0
    mock_admin_reserve_labs_NOK_several_labs_one_NOK_with_force_json_id = 0
    mock_admin_reserve_labs_NOK_several_labs_all_NOK_with_force_json_id = 0
    mock_admin_reserve_labs_NOK_lab_does_not_exist_json_id = 0
    mock_admin_reserve_labs_NOK_user_not_allowed_to_reserve_json_id = 0
    mock_admin_reserve_labs_NOK_lab_already_reserved_json_id = 0
    mock_admin_reserve_labs_NOK_exception_json_id = 0
    mock_admin_remove_snapshots_OK_one_snapshot_json_id = 0
    mock_admin_remove_snapshots_OK_several_snapshots_json_id = 0
    mock_admin_remove_snapshots_OK_one_snapshot_with_force_json_id = 0
    mock_admin_remove_snapshots_OK_several_snapshots_with_force_json_id = 0
    mock_admin_remove_snapshots_NOK_several_snapshots_one_NOK_json_id = 0
    mock_admin_remove_snapshots_NOK_several_snapshots_all_NOK_json_id = 0
    mock_admin_remove_snapshots_NOK_several_snapshots_one_NOK_with_force_json_id = 0
    mock_admin_remove_snapshots_NOK_several_snapshots_all_NOK_with_force_json_id = 0
    mock_admin_remove_snapshots_NOK_lab_does_not_exist_json_id = 0
    mock_admin_remove_snapshots_NOK_user_not_allowed_to_remove_json_id = 0
    mock_admin_remove_snapshots_NOK_lab_already_reserved_json_id = 0
    mock_admin_remove_snapshots_NOK_operation_cancelled_in_question_json_id = 0
    mock_show_admin_server_access_data_ok_no_data_all_labs_json_id = 0
    mock_show_admin_server_access_data_nok_no_data_one_lab_json_id = 0
    mock_show_admin_server_access_data_nok_no_data_one_lab_with_snap_json_id = 0
    mock_show_admin_server_access_data_ok_only_lab_data_all_labs_json_id = 0
    mock_show_admin_server_access_data_ok_only_lab_data_one_lab_json_id = 0
    mock_show_admin_server_access_data_nok_only_lab_data_one_lab_with_snap_json_id = 0
    mock_show_admin_server_access_data_ok_one_lab_data_snaps_empty_json_id = 0
    mock_show_admin_server_access_data_ok_one_lab_data_one_snaps_json_id = 0
    mock_show_admin_server_access_data_ok_one_lab_data_several_snaps_json_id = 0
    mock_show_admin_server_access_data_ok_mass_labs_data_json_id = 0
    mock_show_snapshot_OK_one_snapshot_unavailable_data_json_id = 0

    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()
        self.held, sys.stderr = sys.stderr, StringIO()
        pass

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|states|reser).*')
    def mock_api_create_labs_OK(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        content = {}
        log.debug("### mock_create_test_labs_OK_json_id = {}".format(self.mock_create_test_labs_OK_json_id))
        if self.mock_create_test_labs_OK_json_id == 0:
            content = json.dumps({"_updated": "Fri, 21 Apr 2017 11:02:30 GMT", "_links": {"self": {"href": "labs/58f9e6c60d0b9f00019e0dec", "title": "Lab"}}, "_created": "Fri, 21 Apr 2017 11:02:30 GMT", "_status": "OK", "_id": "58f9e6c60d0b9f00019e0dec", "_etag": "d388765dfa88a58057b5878bac5711f7b879b300"})
        elif self.mock_create_test_labs_OK_json_id == 1:
            content = json.dumps({"_updated": "Fri, 21 Apr 2017 11:02:30 GMT", "_links": {"self": {"href": "states/58f9e6c60d0b9f00019e0ded", "title": "State"}}, "_created": "Fri, 21 Apr 2017 11:02:30 GMT", "_status": "OK", "_id": "58f9e6c60d0b9f00019e0ded", "_etag": "febced723874e008974d50deee4c7b548adcc768"})
        elif self.mock_create_test_labs_OK_json_id == 2:
            content = json.dumps({"_updated": "Fri, 21 Apr 2017 11:02:31 GMT", "_links": {"self": {"href": "labs/58f9e6c70d0b9f00019e0dee", "title": "Lab"}}, "_created": "Fri, 21 Apr 2017 11:02:31 GMT", "_status": "OK", "_id": "58f9e6c70d0b9f00019e0dee", "_etag": "b0ae876f394d3ee00e5eef767cb6d9f33c9e5257"})
        elif self.mock_create_test_labs_OK_json_id == 3:
            content = json.dumps({"_updated": "Fri, 21 Apr 2017 11:02:31 GMT", "_links": {"self": {"href": "states/58f9e6c70d0b9f00019e0def", "title": "State"}}, "_created": "Fri, 21 Apr 2017 11:02:31 GMT", "_status": "OK", "_id": "58f9e6c70d0b9f00019e0def", "_etag": "6493ba1153376ab335ae26bb1b0332b9c66899dd"})
        elif self.mock_create_test_labs_OK_json_id == 4:
            content = json.dumps({"_updated": "Fri, 21 Apr 2017 11:02:31 GMT", "_links": {"self": {"href": "labs/58f9e6c70d0b9f00019e0df0", "title": "Lab"}}, "_created": "Fri, 21 Apr 2017 11:02:31 GMT", "_status": "OK", "_id": "58f9e6c70d0b9f00019e0df0", "_etag": "03b241985b47ee19ed783064d47acc78a6b6da02"})
        elif self.mock_create_test_labs_OK_json_id == 5:
            content = json.dumps({"_updated": "Fri, 21 Apr 2017 11:02:31 GMT", "_links": {"self": {"href": "states/58f9e6c70d0b9f00019e0df1", "title": "State"}}, "_created": "Fri, 21 Apr 2017 11:02:31 GMT", "_status": "OK", "_id": "58f9e6c70d0b9f00019e0df1", "_etag": "08a949e8563d5933f6fd955c80c371fa3a838fe2"})
        elif self.mock_create_test_labs_OK_json_id == 6:
            content = json.dumps({"_updated": "Fri, 21 Apr 2017 11:02:31 GMT", "_links": {"self": {"href": "labs/58f9e6c70d0b9f00019e0df2", "title": "Lab"}}, "_created": "Fri, 21 Apr 2017 11:02:31 GMT", "_status": "OK", "_id": "58f9e6c70d0b9f00019e0df2", "_etag": "96ef0047683a0278aec29cd43bd74b0e67b9010b"})
        elif self.mock_create_test_labs_OK_json_id == 7:
            content = json.dumps({"_updated": "Fri, 21 Apr 2017 11:02:31 GMT", "_links": {"self": {"href": "states/58f9e6c70d0b9f00019e0df3", "title": "State"}}, "_created": "Fri, 21 Apr 2017 11:02:31 GMT", "_status": "OK", "_id": "58f9e6c70d0b9f00019e0df3", "_etag": "335a4380aa361c215c44945e7fd3967226866c78"})
        elif self.mock_create_test_labs_OK_json_id == 8:
            content = json.dumps({"_updated": "Fri, 21 Apr 2017 11:02:31 GMT", "_links": {"self": {"href": "labs/58f9e6c70d0b9f00019e0df4", "title": "Lab"}}, "_created": "Fri, 21 Apr 2017 11:02:31 GMT", "_status": "OK", "_id": "58f9e6c70d0b9f00019e0df4", "_etag": "76a539e8e20f66d263482a5d0b4e017c3eb6c004"})
        elif self.mock_create_test_labs_OK_json_id == 9:
            content = json.dumps({"_updated": "Fri, 21 Apr 2017 11:02:31 GMT", "_links": {"self": {"href": "states/58f9e6c70d0b9f00019e0df5", "title": "State"}}, "_created": "Fri, 21 Apr 2017 11:02:31 GMT", "_status": "OK", "_id": "58f9e6c70d0b9f00019e0df5", "_etag": "e2480ed5ee69996572f91797d06088d3b0b0a8dc"})
        elif self.mock_create_test_labs_OK_json_id == 10:
            content = json.dumps({"_updated": "Fri, 21 Apr 2017 11:02:31 GMT", "_links": {"self": {"href": "states/58f9e6c70d0b9f00019e0df6", "title": "State"}}, "_created": "Fri, 21 Apr 2017 11:02:31 GMT", "_status": "OK", "_id": "58f9e6c70d0b9f00019e0df6", "_etag": "ca20d1fa2f61deb7788a960b1daf765225006cf3"})
        elif self.mock_create_test_labs_OK_json_id == 11:
            content = json.dumps({"_updated": "Fri, 21 Apr 2017 11:02:31 GMT", "_links": {"self": {"href": "states/58f9e6c70d0b9f00019e0df7", "title": "State"}}, "_created": "Fri, 21 Apr 2017 11:02:31 GMT", "_status": "OK", "_id": "58f9e6c70d0b9f00019e0df7", "_etag": "e76ae270d19cfb21b968c714f643b95f24ddd435"})
        elif self.mock_create_test_labs_OK_json_id == 12:
            content = json.dumps({"_updated": "Fri, 21 Apr 2017 11:02:31 GMT", "_links": {"self": {"href": "labs/58f9e6c70d0b9f00019e0df9", "title": "Lab"}}, "_created": "Fri, 21 Apr 2017 11:02:31 GMT", "_status": "OK", "_id": "58f9e6c70d0b9f00019e0df9", "_etag": "94afe5e544dd250a00a90927a64677b1a1547de5"})
        elif self.mock_create_test_labs_OK_json_id == 13:
            content = json.dumps({"_updated": "Fri, 21 Apr 2017 11:02:31 GMT", "_links": {"self": {"href": "states/58f9e6c70d0b9f00019e0dfa", "title": "State"}}, "_created": "Fri, 21 Apr 2017 11:02:31 GMT", "_status": "OK", "_id": "58f9e6c70d0b9f00019e0dfa", "_etag": "9dcdc969eaba6ef4af249f89ad749cf80331f852"})
        elif self.mock_create_test_labs_OK_json_id == 14:
            content = json.dumps({"_updated": "Fri, 21 Apr 2017 11:02:31 GMT", "_links": {"self": {"href": "states/58f9e6c70d0b9f00019e0dfb", "title": "State"}}, "_created": "Fri, 21 Apr 2017 11:02:31 GMT", "_status": "OK", "_id": "58f9e6c70d0b9f00019e0dfb", "_etag": "f650474a051543f91f0f644a8f4fa19d5bd63b70"})
        elif self.mock_create_test_labs_OK_json_id == 15:
            content = json.dumps({"_updated": "Fri, 21 Apr 2017 11:02:31 GMT", "_links": {"self": {"href": "states/58f9e6c70d0b9f00019e0dfc", "title": "State"}}, "_created": "Fri, 21 Apr 2017 11:02:31 GMT", "_status": "OK", "_id": "58f9e6c70d0b9f00019e0dfc", "_etag": "a59b1b2d64ff21c14be8066c6ff7b89ad3399b64"})
        elif self.mock_create_test_labs_OK_json_id == 16:
            content = json.dumps({"_updated": "Fri, 21 Apr 2017 11:02:31 GMT", "_links": {"self": {"href": "labs/58f9e6c70d0b9f00019e0dfe", "title": "Lab"}}, "_created": "Fri, 21 Apr 2017 11:02:31 GMT", "_status": "OK", "_id": "58f9e6c70d0b9f00019e0dfe", "_etag": "7f990c786b4abb1d2ad3c0ad894f9d63ffe290d1"})
        elif self.mock_create_test_labs_OK_json_id == 17:
            content = json.dumps({"_updated": "Fri, 21 Apr 2017 11:02:31 GMT", "_links": {"self": {"href": "states/58f9e6c70d0b9f00019e0dff", "title": "State"}}, "_created": "Fri, 21 Apr 2017 11:02:31 GMT", "_status": "OK", "_id": "58f9e6c70d0b9f00019e0dff", "_etag": "3d63638183d5b9b4ea184eb1806259c352ff8dd1"})
        elif self.mock_create_test_labs_OK_json_id == 18:
            content = json.dumps({"_updated": "Fri, 21 Apr 2017 11:02:31 GMT", "_links": {"self": {"href": "states/58f9e6c70d0b9f00019e0e00", "title": "State"}}, "_created": "Fri, 21 Apr 2017 11:02:31 GMT", "_status": "OK", "_id": "58f9e6c70d0b9f00019e0e00", "_etag": "9473b966f289c82dd08ee3514679ae25581fad0f"})
        elif self.mock_create_test_labs_OK_json_id == 19:
            content = json.dumps({"_updated": "Fri, 21 Apr 2017 11:02:31 GMT", "_links": {"self": {"href": "states/58f9e6c70d0b9f00019e0e01", "title": "State"}}, "_created": "Fri, 21 Apr 2017 11:02:31 GMT", "_status": "OK", "_id": "58f9e6c70d0b9f00019e0e01", "_etag": "2d39ff24bd3bca1534516127153cdf2f7de104e3"})
        elif self.mock_create_test_labs_OK_json_id == 20:
            content = json.dumps({"_updated": "Fri, 21 Apr 2017 11:02:31 GMT", "_links": {"self": {"href": "labs/58f9e6c70d0b9f00019e0e02", "title": "Lab"}}, "_created": "Fri, 21 Apr 2017 11:02:31 GMT", "_status": "OK", "_id": "58f9e6c70d0b9f00019e0e02", "_etag": "911b01b950a3f351519db22f5a0252a9096cf0dd"})
        elif self.mock_create_test_labs_OK_json_id == 21:
            content = json.dumps({"_updated": "Fri, 21 Apr 2017 11:02:31 GMT", "_links": {"self": {"href": "states/58f9e6c70d0b9f00019e0e03", "title": "State"}}, "_created": "Fri, 21 Apr 2017 11:02:31 GMT", "_status": "OK", "_id": "58f9e6c70d0b9f00019e0e03", "_etag": "d506f8fa4f1760c3c4644c292ce1d0337e767149"})
        elif self.mock_create_test_labs_OK_json_id == 22:
            content = json.dumps({"_updated": "Fri, 21 Apr 2017 11:02:31 GMT", "_links": {"self": {"href": "labs/58f9e6c70d0b9f00019e0dfe", "title": "Lab"}}, "_created": "Fri, 21 Apr 2017 11:02:31 GMT", "_status": "OK", "_id": "58f9e6c70d0b9f00019e0dfe", "_etag": "7f990c786b4abb1d2ad3c0ad894f9d63ffe290d1"})
        elif self.mock_create_test_labs_OK_json_id == 23:
            content = json.dumps({"_updated": "Fri, 21 Apr 2017 11:02:31 GMT", "_links": {"self": {"href": "states/58f9e6c70d0b9f00019e0dff", "title": "State"}}, "_created": "Fri, 21 Apr 2017 11:02:31 GMT", "_status": "OK", "_id": "58f9e6c70d0b9f00019e0dff", "_etag": "3d63638183d5b9b4ea184eb1806259c352ff8dd1"})
        elif self.mock_create_test_labs_OK_json_id == 24:
            content = json.dumps({"_updated": "Fri, 21 Apr 2017 11:02:31 GMT", "_links": {"self": {"href": "states/58f9e6c70d0b9f00019e0e00", "title": "State"}}, "_created": "Fri, 21 Apr 2017 11:02:31 GMT", "_status": "OK", "_id": "58f9e6c70d0b9f00019e0e00", "_etag": "9473b966f289c82dd08ee3514679ae25581fad0f"})

        self.mock_create_test_labs_OK_json_id += 1



        return {'status_code': 200,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }


    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*schema.*')
    def mock_api_show_schema_OK(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        content = json.dumps({u'labs': {u'status': {u'default': u'queued_for_initialization', u'type': u'string', u'allowed': [u'reverting_state', u'preserving_state', u'state_operation_failed', u'queued_for_initialization', u'queued_for_revert', u'initializing', u'ready']}, u'previously_reverted_state': {u'type': u'objectid', u'data_relation': {u'field': u'_id', u'resource': u'states', u'embeddable': True}}, u'lab_type': {u'type': u'string', u'allowed': [u'sprint', u'vsprint', u'cloud', u'other']}, u'states': {u'type': u'list', u'schema': {u'type': u'objectid', u'data_relation': {u'field': u'_id', u'resource': u'states', u'embeddable': True}}}, u'lab_name': {u'unique': True, u'type': u'string', u'empty': False, u'required': True}, u'reservation': {u'unique': True, u'type': u'objectid', u'data_relation': {u'field': u'_id', u'resource': u'reservations', u'embeddable': True}, u'nullable': True}, u'_id': {u'type': u'objectid'}}, u'states': {u'lab': {u'required': True, u'type': u'objectid', u'data_relation': {u'field': u'_id', u'resource': u'labs', u'embeddable': True}}, u'build_history': {u'type': u'list'}, u'integrated_nes': {u'type': u'list'}, u'build': {u'required': True, u'type': u'dict', u'schema': {u'nick_name': {u'type': u'string'}, u'id': {u'required': True, u'type': u'string'}}}, u'snapshot_id': {u'dependencies': [u'snapshot_status'], u'type': u'string'}, u'_id': {u'type': u'objectid'}, u'snapshot_status': {u'default': u'queued', u'type': u'string', u'allowed': [u'queued', u'creating', u'available', u'failed']}}, u'labrequests': {u'username': {u'required': True, u'type': u'string'}, u'status': {u'default': u'pending', u'type': u'string', u'allowed': [u'pending', u'no_matching_state', u'no_matching_lab', u'no_lab_available', u'error', u'ready']}, u'group': {u'type': u'string'}, u'expireAt': {u'readonly': True, u'type': u'datetime'}, u'lab_reservation_time': {u'default': u'60', u'type': u'string'}, u'lab': {u'type': u'objectid', u'data_relation': {u'field': u'_id', u'resource': u'labs', u'embeddable': True}}, u'state_search_query': {u'required': True, u'type': u'string'}, u'message': {u'type': u'string'}, u'_id': {u'type': u'objectid'}, u'lab_search_query': {u'type': u'string'}}, u'reservations': {u'username': {u'required': True, u'type': u'string'}, u'message': {u'type': u'string'}, u'_id': {u'type': u'objectid'}, u'expireAt': {u'type': u'datetime'}, u'lab': {u'unique': True, u'type': u'objectid', u'data_relation': {u'field': u'_id', u'resource': u'labs', u'embeddable': True}, u'empty': False, u'required': True}}})
        return {'status_code': 200,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*labs.*')
    def mock_api_labs_OK(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        content = json.dumps({u'_items': [{u'status': u'queued_for_initialization', u'_updated': u'Mon, 27 Mar 2017 08:07:28 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 27 Mar 2017 08:07:28 GMT', u'lab': u'58d8c8401df07900010ddd7b', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'_created': u'Mon, 27 Mar 2017 08:07:28 GMT', u'_id': u'58d8c8401df07900010ddd7c', u'_etag': u'65f1f79c1d1d89638a863f683947ad636a2ae565', u'snapshot_status': u'queued', u'admin_server_access': {u'host': u'sprintlab302vm1.netact.nsn-rdnet.net', u'password': u'admin', u'port': 22}}], u'lab_name': u'CloudLab572', u'_links': {u'self': {u'href': u'labs/58d8c8401df07900010ddd7b', u'title': u'Lab'}}, u'_created': u'Mon, 27 Mar 2017 08:07:28 GMT', u'reservation': None, u'_id': u'58d8c8401df07900010ddd7b', u'_etag': u'1eda13f01637ef17a3a682526e28ce568dc4f1f5'}, {u'status': u'queued_for_initialization', u'_updated': u'Mon, 27 Mar 2017 08:07:28 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 27 Mar 2017 08:07:28 GMT', u'lab': u'58d8c8401df07900010ddd7b', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'_created': u'Mon, 27 Mar 2017 08:07:28 GMT', u'_id': u'58d8c8401df07900010ddd7c', u'_etag': u'65f1f79c1d1d89638a863f683947ad636a2ae565', u'snapshot_status': u'queued', u'admin_server_access': {u'username': u'root', u'host': u'sprintlab302vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'port': 22}}], u'lab_name': u'CloudLab472', u'_links': {u'self': {u'href': u'labs/58d8c8401df07900010ddd7b', u'title': u'Lab'}}, u'_created': u'Mon, 27 Mar 2017 08:07:28 GMT', u'_id': u'58d8c8401df07900010ddd7b', u'_etag': u'1eda13f01637ef17a3a682526e28ce568dc4f1f5'}, {u'status': u'queued_for_initialization', u'_updated': u'Mon, 27 Mar 2017 08:07:28 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 27 Mar 2017 08:07:28 GMT', u'lab': u'58d8c8401df07900010ddd7b', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'_created': u'Mon, 27 Mar 2017 08:07:28 GMT', u'_id': u'58d8c8401df07900010ddd7c', u'_etag': u'65f1f79c1d1d89638a863f683947ad636a2ae565', u'snapshot_status': u'queued'}], u'lab_name': u'CloudLab1247', u'_links': {u'self': {u'href': u'labs/58d8c8401df07900010ddd7b', u'title': u'Lab'}}, u'_created': u'Mon, 27 Mar 2017 08:07:28 GMT', u'reservation': {u'username': u'taako', u'_updated': u'Wed, 29 Mar 2017 12:29:25 GMT', u'lab': u'58d8c8401df07900010ddd7b', u'_created': u'Wed, 29 Mar 2017 12:29:25 GMT', u'message': u'NA17_2 to NA17_5 upgrade tefst', u'_id': u'58dba8a51df07900010dddd2', u'_etag': u'7a6938ed3b6096acac46123cd4db61a7f640dbb0'}, u'_id': u'58d8c8401df07900010ddd7b', u'_etag': u'1eda13f01637ef17a3a682526e28ce568dc4f1f5'}, {u'status': u'queued_for_initialization', u'_updated': u'Mon, 27 Mar 2017 08:07:28 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 27 Mar 2017 08:07:28 GMT', u'lab': u'58d8c8401df07900010ddd7b', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'_created': u'Mon, 27 Mar 2017 08:07:28 GMT', u'_id': u'58d8c8401df07900010ddd7c', u'_etag': u'65f1f79c1d1d89638a863f683947ad636a2ae565', u'snapshot_status': u'queued'}], u'lab_name': u'CloudLab247', u'_links': {u'self': {u'href': u'labs/58d8c8401df07900010ddd7b', u'title': u'Lab'}}, u'_created': u'Mon, 27 Mar 2017 08:07:28 GMT', u'reservation': {u'username': u'taako', u'_updated': u'Wed, 29 Mar 2017 12:29:25 GMT', u'lab': u'58d8c8401df07900010ddd7b', u'_created': u'Wed, 29 Mar 2017 12:29:25 GMT', u'message': u'NA17_2 to NA17_5 upgrade tefst', u'_id': u'58dba8a51df07900010dddd2', u'_etag': u'7a6938ed3b6096acac46123cd4db61a7f640dbb0'}, u'_id': u'58d8c8401df07900010ddd7b', u'_etag': u'1eda13f01637ef17a3a682526e28ce568dc4f1f5'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab247"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
        return {'status_code': 200,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*labs.*')
    def mock_api_labs_OK_paging_case(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        content = {}
        log.debug("### mock_show_lab_OK_paging_json_id = {}".format(self.mock_show_labs_OK_paging_json_id))
        if self.mock_show_labs_OK_paging_json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'queued_for_initialization', u'_updated': u'Mon, 27 Mar 2017 08:07:28 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 27 Mar 2017 08:07:28 GMT', u'lab': u'58d8c8401df07900010ddd7b', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'_created': u'Mon, 27 Mar 2017 08:07:28 GMT', u'_id': u'58d8c8401df07900010ddd7c', u'_etag': u'65f1f79c1d1d89638a863f683947ad636a2ae565', u'snapshot_status': u'queued'}], u'lab_name': u'CloudLab572', u'_links': {u'self': {u'href': u'labs/58d8c8401df07900010ddd7b', u'title': u'Lab'}}, u'_created': u'Mon, 27 Mar 2017 08:07:28 GMT', u'reservation': None, u'_id': u'58d8c8401df07900010ddd7b', u'_etag': u'1eda13f01637ef17a3a682526e28ce568dc4f1f5'}, {u'status': u'queued_for_initialization', u'_updated': u'Mon, 27 Mar 2017 08:07:28 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 27 Mar 2017 08:07:28 GMT', u'lab': u'58d8c8401df07900010ddd7b', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'_created': u'Mon, 27 Mar 2017 08:07:28 GMT', u'_id': u'58d8c8401df07900010ddd7c', u'_etag': u'65f1f79c1d1d89638a863f683947ad636a2ae565', u'snapshot_status': u'queued'}], u'lab_name': u'CloudLab472', u'_links': {u'self': {u'href': u'labs/58d8c8401df07900010ddd7b', u'title': u'Lab'}}, u'_created': u'Mon, 27 Mar 2017 08:07:28 GMT', u'_id': u'58d8c8401df07900010ddd7b', u'_etag': u'1eda13f01637ef17a3a682526e28ce568dc4f1f5'}, {u'status': u'queued_for_initialization', u'_updated': u'Mon, 27 Mar 2017 08:07:28 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 27 Mar 2017 08:07:28 GMT', u'lab': u'58d8c8401df07900010ddd7b', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'_created': u'Mon, 27 Mar 2017 08:07:28 GMT', u'_id': u'58d8c8401df07900010ddd7c', u'_etag': u'65f1f79c1d1d89638a863f683947ad636a2ae565', u'snapshot_status': u'queued'}], u'lab_name': u'CloudLab1247', u'_links': {u'self': {u'href': u'labs/58d8c8401df07900010ddd7b', u'title': u'Lab'}}, u'_created': u'Mon, 27 Mar 2017 08:07:28 GMT', u'reservation': {u'username': u'taako', u'_updated': u'Wed, 29 Mar 2017 12:29:25 GMT', u'lab': u'58d8c8401df07900010ddd7b', u'_created': u'Wed, 29 Mar 2017 12:29:25 GMT', u'message': u'NA17_2 to NA17_5 upgrade tefst', u'_id': u'58dba8a51df07900010dddd2', u'_etag': u'7a6938ed3b6096acac46123cd4db61a7f640dbb0'}, u'_id': u'58d8c8401df07900010ddd7b', u'_etag': u'1eda13f01637ef17a3a682526e28ce568dc4f1f5'}, {u'status': u'queued_for_initialization', u'_updated': u'Mon, 27 Mar 2017 08:07:28 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 27 Mar 2017 08:07:28 GMT', u'lab': u'58d8c8401df07900010ddd7b', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'_created': u'Mon, 27 Mar 2017 08:07:28 GMT', u'_id': u'58d8c8401df07900010ddd7c', u'_etag': u'65f1f79c1d1d89638a863f683947ad636a2ae565', u'snapshot_status': u'queued'}], u'lab_name': u'CloudLab247', u'_links': {u'self': {u'href': u'labs/58d8c8401df07900010ddd7b', u'title': u'Lab'}}, u'_created': u'Mon, 27 Mar 2017 08:07:28 GMT', u'reservation': {u'username': u'taako', u'_updated': u'Wed, 29 Mar 2017 12:29:25 GMT', u'lab': u'58d8c8401df07900010ddd7b', u'_created': u'Wed, 29 Mar 2017 12:29:25 GMT', u'message': u'NA17_2 to NA17_5 upgrade tefst', u'_id': u'58dba8a51df07900010dddd2', u'_etag': u'7a6938ed3b6096acac46123cd4db61a7f640dbb0'}, u'_id': u'58d8c8401df07900010ddd7b', u'_etag': u'1eda13f01637ef17a3a682526e28ce568dc4f1f5'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab247"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}, u'next': {u'href': u'labs?page=2', u'title': u'next page'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
        elif self.mock_show_labs_OK_paging_json_id == 1:
                    content = json.dumps({u'_items': [{u'status': u'queued_for_initialization', u'_updated': u'Mon, 27 Mar 2017 08:07:28 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 27 Mar 2017 08:07:28 GMT', u'lab': u'58d8c8401df07900010ddd7b', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'_created': u'Mon, 27 Mar 2017 08:07:28 GMT', u'_id': u'58d8c8401df07900010ddd7c', u'_etag': u'65f1f79c1d1d89638a863f683947ad636a2ae565', u'snapshot_status': u'queued'}], u'lab_name': u'CloudLab1572', u'_links': {u'self': {u'href': u'labs/58d8c8401df07900010ddd7b', u'title': u'Lab'}}, u'_created': u'Mon, 27 Mar 2017 08:07:28 GMT', u'reservation': None, u'_id': u'58d8c8401df07900010ddd7b', u'_etag': u'1eda13f01637ef17a3a682526e28ce568dc4f1f5'}, {u'status': u'queued_for_initialization', u'_updated': u'Mon, 27 Mar 2017 08:07:28 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 27 Mar 2017 08:07:28 GMT', u'lab': u'58d8c8401df07900010ddd7b', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'_created': u'Mon, 27 Mar 2017 08:07:28 GMT', u'_id': u'58d8c8401df07900010ddd7c', u'_etag': u'65f1f79c1d1d89638a863f683947ad636a2ae565', u'snapshot_status': u'queued'}], u'lab_name': u'CloudLab3472', u'_links': {u'self': {u'href': u'labs/58d8c8401df07900010ddd7b', u'title': u'Lab'}}, u'_created': u'Mon, 27 Mar 2017 08:07:28 GMT', u'_id': u'58d8c8401df07900010ddd7b', u'_etag': u'1eda13f01637ef17a3a682526e28ce568dc4f1f5'}, {u'status': u'queued_for_initialization', u'_updated': u'Mon, 27 Mar 2017 08:07:28 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 27 Mar 2017 08:07:28 GMT', u'lab': u'58d8c8401df07900010ddd7b', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'_created': u'Mon, 27 Mar 2017 08:07:28 GMT', u'_id': u'58d8c8401df07900010ddd7c', u'_etag': u'65f1f79c1d1d89638a863f683947ad636a2ae565', u'snapshot_status': u'queued'}], u'lab_name': u'CloudLab61247', u'_links': {u'self': {u'href': u'labs/58d8c8401df07900010ddd7b', u'title': u'Lab'}}, u'_created': u'Mon, 27 Mar 2017 08:07:28 GMT', u'reservation': {u'username': u'taako', u'_updated': u'Wed, 29 Mar 2017 12:29:25 GMT', u'lab': u'58d8c8401df07900010ddd7b', u'_created': u'Wed, 29 Mar 2017 12:29:25 GMT', u'message': u'NA17_2 to NA17_5 upgrade tefst', u'_id': u'58dba8a51df07900010dddd2', u'_etag': u'7a6938ed3b6096acac46123cd4db61a7f640dbb0'}, u'_id': u'58d8c8401df07900010ddd7b', u'_etag': u'1eda13f01637ef17a3a682526e28ce568dc4f1f5'}, {u'status': u'queued_for_initialization', u'_updated': u'Mon, 27 Mar 2017 08:07:28 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 27 Mar 2017 08:07:28 GMT', u'lab': u'58d8c8401df07900010ddd7b', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'_created': u'Mon, 27 Mar 2017 08:07:28 GMT', u'_id': u'58d8c8401df07900010ddd7c', u'_etag': u'65f1f79c1d1d89638a863f683947ad636a2ae565', u'snapshot_status': u'queued'}], u'lab_name': u'CloudLab2247', u'_links': {u'self': {u'href': u'labs/58d8c8401df07900010ddd7b', u'title': u'Lab'}}, u'_created': u'Mon, 27 Mar 2017 08:07:28 GMT', u'reservation': {u'username': u'taako', u'_updated': u'Wed, 29 Mar 2017 12:29:25 GMT', u'lab': u'58d8c8401df07900010ddd7b', u'_created': u'Wed, 29 Mar 2017 12:29:25 GMT', u'message': u'NA17_2 to NA17_5 upgrade tefst', u'_id': u'58dba8a51df07900010dddd2', u'_etag': u'7a6938ed3b6096acac46123cd4db61a7f640dbb0'}, u'_id': u'58d8c8401df07900010ddd7b', u'_etag': u'1eda13f01637ef17a3a682526e28ce568dc4f1f5'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab247"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
        self.mock_show_labs_OK_paging_json_id += 1
        return {'status_code': 200,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*labs.*')
    def mock_api_labs_OK_reservation_null(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        content = json.dumps({u'_items': [{u'status': u'queued_for_initialization', u'_updated': u'Mon, 27 Mar 2017 08:07:28 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 27 Mar 2017 08:07:28 GMT', u'lab': u'58d8c8401df07900010ddd7b', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'_created': u'Mon, 27 Mar 2017 08:07:28 GMT', u'_id': u'58d8c8401df07900010ddd7c', u'_etag': u'65f1f79c1d1d89638a863f683947ad636a2ae565', u'snapshot_status': u'queued'}], u'lab_name': u'CloudLab1247', u'_links': {u'self': {u'href': u'labs/58d8c8401df07900010ddd7b', u'title': u'Lab'}}, u'_created': u'Mon, 27 Mar 2017 08:07:28 GMT', u'reservation': {}, u'_id': u'58d8c8401df07900010ddd7b', u'_etag': u'1eda13f01637ef17a3a682526e28ce568dc4f1f5'}, {u'status': u'queued_for_initialization', u'_updated': u'Mon, 27 Mar 2017 08:07:28 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 27 Mar 2017 08:07:28 GMT', u'lab': u'58d8c8401df07900010ddd7b', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'_created': u'Mon, 27 Mar 2017 08:07:28 GMT', u'_id': u'58d8c8401df07900010ddd7c', u'_etag': u'65f1f79c1d1d89638a863f683947ad636a2ae565', u'snapshot_status': u'queued'}], u'lab_name': u'CloudLab247', u'_links': {u'self': {u'href': u'labs/58d8c8401df07900010ddd7b', u'title': u'Lab'}}, u'_created': u'Mon, 27 Mar 2017 08:07:28 GMT', u'reservation': {u'username': u'taako', u'_updated': u'Wed, 29 Mar 2017 12:29:25 GMT', u'lab': u'58d8c8401df07900010ddd7b', u'_created': u'Wed, 29 Mar 2017 12:29:25 GMT', u'message': u'NA17_2 to NA17_5 upgrade tefst', u'_id': u'58dba8a51df07900010dddd2', u'_etag': u'7a6938ed3b6096acac46123cd4db61a7f640dbb0'}, u'_id': u'58d8c8401df07900010ddd7b', u'_etag': u'1eda13f01637ef17a3a682526e28ce568dc4f1f5'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab247"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
        return {'status_code': 200,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*labs.*')
    def mock_api_labs_NOK_lab_not_found(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        content = json.dumps({u'_items': [], u'_links': {u'self': {u'href': u'labs', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 0, u'page': 1}})
        return {'status_code': 200,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*labs.*')
    def mock_api_release_lab_NOK_lab_not_found(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        content = json.dumps({u'_items': [], u'_links': {u'self': {u'href': u'labs', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 0, u'page': 1}})
        return {'status_code': 200,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*labs.*')
    def mock_api_release_lab_NOK_lab_is_not_reserved(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        content = json.dumps({u'_items': [{u'status': u'queued_for_initialization', u'_updated': u'Tue, 04 Apr 2017 14:01:39 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Tue, 04 Apr 2017 14:01:39 GMT', u'lab': u'58e3a7431df07900010ddea4', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'_created': u'Tue, 04 Apr 2017 14:01:39 GMT', u'_id': u'58e3a7431df07900010ddea5', u'_etag': u'3326a469c4f2bb46abcda4db8b5849a93e89505b', u'snapshot_status': u'queued'}], u'lab_name': u'CloudLab133', u'_links': {u'self': {u'href': u'labs/58e3a7431df07900010ddea4', u'title': u'Lab'}}, u'_created': u'Tue, 04 Apr 2017 14:01:39 GMT', u'_id': u'58e3a7431df07900010ddea4', u'_etag': u'acbec92ec7e59b535379eed63e4f48fa0196a0d6'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab133"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
        return {'status_code': 200,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakelss.*', path=r'.*lab.*')
    def mock_request_lab_wait_for_free_success(self, url, request):
        ''' mocked sequence where requested lab is reserved in beginning, but will be free after some time '''
        self.request_lab_wait_for_free_success_id = getattr(self, 'request_lab_wait_for_free_success_id', 0)
        log.debug("MOCK FUNCTION: {} ID: {} URL {}".format(inspect.stack()[0][3], self.request_lab_wait_for_free_success_id, url))

        # -> keepalive requests always OK, other ones by list
        if re.search('/keepalive', url.path):
            content = REQUEST_LAB_WAIT_FOR_FREE_SUCCESS['keepalive'][0]
            log.debug('keepalive \t%4.4u %s' % (self.request_lab_wait_for_free_success_id, content)) 
        else:
            content = REQUEST_LAB_WAIT_FOR_FREE_SUCCESS['responses'][self.request_lab_wait_for_free_success_id]
            log.debug('\t%4.4u %s' % (self.request_lab_wait_for_free_success_id, content)) 
            self.request_lab_wait_for_free_success_id += 1
        return {'status_code': 200,
                'content': json.dumps(content),
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakelss.*', path=r'.*lab.*')
    def mock_request_for_free_lab(self, url, request):
        ''' mocked sequence where requested lab is not reserved '''
        self.request_for_free_lab_id = getattr(self, 'request_for_free_lab_id', 0)
        log.debug("MOCK FUNCTION: {} ID: {} URL {}".format(inspect.stack()[0][3], self.request_for_free_lab_id, url))

        responses = filter(lambda x: not x.get('status') == 'no_lab_available', REQUEST_LAB_WAIT_FOR_FREE_SUCCESS['responses'])

        # -> keepalive requests always OK, other ones by list
        if re.search('/keepalive', url.path):
            content = REQUEST_LAB_WAIT_FOR_FREE_SUCCESS['keepalive'][0]
            log.debug('keepalive \t%4.4u %s' % (self.request_for_free_lab_id, content)) 
        else:
            content = responses[self.request_for_free_lab_id]
            log.debug('\t%4.4u %s' % (self.request_for_free_lab_id, content)) 
            self.request_for_free_lab_id += 1
        return {'status_code': 200,
                'content': json.dumps(content),
                'headers': {'content-type': 'application/json'}
                }

    '''
    @urlmatch(netloc=r'.*fakelss.*', path=r'.*lab.*')
    def mock_api_request_lab_is_reserved_for_some_time(self, url, request):
        self.mock_api_request_lab_is_reserved_for_some_time_id = getattr(self, 'mock_api_request_lab_is_reserved_for_some_time_id', 0)
        log.debug("MOCK FUNCTION: {} ID: {} URL {}".format(inspect.stack()[0][3], self.mock_api_request_lab_is_reserved_for_some_time_id, url))
        log.debug("\n\t%u:createLabRequest() is %s" % (self.mock_api_request_lab_is_reserved_for_some_time_id, createLabRequest))
        if self.mock_api_request_lab_is_reserved_for_some_time_id == 0:
            self.content, self.lr_id, self.etag = createLabRequest()
        if self.mock_api_request_lab_is_reserved_for_some_time_id == 1:
            log.debug("1")
            self.content = updateLRPending(self.content, 
                state_search_query = {"build.id":"netact/product/99.17.03.0.123"},
                message = u"kokeilu",
            )
            log.debug("MARK")
        log.debug("%4.4u: content=%s" % (self.mock_api_request_lab_is_reserved_for_some_time_id, self.content))
        self.mock_api_request_lab_is_reserved_for_some_time_id += 1
        return {'status_code': 200,
                'content': json.dumps(self.content),
                'headers': {'content-type': 'application/json'}
                }
    '''

    @urlmatch(netloc=r'.*fakelss.*', path=r'.*lab.*')
    def mock_api_request_lab_NOK_timeout_triggers(self, url, request):
        log.debug("MOCK FUNCTION: {} ID: {} URL {}".format(inspect.stack()[0][3], self.mock_request_lab_NOK_timeout_triggers_json_id, url))
        content = ""
        if self.mock_request_lab_NOK_timeout_triggers_json_id == 0:
            content = json.dumps({u'_updated': u'Wed, 21 Jun 2017 11:45:46 GMT', u'_links': {
                u'self': {u'href': u'labrequests/594a5c6a5850e800012fd299', u'title': u'Labrequest'}},
                                  u'_created': u'Wed, 21 Jun 2017 11:45:46 GMT', u'_status': u'OK',
                                  u'_id': u'594a5c6a5850e800012fd299',
                                  u'_etag': u'd6173aad39cca844df47e00a84f9df3fa121a792'})
        elif self.mock_request_lab_NOK_timeout_triggers_json_id == 1:
            content = json.dumps({u'username': u'tester', u'status': u'pending', u'_updated': u'Wed, 21 Jun 2017 11:45:47 GMT', u'expireAt': u'Wed, 21 Jun 2017 11:46:46 GMT', u'lab_reservation_time': u'60', u'_links': {u'self': {u'href': u'labrequests/594a5c6a5850e800012fd299', u'title': u'Labrequest'}, u'parent': {u'href': u'/', u'title': u'home'}, u'collection': {u'href': u'labrequests', u'title': u'labrequests'}}, u'_created': u'Wed, 21 Jun 2017 11:45:46 GMT', u'state_search_query': u'{"build.id":"netact/product/99.17.03.0.123"}', u'message': u'kokeilu', u'_id': u'594a5c6a5850e800012fd299', u'_etag': u'8f6dd40ee28f348ff8960756860afa343f9516e7'})
        elif self.mock_request_lab_NOK_timeout_triggers_json_id == 2:
            content = json.dumps({u'_updated': u'Wed, 21 Jun 2017 11:45:48 GMT', u'_links': {u'self': {u'href': u'labrequests/594a5c6a5850e800012fd299/keepalive/594a5c6a5850e800012fd299', u'title': u'Labrequest'}}, u'_created': u'Wed, 21 Jun 2017 11:45:46 GMT', u'_status': u'OK', u'_id': u'594a5c6a5850e800012fd299', u'_etag': u'b69f1b7b3f7bb350b3f3e28c3536573383f6af7a'})
        elif self.mock_request_lab_NOK_timeout_triggers_json_id == 3:
            content = json.dumps({u'username': u'tester', u'status': u'ready', u'_updated': u'Wed, 21 Jun 2017 11:45:49 GMT', u'expireAt': u'Wed, 21 Jun 2017 11:46:46 GMT', u'lab_reservation_time': u'60', u'lab': u'594a55195850e80001c158de', u'_links': {u'self': {u'href': u'labrequests/594a5c6a5850e800012fd299', u'title': u'Labrequest'}, u'parent': {u'href': u'/', u'title': u'home'}, u'collection': {u'href': u'labrequests', u'title': u'labrequests'}}, u'_created': u'Wed, 21 Jun 2017 11:45:46 GMT', u'state_search_query': u'{"build.id":"netact/product/99.17.03.0.123"}', u'message': u'kokeilu', u'_id': u'594a5c6a5850e800012fd299', u'_etag': u'5db06fd34a1afbe1051a3db37505f3d5336a6671'})
        elif self.mock_request_lab_NOK_timeout_triggers_json_id >= 4:
            content = json.dumps({u'status': u'queued_for_revert', u'_updated': u'Wed, 21 Jun 2017 11:45:50 GMT', u'lab_type': u'cloud', u'states': [u'594a55195850e80001c158df'], u'lab_name': u'CloudLab4087', u'_links': {u'self': {u'href': u'labs/594a55195850e80001c158de', u'title': u'Lab'}, u'parent': {u'href': u'/', u'title': u'home'}, u'collection': {u'href': u'labs', u'title': u'labs'}}, u'_created': u'Wed, 21 Jun 2017 11:14:33 GMT', u'reservation': u'594a5c6a5850e800012fd29a', u'_id': u'594a55195850e80001c158de', u'_etag': u'c9be79d124893a8ea099bdce2a6aee79da3d528c'})
        self.mock_request_lab_NOK_timeout_triggers_json_id += 1
        return {'status_code': 200,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*labs.*')
    def mock_api_release_lab_NOK_lab_is_not_reserved_2(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        content = json.dumps({u'_items': [{u'status': u'queued_for_initialization', u'_updated': u'Tue, 04 Apr 2017 14:01:39 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Tue, 04 Apr 2017 14:01:39 GMT', u'lab': u'58e3a7431df07900010ddea2', u'build': {u'id': u'netact/product/99.17.03.0.166'}, u'_created': u'Tue, 04 Apr 2017 14:01:39 GMT', u'_id': u'58e3a7431df07900010ddea3', u'_etag': u'f994b88ff52740182eb531fad7dde0bdc3b95476', u'snapshot_status': u'queued'}], u'lab_name': u'CloudLab1640', u'_links': {u'self': {u'href': u'labs/58e3a7431df07900010ddea2', u'title': u'Lab'}}, u'_created': u'Tue, 04 Apr 2017 14:01:39 GMT', u'reservation': {}, u'_id': u'58e3a7431df07900010ddea2', u'_etag': u'a8a01e448ef12c2677b09d5995fb141c48336d09'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab1640"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
        return {'status_code': 200,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*labs.*')
    def mock_api_release_lab_NOK_reserved_by_another_user(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        content = json.dumps({u'_items': [{u'status': u'queued_for_initialization', u'_updated': u'Tue, 04 Apr 2017 14:01:39 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Tue, 04 Apr 2017 14:01:39 GMT', u'lab': u'58e3a7431df07900010ddea2', u'build': {u'id': u'netact/product/99.17.03.0.166'}, u'_created': u'Tue, 04 Apr 2017 14:01:39 GMT', u'_id': u'58e3a7431df07900010ddea3', u'_etag': u'f994b88ff52740182eb531fad7dde0bdc3b95476', u'snapshot_status': u'queued'}], u'lab_name': u'CloudLab1640', u'_links': {u'self': {u'href': u'labs/58e3a7431df07900010ddea2', u'title': u'Lab'}}, u'_created': u'Tue, 04 Apr 2017 14:01:39 GMT', u'reservation': {u'username': u'root', u'_updated': u'Tue, 04 Apr 2017 14:02:23 GMT', u'lab': u'58e3a7431df07900010ddea2', u'_created': u'Tue, 04 Apr 2017 14:02:23 GMT', u'message': u'NA17_2 to NA17_5 upgrade test', u'_id': u'58e3a76f1df07900010ddea9', u'_etag': u'16740001b53c4d59bac98886387d4625a0e35208'}, u'_id': u'58e3a7431df07900010ddea2', u'_etag': u'a8a01e448ef12c2677b09d5995fb141c48336d09'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab1640"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
        return {'status_code': 200,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|reservations).*')
    def mock_api_release_lab_NOK_server_precondition_failure(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_release_lab_NOK_server_precondition_failure_json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'queued_for_initialization', u'_updated': u'Tue, 04 Apr 2017 14:01:39 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Tue, 04 Apr 2017 14:01:39 GMT', u'lab': u'58e3a7431df07900010ddea2', u'build': {u'id': u'netact/product/99.17.03.0.166'}, u'_created': u'Tue, 04 Apr 2017 14:01:39 GMT', u'_id': u'58e3a7431df07900010ddea3', u'_etag': u'f994b88ff52740182eb531fad7dde0bdc3b95476', u'snapshot_status': u'queued'}], u'lab_name': u'CloudLab1640', u'_links': {u'self': {u'href': u'labs/58e3a7431df07900010ddea2', u'title': u'Lab'}}, u'_created': u'Tue, 04 Apr 2017 14:01:39 GMT', u'reservation': {u'username': u'tester', u'_updated': u'Tue, 04 Apr 2017 14:02:23 GMT', u'lab': u'58e3a7431df07900010ddea2', u'_created': u'Tue, 04 Apr 2017 14:02:23 GMT', u'message': u'NA17_2 to NA17_5 upgrade test', u'_id': u'58e3a76f1df07900010ddea9', u'_etag': u'16740001b53c4d59bac98886387d4625a0e35208'}, u'_id': u'58e3a7431df07900010ddea2', u'_etag': u'a8a01e448ef12c2677b09d5995fb141c48336d09'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab1640"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        elif self.mock_release_lab_NOK_server_precondition_failure_json_id == 1:
            content = None
            status_code = 422
        self.mock_release_lab_NOK_server_precondition_failure_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|reservations).*')
    def mock_api_release_lab_server_precondition_ignored(self, url, request):
        log.debug("MOCK FUNCTION: {} URL: {}".format(inspect.stack()[0][3], url))
        if self.mock_release_lab_NOK_server_precondition_failure_json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'queued_for_initialization', u'_updated': u'Tue, 04 Apr 2017 14:01:39 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Tue, 04 Apr 2017 14:01:39 GMT', u'lab': u'58e3a7431df07900010ddea2', u'build': {u'id': u'netact/product/99.17.03.0.166'}, u'_created': u'Tue, 04 Apr 2017 14:01:39 GMT', u'_id': u'58e3a7431df07900010ddea3', u'_etag': u'f994b88ff52740182eb531fad7dde0bdc3b95476', u'snapshot_status': u'queued'}], u'lab_name': u'CloudLab1640', u'_links': {u'self': {u'href': u'labs/58e3a7431df07900010ddea2', u'title': u'Lab'}}, u'_created': u'Tue, 04 Apr 2017 14:01:39 GMT', u'reservation': {u'username': u'tester', u'_updated': u'Tue, 04 Apr 2017 14:02:23 GMT', u'lab': u'58e3a7431df07900010ddea2', u'_created': u'Tue, 04 Apr 2017 14:02:23 GMT', u'message': u'NA17_2 to NA17_5 upgrade test', u'_id': u'58e3a76f1df07900010ddea9', u'_etag': u'16740001b53c4d59bac98886387d4625a0e35208'}, u'_id': u'58e3a7431df07900010ddea2', u'_etag': u'a8a01e448ef12c2677b09d5995fb141c48336d09'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab1640"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        elif self.mock_release_lab_NOK_server_precondition_failure_json_id == 1:
            self.assertTrue('force' in url.query)
            content = None
            status_code = 204
        self.mock_release_lab_NOK_server_precondition_failure_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|reservations).*')
    def mock_api_release_lab_OK(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_release_lab_OK_json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'queued_for_initialization', u'_updated': u'Tue, 04 Apr 2017 14:01:39 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Tue, 04 Apr 2017 14:01:39 GMT', u'lab': u'58e3a7431df07900010ddea2', u'build': {u'id': u'netact/product/99.17.03.0.166'}, u'_created': u'Tue, 04 Apr 2017 14:01:39 GMT', u'_id': u'58e3a7431df07900010ddea3', u'_etag': u'f994b88ff52740182eb531fad7dde0bdc3b95476', u'snapshot_status': u'queued'}], u'lab_name': u'CloudLab1640', u'_links': {u'self': {u'href': u'labs/58e3a7431df07900010ddea2', u'title': u'Lab'}}, u'_created': u'Tue, 04 Apr 2017 14:01:39 GMT', u'reservation': {u'username': u'tester', u'_updated': u'Tue, 04 Apr 2017 14:02:23 GMT', u'lab': u'58e3a7431df07900010ddea2', u'_created': u'Tue, 04 Apr 2017 14:02:23 GMT', u'message': u'NA17_2 to NA17_5 upgrade test', u'_id': u'58e3a76f1df07900010ddea9', u'_etag': u'16740001b53c4d59bac98886387d4625a0e35208'}, u'_id': u'58e3a7431df07900010ddea2', u'_etag': u'a8a01e448ef12c2677b09d5995fb141c48336d09'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab1640"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        elif self.mock_release_lab_OK_json_id == 1:
            content = None
            status_code = 204
        self.mock_release_lab_OK_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|states|reservations).*')
    def mock_api_preserve_state_OK(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        content = {}
        log.debug("### mock_preserve_state_OK_json_id = {}".format(self.mock_preserve_state_OK_json_id))
        if self.mock_preserve_state_OK_json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Wed, 03 May 2017 08:18:55 GMT', u'previously_reverted_state': {u'_updated': u'Wed, 03 May 2017 07:27:17 GMT', u'lab': u'59098654b173b90001f31ae8', u'build': {u'id': u'netact/product/99.17.03.0.303'}, u'snapshot_id': u'269129', u'_created': u'Wed, 03 May 2017 07:27:16 GMT', u'_id': u'59098654b173b90001f31ae9', u'_etag': u'4072057831a88f7ab49c1ada824ac290a96ec0e7', u'snapshot_status': u'available'}, u'lab_type': u'vsprint', u'states': [{u'_updated': u'Wed, 03 May 2017 07:27:17 GMT', u'lab': u'59098654b173b90001f31ae8', u'build': {u'id': u'netact/product/99.17.03.0.303'}, u'snapshot_id': u'269129', u'_created': u'Wed, 03 May 2017 07:27:16 GMT', u'_id': u'59098654b173b90001f31ae9', u'_etag': u'4072057831a88f7ab49c1ada824ac290a96ec0e7', u'snapshot_status': u'available'}, {u'_updated': u'Wed, 03 May 2017 07:27:16 GMT', u'lab': u'59098654b173b90001f31ae8', u'build': {u'id': u'netact/product/99.17.03.0.522'}, u'_created': u'Wed, 03 May 2017 07:27:16 GMT', u'_id': u'59098654b173b90001f31aea', u'_etag': u'dfc48632c0f1571105ce3057778b11527c607772', u'snapshot_status': u'queued'}, {u'_updated': u'Wed, 03 May 2017 07:27:17 GMT', u'lab': u'59098654b173b90001f31ae8', u'build': {u'id': u'netact/product/99.17.03.0.645'}, u'snapshot_id': u'330035', u'_created': u'Wed, 03 May 2017 07:27:16 GMT', u'_id': u'59098654b173b90001f31aeb', u'_etag': u'336014775078c2c09ff41ebf2ca1e8315ca347a9', u'snapshot_status': u'available'}], u'lab_name': u'SprintLab16', u'_links': {u'self': {u'href': u'labs/59098654b173b90001f31ae8', u'title': u'Lab'}}, u'_created': u'Wed, 03 May 2017 07:27:16 GMT', u'reservation': {u'username': u'tester', u'_updated': u'Wed, 03 May 2017 08:18:55 GMT', u'lab': u'59098654b173b90001f31ae8', u'_created': u'Wed, 03 May 2017 08:18:55 GMT', u'message': u'NA17_2 to NA17_5 upgrade test', u'_id': u'5909926fb173b90001f31afa', u'_etag': u'b025ece73dd25d43103fb890b44409448277d3c8'}, u'_id': u'59098654b173b90001f31ae8', u'_etag': u'56fbaedee92f9c3a0d6ae923b657cd218e2acb7c'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"SprintLab16"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        elif self.mock_preserve_state_OK_json_id == 1:
            content = json.dumps({u'_updated': u'Wed, 03 May 2017 07:55:13 GMT', u'_links': {u'self': {u'href': u'states/59098ce1b173b90001f31af8', u'title': u'State'}}, u'_created': u'Wed, 03 May 2017 07:55:13 GMT', u'_status': u'OK', u'_id': u'59098ce1b173b90001f31af8', u'_etag': u'db4bb0e75cdae5ba4cf66597959b86c64444fbc0'})
            status_code = 200
        elif self.mock_preserve_state_OK_json_id == 2:
            content = json.dumps({u'_updated': u'Wed, 03 May 2017 07:55:13 GMT', u'lab': u'59098654b173b90001f31ad6', u'_links': {u'self': {u'href': u'states/59098ce1b173b90001f31af8', u'title': u'State'}, u'parent': {u'href': u'/', u'title': u'home'}, u'collection': {u'href': u'states', u'title': u'states'}}, u'build': {u'id': u'netact/product/99.17.03.0.335572'}, u'_created': u'Wed, 03 May 2017 07:55:13 GMT', u'_id': u'59098ce1b173b90001f31af8', u'_etag': u'db4bb0e75cdae5ba4cf66597959b86c64444fbc0', u'snapshot_status': u'queued'})
            status_code = 200
        elif self.mock_preserve_state_OK_json_id == 3:
            content = json.dumps({u'_updated': u'Wed, 03 May 2017 07:55:14 GMT', u'lab': u'59098654b173b90001f31ad6', u'_links': {u'self': {u'href': u'states/59098ce1b173b90001f31af8', u'title': u'State'}, u'parent': {u'href': u'/', u'title': u'home'}, u'collection': {u'href': u'states', u'title': u'states'}}, u'build': {u'id': u'netact/product/99.17.03.0.335572'}, u'snapshot_id': u'342914', u'_created': u'Wed, 03 May 2017 07:55:13 GMT', u'_id': u'59098ce1b173b90001f31af8', u'_etag': u'7af3fbef1e34ca8f50aba347bb1eafe85a5c923f', u'snapshot_status': u'available'})
            status_code = 200
        self.mock_preserve_state_OK_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|states|reservations).*')
    def mock_api_preserve_state_NOK_snapshot_status_error(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        content = {}
        log.debug("### mock_preserve_state_NOK_snapshot_status_error_json_id = {}".format(self.mock_preserve_state_NOK_snapshot_status_error_json_id))
        if self.mock_preserve_state_NOK_snapshot_status_error_json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Wed, 03 May 2017 08:18:55 GMT', u'previously_reverted_state': {u'_updated': u'Wed, 03 May 2017 07:27:17 GMT', u'lab': u'59098654b173b90001f31ae8', u'build': {u'id': u'netact/product/99.17.03.0.303'}, u'snapshot_id': u'269129', u'_created': u'Wed, 03 May 2017 07:27:16 GMT', u'_id': u'59098654b173b90001f31ae9', u'_etag': u'4072057831a88f7ab49c1ada824ac290a96ec0e7', u'snapshot_status': u'available'}, u'lab_type': u'vsprint', u'states': [{u'_updated': u'Wed, 03 May 2017 07:27:17 GMT', u'lab': u'59098654b173b90001f31ae8', u'build': {u'id': u'netact/product/99.17.03.0.303'}, u'snapshot_id': u'269129', u'_created': u'Wed, 03 May 2017 07:27:16 GMT', u'_id': u'59098654b173b90001f31ae9', u'_etag': u'4072057831a88f7ab49c1ada824ac290a96ec0e7', u'snapshot_status': u'available'}, {u'_updated': u'Wed, 03 May 2017 07:27:16 GMT', u'lab': u'59098654b173b90001f31ae8', u'build': {u'id': u'netact/product/99.17.03.0.522'}, u'_created': u'Wed, 03 May 2017 07:27:16 GMT', u'_id': u'59098654b173b90001f31aea', u'_etag': u'dfc48632c0f1571105ce3057778b11527c607772', u'snapshot_status': u'queued'}, {u'_updated': u'Wed, 03 May 2017 07:27:17 GMT', u'lab': u'59098654b173b90001f31ae8', u'build': {u'id': u'netact/product/99.17.03.0.645'}, u'snapshot_id': u'330035', u'_created': u'Wed, 03 May 2017 07:27:16 GMT', u'_id': u'59098654b173b90001f31aeb', u'_etag': u'336014775078c2c09ff41ebf2ca1e8315ca347a9', u'snapshot_status': u'available'}], u'lab_name': u'SprintLab16', u'_links': {u'self': {u'href': u'labs/59098654b173b90001f31ae8', u'title': u'Lab'}}, u'_created': u'Wed, 03 May 2017 07:27:16 GMT', u'reservation': {u'username': u'tester', u'_updated': u'Wed, 03 May 2017 08:18:55 GMT', u'lab': u'59098654b173b90001f31ae8', u'_created': u'Wed, 03 May 2017 08:18:55 GMT', u'message': u'NA17_2 to NA17_5 upgrade test', u'_id': u'5909926fb173b90001f31afa', u'_etag': u'b025ece73dd25d43103fb890b44409448277d3c8'}, u'_id': u'59098654b173b90001f31ae8', u'_etag': u'56fbaedee92f9c3a0d6ae923b657cd218e2acb7c'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"SprintLab16"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        elif self.mock_preserve_state_NOK_snapshot_status_error_json_id == 1:
            content = json.dumps({u'_updated': u'Wed, 03 May 2017 07:55:13 GMT', u'_links': {u'self': {u'href': u'states/59098ce1b173b90001f31af8', u'title': u'State'}}, u'_created': u'Wed, 03 May 2017 07:55:13 GMT', u'_status': u'OK', u'_id': u'59098ce1b173b90001f31af8', u'_etag': u'db4bb0e75cdae5ba4cf66597959b86c64444fbc0'})
            status_code = 200
        elif self.mock_preserve_state_NOK_snapshot_status_error_json_id == 2:
            content = json.dumps({u'_updated': u'Wed, 03 May 2017 07:55:13 GMT', u'lab': u'59098654b173b90001f31ad6', u'_links': {u'self': {u'href': u'states/59098ce1b173b90001f31af8', u'title': u'State'}, u'parent': {u'href': u'/', u'title': u'home'}, u'collection': {u'href': u'states', u'title': u'states'}}, u'build': {u'id': u'netact/product/99.17.03.0.335572'}, u'_created': u'Wed, 03 May 2017 07:55:13 GMT', u'_id': u'59098ce1b173b90001f31af8', u'_etag': u'db4bb0e75cdae5ba4cf66597959b86c64444fbc0', u'snapshot_status': u'queued'})
            status_code = 200
        elif self.mock_preserve_state_NOK_snapshot_status_error_json_id == 3:
            content = json.dumps({u'_updated': u'Wed, 03 May 2017 07:55:14 GMT', u'lab': u'59098654b173b90001f31ad6', u'_links': {u'self': {u'href': u'states/59098ce1b173b90001f31af8', u'title': u'State'}, u'parent': {u'href': u'/', u'title': u'home'}, u'collection': {u'href': u'states', u'title': u'states'}}, u'build': {u'id': u'netact/product/99.17.03.0.335572'}, u'snapshot_id': u'342914', u'_created': u'Wed, 03 May 2017 07:55:13 GMT', u'_id': u'59098ce1b173b90001f31af8', u'_etag': u'7af3fbef1e34ca8f50aba347bb1eafe85a5c923f', u'snapshot_status': u'failed'})
            status_code = 200
        self.mock_preserve_state_NOK_snapshot_status_error_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|states|reservations).*')
    def mock_api_preserve_state_NOK_lab_reserved_by_another_user(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        content = {}
        log.debug("### mock_preserve_state_NOK_lab_reserved_by_another_user_json_id = {}".format(self.mock_preserve_state_NOK_lab_reserved_by_another_user_json_id))
        if self.mock_preserve_state_NOK_lab_reserved_by_another_user_json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Tue, 04 Apr 2017 14:01:39 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Tue, 04 Apr 2017 14:01:39 GMT', u'lab': u'58e3a7431df07900010ddea2', u'build': {u'id': u'netact/product/99.17.03.0.166'}, u'_created': u'Tue, 04 Apr 2017 14:01:39 GMT', u'_id': u'58e3a7431df07900010ddea3', u'_etag': u'f994b88ff52740182eb531fad7dde0bdc3b95476', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab1640', u'_links': {u'self': {u'href': u'labs/58e3a7431df07900010ddea2', u'title': u'Lab'}}, u'_created': u'Tue, 04 Apr 2017 14:01:39 GMT', u'reservation': {u'username': u'another_tester', u'_updated': u'Tue, 04 Apr 2017 14:02:23 GMT', u'lab': u'58e3a7431df07900010ddea2', u'_created': u'Tue, 04 Apr 2017 14:02:23 GMT', u'message': u'NA17_2 to NA17_5 upgrade test', u'_id': u'58e3a76f1df07900010ddea9', u'_etag': u'16740001b53c4d59bac98886387d4625a0e35208'}, 'previously_reverted_state': {u'_updated': u'Mon, 27 May 2017 08:07:28 GMT', u'lab': u'58e3a7431df07900010ddea2', u'build': {u'id': u'netact/product/99.17.03.0.166'}}, u'_id': u'58e3a7431df07900010ddea2', u'_etag': u'a8a01e448ef12c2677b09d5995fb141c48336d09'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab1640"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        elif self.mock_preserve_state_NOK_lab_reserved_by_another_user_json_id == 1:
            status_code = 200
            time.sleep(5)
        self.mock_preserve_state_NOK_lab_reserved_by_another_user_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|labrequest).*')
    def mock_api_request_lab_OK_lab_allocated(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        content = {}
        log.debug("### mock_request_lab_OK_json_id = {}".format(self. mock_request_lab_OK_json_id))
        if self.mock_request_lab_OK_json_id == 0:
            content = json.dumps({"_updated": "Fri, 31 Mar 2017 12:53:19 GMT", "_links": {"self": {"href": "labrequests/58de513f1df07900010dddf2", "title": "Labrequest"}}, "_created": "Fri, 31 Mar 2017 12:53:19 GMT", "_status": "OK", "_id": "58de513f1df07900010dddf2", "_etag": "ddc5f2e9e4b025d114ab36565997de71e41f8a3b"})
        elif self.mock_request_lab_OK_json_id == 1:
            content = json.dumps({"status": "queued_for_initialization", "_updated": "Wed, 22 Mar 2017 12:51:57 GMT", "lab_type": "cloud", "states": ["58d2736d1df07900010ddd20"], "_links": {"self": {"href": "labs/58d2736d1df07900010ddd1f", "title": "Lab"}, "collection": {"href": "labs", "title": "labs"}, "parent": {"href": "/", "title": "home"}}, "reservation": "58e1f3311df07900010dddff", "_created": "Wed, 22 Mar 2017 12:51:57 GMT", "_id": "58d2736d1df07900010ddd1f", "_etag": "5d95c871a0c1207793c538737357b7c7db69e6f7"})
        elif self.mock_request_lab_OK_json_id == 2:
            content = json.dumps({"_updated": "Mon, 03 Apr 2017 07:01:05 GMT", "_links": {"self": {"href": "labrequests/58e1f3311df07900010dddfd/keepalive/58e1f3311df07900010dddfd", "title": "Labrequest"}}, "_created": "Mon, 03 Apr 2017 07:01:05 GMT", "_status": "OK", "_id": "58e1f3311df07900010dddfd", "_etag": "8d118f4dcab590afb6870bc5a0e8e6bb7f7a82f6"})
        elif self.mock_request_lab_OK_json_id == 3:
            content = json.dumps({"username": "root", "status": "pending", "_updated": "Mon, 03 Apr 2017 07:36:07 GMT", "expireAt": "Mon, 03 Apr 2017 07:37:07 GMT", "lab_reservation_time": "60", "lab": "58d8c9851df07900010ddd8d", "_links": {"self": {"href": "labrequests/58e1fb671df07900010dde02", "title": "Labrequest"}, "collection": {"href": "labrequests", "title": "labrequests"}, "parent": {"href": "/", "title": "home"}}, "state_search_query": "{\"build.id\":\"netact/product/99.17.03.0.166\"}", "_created": "Mon, 03 Apr 2017 07:36:07 GMT", "message": "NA17_2 to NA17_5 upgrade test", "_id": "58e1fb671df07900010dde02", "_etag": "8359e79f9b7d9f75bc9c65483fb24a9a66a88b49"})
        elif self.mock_request_lab_OK_json_id == 4:
            content = json.dumps({"status": "ready", "_updated": "Wed, 22 Mar 2017 12:51:57 GMT", "lab_type": "cloud", "states": ["58d2736d1df07900010ddd20"], "lab_name": "CloudLab655", "_links": {"self": {"href": "labs/58d2736d1df07900010ddd1f", "title": "Lab"}, "collection": {"href": "labs", "title": "labs"}, "parent": {"href": "/", "title": "home"}}, "reservation": "58e1f3311df07900010dddff", "_created": "Wed, 22 Mar 2017 12:51:57 GMT", "_id": "58d2736d1df07900010ddd1f", "_etag": "5d95c871a0c1207793c538737357b7c7db69e6f7"})
        self.mock_request_lab_OK_json_id += 1
        return {'status_code': 200,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|labrequest).*')
    def mock_api_request_lab_OK_lab_allocated_with_lab_search_query(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        content = {}
        log.debug("### mock_request_lab_OK_json_id = {}".format(self. mock_request_lab_OK_json_id))
        if self.mock_request_lab_OK_json_id == 0:
            self._assert_param_exists_in_request_data("lab_search_query", url, request)
            self._assert_param_exists_in_request_data("state_search_query", url, request)
            content = json.dumps({"_updated": "Fri, 31 Mar 2017 12:53:19 GMT", "_links": {"self": {"href": "labrequests/58de513f1df07900010dddf2", "title": "Labrequest"}}, "_created": "Fri, 31 Mar 2017 12:53:19 GMT", "_status": "OK", "_id": "58de513f1df07900010dddf2", "_etag": "ddc5f2e9e4b025d114ab36565997de71e41f8a3b"})
        elif self.mock_request_lab_OK_json_id == 1:
            content = json.dumps({"status": "queued_for_initialization", "_updated": "Wed, 22 Mar 2017 12:51:57 GMT", "lab_type": "cloud", "states": ["58d2736d1df07900010ddd20"], "_links": {"self": {"href": "labs/58d2736d1df07900010ddd1f", "title": "Lab"}, "collection": {"href": "labs", "title": "labs"}, "parent": {"href": "/", "title": "home"}}, "reservation": "58e1f3311df07900010dddff", "_created": "Wed, 22 Mar 2017 12:51:57 GMT", "_id": "58d2736d1df07900010ddd1f", "_etag": "5d95c871a0c1207793c538737357b7c7db69e6f7"})
        elif self.mock_request_lab_OK_json_id == 2:
            content = json.dumps({"_updated": "Mon, 03 Apr 2017 07:01:05 GMT", "_links": {"self": {"href": "labrequests/58e1f3311df07900010dddfd/keepalive/58e1f3311df07900010dddfd", "title": "Labrequest"}}, "_created": "Mon, 03 Apr 2017 07:01:05 GMT", "_status": "OK", "_id": "58e1f3311df07900010dddfd", "_etag": "8d118f4dcab590afb6870bc5a0e8e6bb7f7a82f6"})
        elif self.mock_request_lab_OK_json_id == 3:
            content = json.dumps({"username": "root", "status": "pending", "_updated": "Mon, 03 Apr 2017 07:36:07 GMT", "expireAt": "Mon, 03 Apr 2017 07:37:07 GMT", "lab_reservation_time": "60", "lab": "58d8c9851df07900010ddd8d", "_links": {"self": {"href": "labrequests/58e1fb671df07900010dde02", "title": "Labrequest"}, "collection": {"href": "labrequests", "title": "labrequests"}, "parent": {"href": "/", "title": "home"}}, "state_search_query": "{\"build.id\":\"netact/product/99.17.03.0.166\"}", "_created": "Mon, 03 Apr 2017 07:36:07 GMT", "message": "NA17_2 to NA17_5 upgrade test", "_id": "58e1fb671df07900010dde02", "_etag": "8359e79f9b7d9f75bc9c65483fb24a9a66a88b49"})
        elif self.mock_request_lab_OK_json_id == 4:
            content = json.dumps({"status": "ready", "_updated": "Wed, 22 Mar 2017 12:51:57 GMT", "lab_type": "cloud", "states": ["58d2736d1df07900010ddd20"], "lab_name": "CloudLab655", "_links": {"self": {"href": "labs/58d2736d1df07900010ddd1f", "title": "Lab"}, "collection": {"href": "labs", "title": "labs"}, "parent": {"href": "/", "title": "home"}}, "reservation": "58e1f3311df07900010dddff", "_created": "Wed, 22 Mar 2017 12:51:57 GMT", "_id": "58d2736d1df07900010ddd1f", "_etag": "5d95c871a0c1207793c538737357b7c7db69e6f7"})
        self.mock_request_lab_OK_json_id += 1
        return {'status_code': 200,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|labrequest).*')
    def mock_api_request_lab_OK_no_lab_available(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        log.debug("### mock_request_lab_OK_json_id = {}".format(self. mock_request_lab_OK_json_id))
        if self.mock_request_lab_OK_json_id == 0:
            content = json.dumps({"_updated": "Fri, 31 Mar 2017 12:53:19 GMT", "_links": {"self": {"href": "labrequests/58de513f1df07900010dddf2", "title": "Labrequest"}}, "_created": "Fri, 31 Mar 2017 12:53:19 GMT", "_status": "OK", "_id": "58de513f1df07900010dddf2", "_etag": "ddc5f2e9e4b025d114ab36565997de71e41f8a3b"})
        elif self.mock_request_lab_OK_json_id == 1:
            content = json.dumps({"username": "root", "status": "pending", "_updated": "Mon, 03 Apr 2017 07:36:07 GMT", "expireAt": "Mon, 03 Apr 2017 07:37:07 GMT", "lab_reservation_time": "60", "_links": {"self": {"href": "labrequests/58e1fb671df07900010dde02", "title": "Labrequest"}, "collection": {"href": "labrequests", "title": "labrequests"}, "parent": {"href": "/", "title": "home"}}, "state_search_query": "{\"build.id\":\"netact/product/99.17.03.0.166\"}", "_created": "Mon, 03 Apr 2017 07:36:07 GMT", "message": "NA17_2 to NA17_5 upgrade test", "_id": "58e1fb671df07900010dde02", "_etag": "127d1caee20f7f5bc95b4c3d3a9abbc9c897df19"})
        elif self.mock_request_lab_OK_json_id == 2:
            content = json.dumps({"_updated": "Mon, 03 Apr 2017 07:01:05 GMT", "_links": {"self": {"href": "labrequests/58e1f3311df07900010dddfd/keepalive/58e1f3311df07900010dddfd", "title": "Labrequest"}}, "_created": "Mon, 03 Apr 2017 07:01:05 GMT", "_status": "OK", "_id": "58e1f3311df07900010dddfd", "_etag": "8d118f4dcab590afb6870bc5a0e8e6bb7f7a82f6"})
        elif self.mock_request_lab_OK_json_id == 3:
            content = json.dumps({"username": "root", "status": "pending", "_updated": "Mon, 03 Apr 2017 07:36:07 GMT", "expireAt": "Mon, 03 Apr 2017 07:37:07 GMT", "lab_reservation_time": "60", "_links": {"self": {"href": "labrequests/58e1fb671df07900010dde02", "title": "Labrequest"}, "collection": {"href": "labrequests", "title": "labrequests"}, "parent": {"href": "/", "title": "home"}}, "state_search_query": "{\"build.id\":\"netact/product/99.17.03.0.166\"}", "_created": "Mon, 03 Apr 2017 07:36:07 GMT", "message": "NA17_2 to NA17_5 upgrade test", "_id": "58e1fb671df07900010dde02", "_etag": "127d1caee20f7f5bc95b4c3d3a9abbc9c897df19"})
        elif self.mock_request_lab_OK_json_id == 4:
            content = json.dumps({"_updated": "Mon, 03 Apr 2017 07:01:05 GMT", "_links": {"self": {"href": "labrequests/58e1f3311df07900010dddfd/keepalive/58e1f3311df07900010dddfd", "title": "Labrequest"}}, "_created": "Mon, 03 Apr 2017 07:01:05 GMT", "_status": "OK", "_id": "58e1f3311df07900010dddfd", "_etag": "8d118f4dcab590afb6870bc5a0e8e6bb7f7a82f6"})
        elif self.mock_request_lab_OK_json_id == 3:
            content = json.dumps({"username": "root", "status": "pending", "_updated": "Mon, 03 Apr 2017 07:36:07 GMT", "expireAt": "Mon, 03 Apr 2017 07:37:07 GMT", "lab_reservation_time": "60", "_links": {"self": {"href": "labrequests/58e1fb671df07900010dde02", "title": "Labrequest"}, "collection": {"href": "labrequests", "title": "labrequests"}, "parent": {"href": "/", "title": "home"}}, "state_search_query": "{\"build.id\":\"netact/product/99.17.03.0.166\"}", "_created": "Mon, 03 Apr 2017 07:36:07 GMT", "message": "NA17_2 to NA17_5 upgrade test", "_id": "58e1fb671df07900010dde02", "_etag": "127d1caee20f7f5bc95b4c3d3a9abbc9c897df19"})

        self.mock_request_lab_OK_json_id += 1
        return {'status_code': 200,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|labrequest).*')
    def mock_api_request_lab_NOK_lab_allocated_snapshot_failed(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        content = {}
        log.debug("### mock_request_lab_NOK_lab_allocated_snapshot_failed_json_id = {}".format(self.mock_request_lab_NOK_lab_allocated_snapshot_failed_json_id))
        if self.mock_request_lab_NOK_lab_allocated_snapshot_failed_json_id == 0:
            content = json.dumps({"_updated": "Fri, 31 Mar 2017 12:53:19 GMT", "_links": {"self": {"href": "labrequests/58de513f1df07900010dddf2", "title": "Labrequest"}}, "_created": "Fri, 31 Mar 2017 12:53:19 GMT", "_status": "OK", "_id": "58de513f1df07900010dddf2", "_etag": "ddc5f2e9e4b025d114ab36565997de71e41f8a3b"})
        elif self.mock_request_lab_NOK_lab_allocated_snapshot_failed_json_id == 1:
            content = json.dumps({"status": "queued_for_initialization", "_updated": "Wed, 22 Mar 2017 12:51:57 GMT", "lab_type": "cloud", "states": ["58d2736d1df07900010ddd20"], "_links": {"self": {"href": "labs/58d2736d1df07900010ddd1f", "title": "Lab"}, "collection": {"href": "labs", "title": "labs"}, "parent": {"href": "/", "title": "home"}}, "reservation": "58e1f3311df07900010dddff", "_created": "Wed, 22 Mar 2017 12:51:57 GMT", "_id": "58d2736d1df07900010ddd1f", "_etag": "5d95c871a0c1207793c538737357b7c7db69e6f7"})
        elif self.mock_request_lab_NOK_lab_allocated_snapshot_failed_json_id == 2:
            content = json.dumps({"_updated": "Mon, 03 Apr 2017 07:01:05 GMT", "_links": {"self": {"href": "labrequests/58e1f3311df07900010dddfd/keepalive/58e1f3311df07900010dddfd", "title": "Labrequest"}}, "_created": "Mon, 03 Apr 2017 07:01:05 GMT", "_status": "OK", "_id": "58e1f3311df07900010dddfd", "_etag": "8d118f4dcab590afb6870bc5a0e8e6bb7f7a82f6"})
        elif self.mock_request_lab_NOK_lab_allocated_snapshot_failed_json_id == 3:
            content = json.dumps({"username": "root", "status": "pending", "_updated": "Mon, 03 Apr 2017 07:36:07 GMT", "expireAt": "Mon, 03 Apr 2017 07:37:07 GMT", "lab_reservation_time": "60", "lab": "58d8c9851df07900010ddd8d", "_links": {"self": {"href": "labrequests/58e1fb671df07900010dde02", "title": "Labrequest"}, "collection": {"href": "labrequests", "title": "labrequests"}, "parent": {"href": "/", "title": "home"}}, "state_search_query": "{\"build.id\":\"netact/product/99.17.03.0.166\"}", "_created": "Mon, 03 Apr 2017 07:36:07 GMT", "message": "NA17_2 to NA17_5 upgrade test", "_id": "58e1fb671df07900010dde02", "_etag": "8359e79f9b7d9f75bc9c65483fb24a9a66a88b49"})
        elif self.mock_request_lab_NOK_lab_allocated_snapshot_failed_json_id == 4:
            content = json.dumps({"status": "state_operation_failed", "_updated": "Wed, 22 Mar 2017 12:51:57 GMT", "lab_type": "cloud", "states": ["58d2736d1df07900010ddd20"], "lab_name": "CloudLab655", "_links": {"self": {"href": "labs/58d2736d1df07900010ddd1f", "title": "Lab"}, "collection": {"href": "labs", "title": "labs"}, "parent": {"href": "/", "title": "home"}}, "reservation": "58e1f3311df07900010dddff", "_created": "Wed, 22 Mar 2017 12:51:57 GMT", "_id": "58d2736d1df07900010ddd1f", "_etag": "5d95c871a0c1207793c538737357b7c7db69e6f7"})
        self.mock_request_lab_NOK_lab_allocated_snapshot_failed_json_id += 1
        return {'status_code': 200,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|labrequest).*')
    def mock_api_request_lab_NOK_invalid_query(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        log.debug("### mock_request_lab_NOK_invalid_query_json_id = {}".format(self. mock_request_lab_NOK_invalid_query_json_id))
        if self.mock_request_lab_NOK_invalid_query_json_id == 0:
            content = json.dumps({"_updated": "Fri, 31 Mar 2017 12:53:19 GMT", "_links": {"self": {"href": "labrequests/58de513f1df07900010dddf2", "title": "Labrequest"}}, "_created": "Fri, 31 Mar 2017 12:53:19 GMT", "_status": "OK", "_id": "58de513f1df07900010dddf2", "_etag": "ddc5f2e9e4b025d114ab36565997de71e41f8a3b"})
        elif self.mock_request_lab_NOK_invalid_query_json_id == 1:
            content = json.dumps({"username": "root", "status": "error", "_updated": "Mon, 03 Apr 2017 07:36:07 GMT", "expireAt": "Mon, 03 Apr 2017 07:37:07 GMT", "lab_reservation_time": "60", "_links": {"self": {"href": "labrequests/58e1fb671df07900010dde02", "title": "Labrequest"}, "collection": {"href": "labrequests", "title": "labrequests"}, "parent": {"href": "/", "title": "home"}}, "state_search_query": "{\"build.id\":\"netact/product/99.17.03.0.166\"}", "_created": "Mon, 03 Apr 2017 07:36:07 GMT", "message": "NA17_2 to NA17_5 upgrade test", "_id": "58e1fb671df07900010dde02", "_etag": "127d1caee20f7f5bc95b4c3d3a9abbc9c897df19"})
        self.mock_request_lab_NOK_invalid_query_json_id += 1
        return {'status_code': 200,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|labrequest).*')
    def mock_api_request_lab_NOK_timeout_no_lab_available(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        log.debug("MOCK FUNCTION: {} ID: {} URL {}".format(inspect.stack()[0][3], self.mock_request_lab_NOK_timeout_no_lab_available_json_id, url))
        log.debug("### mock_request_lab_NOK_timeout_no_lab_available_json_id = {}".format(self.mock_request_lab_NOK_timeout_no_lab_available_json_id))
        if self.mock_request_lab_NOK_timeout_no_lab_available_json_id == 0:
            content = json.dumps({"_updated": "Fri, 31 Mar 2017 12:53:19 GMT", "_links": {"self": {"href": "labrequests/58de513f1df07900010dddf2", "title": "Labrequest"}}, "_created": "Fri, 31 Mar 2017 12:53:19 GMT", "_status": "OK", "_id": "58de513f1df07900010dddf2", "_etag": "ddc5f2e9e4b025d114ab36565997de71e41f8a3b"})
        elif self.mock_request_lab_NOK_timeout_no_lab_available_json_id == 1:
            content = json.dumps({"username": "root", "status": "no_lab_available", "_updated": "Mon, 03 Apr 2017 07:36:07 GMT", "expireAt": "Mon, 03 Apr 2017 07:37:07 GMT", "lab_reservation_time": "60", "_links": {"self": {"href": "labrequests/58e1fb671df07900010dde02", "title": "Labrequest"}, "collection": {"href": "labrequests", "title": "labrequests"}, "parent": {"href": "/", "title": "home"}}, "state_search_query": "{\"build.id\":\"netact/product/99.17.03.0.166\"}", "_created": "Mon, 03 Apr 2017 07:36:07 GMT", "message": "NA17_2 to NA17_5 upgrade test", "_id": "58e1fb671df07900010dde02", "_etag": "127d1caee20f7f5bc95b4c3d3a9abbc9c897df19"})
        elif self.mock_request_lab_NOK_timeout_no_lab_available_json_id == 2:
            content = json.dumps({"_updated": "Fri, 31 Mar 2017 12:53:19 GMT", "_links": {"self": {"href": "labrequests/58de513f1df07900010dddf2", "title": "Labrequest"}}, "_created": "Fri, 31 Mar 2017 12:53:19 GMT", "_status": "OK", "_id": "58de513f1df07900010dddf2", "_etag": "ddc5f2e9e4b025d114ab36565997de71e41f8a3b"})
        elif self.mock_request_lab_NOK_timeout_no_lab_available_json_id == 3:
            content = json.dumps({"username": "root", "status": "no_lab_available", "_updated": "Mon, 03 Apr 2017 07:36:07 GMT", "expireAt": "Mon, 03 Apr 2017 07:37:07 GMT", "lab_reservation_time": "60", "_links": {"self": {"href": "labrequests/58e1fb671df07900010dde02", "title": "Labrequest"}, "collection": {"href": "labrequests", "title": "labrequests"}, "parent": {"href": "/", "title": "home"}}, "state_search_query": "{\"build.id\":\"netact/product/99.17.03.0.166\"}", "_created": "Mon, 03 Apr 2017 07:36:07 GMT", "message": "NA17_2 to NA17_5 upgrade test", "_id": "58e1fb671df07900010dde02", "_etag": "127d1caee20f7f5bc95b4c3d3a9abbc9c897df19"})
        self.mock_request_lab_NOK_timeout_no_lab_available_json_id += 1
        return {'status_code': 200,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*lab.*')
    def mock_api_error_500(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        return {'status_code': 500,
                'headers': {'content-type': 'application/json'},
                'content': json.dumps("Internal server error")}

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*lab.*')
    def mock_api_error_404(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        return {'status_code': 404,
                'headers': {'content-type': 'application/json'},
                'content': json.dumps("Not found")}

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*lab.*')
    def mock_api_error_401(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        return {'status_code': 401,
                'headers': {'content-type': 'application/json'},
                'content': json.dumps("Permission denied")}

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|states|storage/snapshot/).*')
    def mock_api_admin_migrate_snapshots_OK(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_admin_migrate_snapshots_OK_json_id == 0:
            content = json.dumps({u'_items': [], u'_links': {u'self': {u'href': u'labs', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 0, u'page': 1}})
            status_code = 200
        elif self.mock_admin_migrate_snapshots_OK_json_id == 1:
            content = json.dumps({u'maxsnapshots': u'3', u'snapshots': [{u'comment': u'NetAct16_5_P8_vSphere_Updated_NE_S/W_updated_vSpehereLicenseInstalled', u'snapshotID': u'1435', u'envID': u'6692', u'date': u'1483597803', u'name': u'SprintLab283-1483597803'}, {u'comment': u'NetAct_17.2_P8', u'snapshotID': u'1726', u'envID': u'6692', u'date': u'1490852297', u'name': u'SprintLab283-1490852297'}, {u'comment': u'NetAct_17.2_P8_w_bsc17_adapt', u'snapshotID': u'2148', u'envID': u'6692', u'date': u'1499326517', u'name': u'SprintLab283-1499326517'}]})
            status_code = 200
        elif self.mock_admin_migrate_snapshots_OK_json_id == 2:
            content = json.dumps({u'_updated': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_links': {u'self': {u'href': u'labs/59773b5e58a5940001759c6e', u'title': u'Lab'}}, u'_created': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_status': u'OK', u'_id': u'59773b5e58a5940001759c6e', u'_etag': u'b5d52acba24b9c40a4cb8c639f5f17ca83ec634e'})
            status_code = 200
        elif self.mock_admin_migrate_snapshots_OK_json_id == 3:
            content = json.dumps({u'_updated': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_links': {u'self': {u'href': u'states/59773b5e58a5940001759c6f', u'title': u'State'}}, u'_created': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_status': u'OK', u'_id': u'59773b5e58a5940001759c6f', u'_etag': u'e61f7788c80f9543da5f3012a048734f46df5e4b'})
            status_code = 200
        elif self.mock_admin_migrate_snapshots_OK_json_id == 4:
            content = json.dumps({u'_updated': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_links': {u'self': {u'href': u'states/59773b5e58a5940001759c70', u'title': u'State'}}, u'_created': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_status': u'OK', u'_id': u'59773b5e58a5940001759c70', u'_etag': u'f5092cb020a1847060d0d9a409847efc2c4ca5e7'})
            status_code = 200
        elif self.mock_admin_migrate_snapshots_OK_json_id == 5:
            content = json.dumps({u'_updated': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_links': {u'self': {u'href': u'states/59773b5e58a5940001759c71', u'title': u'State'}}, u'_created': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_status': u'OK', u'_id': u'59773b5e58a5940001759c71', u'_etag': u'd16f3b25854bb7f06f88c48f87b403645854b63c'})
            status_code = 200
        self.mock_admin_migrate_snapshots_OK_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|states|storage/snapshot/).*')
    def mock_api_admin_migrate_snapshots_OK_with_admin_server_access_params(self, url, request):
        json_id = self.mock_admin_migrate_snapshots_OK_with_admin_server_access_params_json_id
        log.debug("MOCK FUNCTION: {}, json_id: '{}'".format(inspect.stack()[0][3], json_id))
        if json_id == 0:
            content = json.dumps({u'_items': [], u'_links': {u'self': {u'href': u'labs', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 0, u'page': 1}})
            status_code = 200
        elif json_id == 1:
            content = json.dumps({u'maxsnapshots': u'3', u'snapshots': [{u'comment': u'NetAct16_5_P8_vSphere_Updated_NE_S/W_updated_vSpehereLicenseInstalled', u'snapshotID': u'1435', u'envID': u'6692', u'date': u'1483597803', u'name': u'SprintLab283-1483597803'}, {u'comment': u'NetAct_17.2_P8', u'snapshotID': u'1726', u'envID': u'6692', u'date': u'1490852297', u'name': u'SprintLab283-1490852297'}, {u'comment': u'NetAct_17.2_P8_w_bsc17_adapt', u'snapshotID': u'2148', u'envID': u'6692', u'date': u'1499326517', u'name': u'SprintLab283-1499326517'}]})
            status_code = 200
        elif json_id == 2:
            content = json.dumps({u'_updated': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_links': {u'self': {u'href': u'labs/59773b5e58a5940001759c6e', u'title': u'Lab'}}, u'_created': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_status': u'OK', u'_id': u'59773b5e58a5940001759c6e', u'_etag': u'b5d52acba24b9c40a4cb8c639f5f17ca83ec634e'})
            status_code = 200
        elif json_id == 3:
            self._assert_param_exists_in_request_data('"username": "mytestuser"', url, request)
            content = json.dumps({u'_updated': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_links': {u'self': {u'href': u'states/59773b5e58a5940001759c6f', u'title': u'State'}}, u'_created': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_status': u'OK', u'_id': u'59773b5e58a5940001759c6f', u'_etag': u'e61f7788c80f9543da5f3012a048734f46df5e4b'})
            status_code = 200
        elif json_id == 4:
            self._assert_param_exists_in_request_data('"username": "mytestuser"', url, request)
            content = json.dumps({u'_updated': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_links': {u'self': {u'href': u'states/59773b5e58a5940001759c70', u'title': u'State'}}, u'_created': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_status': u'OK', u'_id': u'59773b5e58a5940001759c70', u'_etag': u'f5092cb020a1847060d0d9a409847efc2c4ca5e7'})
            status_code = 200
        elif json_id == 5:
            content = json.dumps({u'_updated': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_links': {u'self': {u'href': u'states/59773b5e58a5940001759c71', u'title': u'State'}}, u'_created': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_status': u'OK', u'_id': u'59773b5e58a5940001759c71', u'_etag': u'd16f3b25854bb7f06f88c48f87b403645854b63c'})
            status_code = 200
        self.mock_admin_migrate_snapshots_OK_with_admin_server_access_params_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|states|storage/snapshot/).*')
    def mock_api_admin_migrate_snapshots_OK_lab_exists_and_snapshots_exist(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_admin_migrate_snapshots_OK_lab_exists_and_snapshots_exist_json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Tue, 25 Jul 2017 12:36:46 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Tue, 25 Jul 2017 13:31:17 GMT', u'lab': u'59773b5e58a5940001759c6e', u'build': {u'id': u'NetAct16_5_P8_vSphere_Updated_NE_S/W_updated_vSpehereLicenseInstalled'}, u'snapshot_id': u'CloudLab283-1483597803', u'_created': u'Tue, 25 Jul 2017 13:18:22 GMT', u'_id': u'5977451e58a5940001759c72', u'_etag': u'68f884946354a5002cc41e64b8f988bbcd346011', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 25 Jul 2017 13:31:17 GMT', u'lab': u'59773b5e58a5940001759c6e', u'build': {u'id': u'NetAct_17.2_P8'}, u'snapshot_id': u'CloudLab283-1490852297', u'_created': u'Tue, 25 Jul 2017 13:18:22 GMT', u'_id': u'5977451e58a5940001759c73', u'_etag': u'80d055339da1aad78f27e9397be45dc874fd8e4e', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 25 Jul 2017 13:31:17 GMT', u'lab': u'59773b5e58a5940001759c6e', u'build': {u'id': u'NetAct_17.2_P8_w_bsc17_adapt'}, u'snapshot_id': u'CloudLab283-1499326517', u'_created': u'Tue, 25 Jul 2017 13:18:22 GMT', u'_id': u'5977451e58a5940001759c74', u'_etag': u'1e5cd875310864003a89f4b8b0d6e1f1363d1d09', u'snapshot_status': u'available'}], u'lab_name': u'CLAB283', u'_links': {u'self': {u'href': u'labs/59773b5e58a5940001759c6e', u'title': u'Lab'}}, u'_created': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_id': u'59773b5e58a5940001759c6e', u'_etag': u'b5d52acba24b9c40a4cb8c639f5f17ca83ec634e'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CLAB283"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        elif self.mock_admin_migrate_snapshots_OK_lab_exists_and_snapshots_exist_json_id == 1:
            content = json.dumps({u'maxsnapshots': u'3', u'snapshots': [{u'comment': u'NetAct16_5_P8_vSphere_Updated_NE_S/W_updated_vSpehereLicenseInstalled', u'snapshotID': u'1435', u'envID': u'6692', u'date': u'1483597803', u'name': u'CloudLab283-1483597803'}, {u'comment': u'NetAct_17.2_P8', u'snapshotID': u'1726', u'envID': u'6692', u'date': u'1490852297', u'name': u'CloudLab283-1490852297'}, {u'comment': u'NetAct_17.2_P8_w_bsc17_adapt', u'snapshotID': u'2148', u'envID': u'6692', u'date': u'1499326517', u'name': u'CloudLab283-1499326517'}]})
            status_code = 200
        elif self.mock_admin_migrate_snapshots_OK_lab_exists_and_snapshots_exist_json_id == 2:
            content = json.dumps({u'_updated': u'Wed, 26 Jul 2017 06:22:12 GMT', u'_links': {u'self': {u'href': u'states/5977451e58a5940001759c72', u'title': u'State'}}, u'_created': u'Tue, 25 Jul 2017 13:18:22 GMT', u'_status': u'OK', u'_id': u'5977451e58a5940001759c72', u'_etag': u'f17f8fedd8aa85e8bc8e2d517eb08b600bb04f30'})
            status_code = 200
        elif self.mock_admin_migrate_snapshots_OK_lab_exists_and_snapshots_exist_json_id == 3:
            content = json.dumps({u'_updated': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_links': {u'self': {u'href': u'states/59773b5e58a5940001759c6f', u'title': u'State'}}, u'_created': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_status': u'OK', u'_id': u'59773b5e58a5940001759c6f', u'_etag': u'e61f7788c80f9543da5f3012a048734f46df5e4b'})
            status_code = 200
        elif self.mock_admin_migrate_snapshots_OK_lab_exists_and_snapshots_exist_json_id == 4:
            content = json.dumps({u'_updated': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_links': {u'self': {u'href': u'states/59773b5e58a5940001759c70', u'title': u'State'}}, u'_created': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_status': u'OK', u'_id': u'59773b5e58a5940001759c70', u'_etag': u'f5092cb020a1847060d0d9a409847efc2c4ca5e7'})
            status_code = 200
        elif self.mock_admin_migrate_snapshots_OK_lab_exists_and_snapshots_exist_json_id == 5:
            content = json.dumps({u'_updated': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_links': {u'self': {u'href': u'states/59773b5e58a5940001759c71', u'title': u'State'}}, u'_created': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_status': u'OK', u'_id': u'59773b5e58a5940001759c71', u'_etag': u'd16f3b25854bb7f06f88c48f87b403645854b63c'})
            status_code = 200
        self.mock_admin_migrate_snapshots_OK_lab_exists_and_snapshots_exist_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|states|storage/snapshot/).*')
    def mock_api_admin_migrate_snapshots_OK_additional_snapshots_exist(self, url, request):
        json_id = self.mock_admin_migrate_snapshots_OK_additional_snapshots_exist_json_id
        log.debug("MOCK FUNCTION: {}, JSON_ID : '{}'".format(inspect.stack()[0][3], json_id))
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Tue, 25 Jul 2017 12:36:46 GMT', u'lab_type': u'sprint', u'states': [{u'_updated': u'Tue, 25 Jul 2017 13:31:17 GMT', u'lab': u'59773b5e58a5940001759c6e', u'build': {u'id': u'NetAct16_5_P8_vSphere_Updated_NE_S/W_updated_vSpehereLicenseInstalled'}, u'snapshot_id': u'SprintLab283-1483597803_additional', u'_created': u'Tue, 25 Jul 2017 13:18:22 GMT', u'_id': u'5977451e58a5940001759c72', u'_etag': u'68f884946354a5002cc41e64b8f988bbcd346011', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 25 Jul 2017 13:31:17 GMT', u'lab': u'59773b5e58a5940001759c6e', u'build': {u'id': u'NetAct_17.2_P8'}, u'snapshot_id': u'SprintLab283-1490852297', u'_created': u'Tue, 25 Jul 2017 13:18:22 GMT', u'_id': u'5977451e58a5940001759c73', u'_etag': u'80d055339da1aad78f27e9397be45dc874fd8e4e', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 25 Jul 2017 13:31:17 GMT', u'lab': u'59773b5e58a5940001759c6e', u'build': {u'id': u'NetAct_17.2_P8_w_bsc17_adapt'}, u'snapshot_id': u'SprintLab283-1499326517', u'_created': u'Tue, 25 Jul 2017 13:18:22 GMT', u'_id': u'5977451e58a5940001759c74', u'_etag': u'1e5cd875310864003a89f4b8b0d6e1f1363d1d09', u'snapshot_status': u'available'}], u'lab_name': u'sprintlab283', u'_links': {u'self': {u'href': u'labs/59773b5e58a5940001759c6e', u'title': u'Lab'}}, u'_created': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_id': u'59773b5e58a5940001759c6e', u'_etag': u'b5d52acba24b9c40a4cb8c639f5f17ca83ec634e'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"sprintlab283"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        elif json_id == 1:
            content = json.dumps({u'maxsnapshots': u'3', u'snapshots': [{u'comment': u'NetAct16_5_P8_vSphere_Updated_NE_S/W_updated_vSpehereLicenseInstalled', u'snapshotID': u'1435', u'envID': u'6692', u'date': u'1483597803', u'name': u'SprintLab283-1483597803'}, {u'comment': u'NetAct_17.2_P8', u'snapshotID': u'1726', u'envID': u'6692', u'date': u'1490852297', u'name': u'SprintLab283-1490852297'}, {u'comment': u'NetAct_17.2_P8_w_bsc17_adapt', u'snapshotID': u'2148', u'envID': u'6692', u'date': u'1499326517', u'name': u'SprintLab283-1499326517'}]})
            status_code = 200
        elif json_id == 2:
            content = json.dumps({u'_updated': u'Wed, 26 Jul 2017 06:22:12 GMT', u'_links': {u'self': {u'href': u'states/5977451e58a5940001759c72', u'title': u'State'}}, u'_created': u'Tue, 25 Jul 2017 13:18:22 GMT', u'_status': u'OK', u'_id': u'5977451e58a5940001759c72', u'_etag': u'f17f8fedd8aa85e8bc8e2d517eb08b600bb04f30'})
            status_code = 200
        elif json_id == 3:
            content = json.dumps({u'_updated': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_links': {u'self': {u'href': u'states/59773b5e58a5940001759c6f', u'title': u'State'}}, u'_created': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_status': u'OK', u'_id': u'59773b5e58a5940001759c6f', u'_etag': u'e61f7788c80f9543da5f3012a048734f46df5e4b'})
            status_code = 200
        elif json_id == 4:
            content = json.dumps({u'_updated': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_links': {u'self': {u'href': u'states/59773b5e58a5940001759c70', u'title': u'State'}}, u'_created': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_status': u'OK', u'_id': u'59773b5e58a5940001759c70', u'_etag': u'f5092cb020a1847060d0d9a409847efc2c4ca5e7'})
            status_code = 200
        elif json_id == 5:
            content = json.dumps({u'_updated': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_links': {u'self': {u'href': u'states/59773b5e58a5940001759c71', u'title': u'State'}}, u'_created': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_status': u'OK', u'_id': u'59773b5e58a5940001759c71', u'_etag': u'd16f3b25854bb7f06f88c48f87b403645854b63c'})
            status_code = 200
        self.mock_admin_migrate_snapshots_OK_additional_snapshots_exist_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|states|storage/snapshot/).*')
    def mock_api_admin_migrate_snapshots_OK_additional_snapshots_exist_with_null_snap_id(self, url, request):
        json_id = self.mock_admin_migrate_snapshots_OK_additional_snapshots_exist_with_null_snap_id_json_id
        log.debug("MOCK FUNCTION: {}, JSON_ID : '{}'".format(inspect.stack()[0][3], json_id))
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Tue, 25 Jul 2017 12:36:46 GMT', u'lab_type': u'sprint', u'states': [{u'_updated': u'Tue, 25 Jul 2017 13:31:17 GMT', u'lab': u'59773b5e58a5940001759c6e', u'build': {u'id': u'NetAct16_5_P8_vSphere_Updated_NE_S/W_updated_vSpehereLicenseInstalled'}, u'snapshot_id': u'SprintLab283-1483597803_additional', u'_created': u'Tue, 25 Jul 2017 13:18:22 GMT', u'_id': u'5977451e58a5940001759c72', u'_etag': u'68f884946354a5002cc41e64b8f988bbcd346011', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 25 Jul 2017 13:31:17 GMT', u'lab': u'59773b5e58a5940001759c6e', u'build': {u'id': u'NetAct_17.2_P8'}, u'_created': u'Tue, 25 Jul 2017 13:18:22 GMT', u'_id': u'5977451e58a5940001759c73', u'_etag': u'80d055339da1aad78f27e9397be45dc874fd8e4e', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 25 Jul 2017 13:31:17 GMT', u'lab': u'59773b5e58a5940001759c6e', u'build': {u'id': u'NetAct_17.2_P8_w_bsc17_adapt'}, u'snapshot_id': u'SprintLab283-1499326517', u'_created': u'Tue, 25 Jul 2017 13:18:22 GMT', u'_id': u'5977451e58a5940001759c74', u'_etag': u'1e5cd875310864003a89f4b8b0d6e1f1363d1d09', u'snapshot_status': u'available'}], u'lab_name': u'sprintlab283', u'_links': {u'self': {u'href': u'labs/59773b5e58a5940001759c6e', u'title': u'Lab'}}, u'_created': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_id': u'59773b5e58a5940001759c6e', u'_etag': u'b5d52acba24b9c40a4cb8c639f5f17ca83ec634e'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"sprintlab283"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        elif json_id == 1:
            content = json.dumps({u'maxsnapshots': u'3', u'snapshots': [{u'comment': u'NetAct16_5_P8_vSphere_Updated_NE_S/W_updated_vSpehereLicenseInstalled', u'snapshotID': u'1435', u'envID': u'6692', u'date': u'1483597803', u'name': u'SprintLab283-1483597803'}, {u'comment': u'NetAct_17.2_P8_w_bsc17_adapt', u'snapshotID': u'2148', u'envID': u'6692', u'date': u'1499326517', u'name': u'SprintLab283-1499326517'}]})
            status_code = 200
        elif json_id == 2:
            content = json.dumps({u'_updated': u'Wed, 26 Jul 2017 06:22:12 GMT', u'_links': {u'self': {u'href': u'states/5977451e58a5940001759c72', u'title': u'State'}}, u'_created': u'Tue, 25 Jul 2017 13:18:22 GMT', u'_status': u'OK', u'_id': u'5977451e58a5940001759c72', u'_etag': u'f17f8fedd8aa85e8bc8e2d517eb08b600bb04f30'})
            status_code = 200
        elif json_id == 3:
            content = json.dumps({u'_updated': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_links': {u'self': {u'href': u'states/59773b5e58a5940001759c6f', u'title': u'State'}}, u'_created': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_status': u'OK', u'_id': u'59773b5e58a5940001759c6f', u'_etag': u'e61f7788c80f9543da5f3012a048734f46df5e4b'})
            status_code = 200
        elif json_id == 4:
            content = json.dumps({u'_updated': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_links': {u'self': {u'href': u'states/59773b5e58a5940001759c70', u'title': u'State'}}, u'_created': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_status': u'OK', u'_id': u'59773b5e58a5940001759c70', u'_etag': u'f5092cb020a1847060d0d9a409847efc2c4ca5e7'})
            status_code = 200
        elif json_id == 5:
            content = json.dumps({u'_updated': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_links': {u'self': {u'href': u'states/59773b5e58a5940001759c71', u'title': u'State'}}, u'_created': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_status': u'OK', u'_id': u'59773b5e58a5940001759c71', u'_etag': u'd16f3b25854bb7f06f88c48f87b403645854b63c'})
            status_code = 200
        self.mock_admin_migrate_snapshots_OK_additional_snapshots_exist_with_null_snap_id_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|states|storage/snapshot/).*')
    def mock_api_admin_migrate_snapshots_NOK_additional_snapshots_remove_failure_404(self, url, request):
        json_id = self.mock_admin_migrate_snapshots_NOK_additional_snapshots_remove_failure_404_json_id
        log.debug("MOCK FUNCTION: {}, JSON_ID : '{}'".format(inspect.stack()[0][3], json_id))
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Tue, 25 Jul 2017 12:36:46 GMT', u'lab_type': u'sprint', u'states': [{u'_updated': u'Tue, 25 Jul 2017 13:31:17 GMT', u'lab': u'59773b5e58a5940001759c6e', u'build': {u'id': u'NetAct16_5_P8_vSphere_Updated_NE_S/W_updated_vSpehereLicenseInstalled'}, u'snapshot_id': u'SprintLab283-1483597803_additional', u'_created': u'Tue, 25 Jul 2017 13:18:22 GMT', u'_id': u'5977451e58a5940001759c72', u'_etag': u'68f884946354a5002cc41e64b8f988bbcd346011', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 25 Jul 2017 13:31:17 GMT', u'lab': u'59773b5e58a5940001759c6e', u'build': {u'id': u'NetAct_17.2_P8'}, u'snapshot_id': u'SprintLab283-1490852297', u'_created': u'Tue, 25 Jul 2017 13:18:22 GMT', u'_id': u'5977451e58a5940001759c73', u'_etag': u'80d055339da1aad78f27e9397be45dc874fd8e4e', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 25 Jul 2017 13:31:17 GMT', u'lab': u'59773b5e58a5940001759c6e', u'build': {u'id': u'NetAct_17.2_P8_w_bsc17_adapt'}, u'snapshot_id': u'SprintLab283-1499326517', u'_created': u'Tue, 25 Jul 2017 13:18:22 GMT', u'_id': u'5977451e58a5940001759c74', u'_etag': u'1e5cd875310864003a89f4b8b0d6e1f1363d1d09', u'snapshot_status': u'available'}], u'lab_name': u'sprintlab283', u'_links': {u'self': {u'href': u'labs/59773b5e58a5940001759c6e', u'title': u'Lab'}}, u'_created': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_id': u'59773b5e58a5940001759c6e', u'_etag': u'b5d52acba24b9c40a4cb8c639f5f17ca83ec634e'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"sprintlab283"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        elif json_id == 1:
            content = json.dumps({u'maxsnapshots': u'3', u'snapshots': [{u'comment': u'NetAct16_5_P8_vSphere_Updated_NE_S/W_updated_vSpehereLicenseInstalled', u'snapshotID': u'1435', u'envID': u'6692', u'date': u'1483597803', u'name': u'SprintLab283-1483597803'}, {u'comment': u'NetAct_17.2_P8', u'snapshotID': u'1726', u'envID': u'6692', u'date': u'1490852297', u'name': u'SprintLab283-1490852297'}, {u'comment': u'NetAct_17.2_P8_w_bsc17_adapt', u'snapshotID': u'2148', u'envID': u'6692', u'date': u'1499326517', u'name': u'SprintLab283-1499326517'}]})
            status_code = 200
        elif json_id == 2:
            content = json.dumps({u'_updated': u'Wed, 26 Jul 2017 06:22:12 GMT', u'_links': {u'self': {u'href': u'states/5977451e58a5940001759c72', u'title': u'State'}}, u'_created': u'Tue, 25 Jul 2017 13:18:22 GMT', u'_status': u'OK', u'_id': u'5977451e58a5940001759c72', u'_etag': u'f17f8fedd8aa85e8bc8e2d517eb08b600bb04f30'})
            status_code = 200
        elif json_id == 3:
            content = None
            status_code = 404
        elif json_id == 4:
            content = json.dumps({u'_updated': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_links': {u'self': {u'href': u'states/59773b5e58a5940001759c70', u'title': u'State'}}, u'_created': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_status': u'OK', u'_id': u'59773b5e58a5940001759c70', u'_etag': u'f5092cb020a1847060d0d9a409847efc2c4ca5e7'})
            status_code = 200
        elif json_id == 5:
            content = json.dumps({u'_updated': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_links': {u'self': {u'href': u'states/59773b5e58a5940001759c71', u'title': u'State'}}, u'_created': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_status': u'OK', u'_id': u'59773b5e58a5940001759c71', u'_etag': u'd16f3b25854bb7f06f88c48f87b403645854b63c'})
            status_code = 200
        self.mock_admin_migrate_snapshots_NOK_additional_snapshots_remove_failure_404_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|states|storage/snapshot/).*')
    def mock_api_admin_migrate_snapshots_NOK_additional_snapshots_remove_failure_422(self, url, request):
        json_id = self.mock_admin_migrate_snapshots_NOK_additional_snapshots_remove_failure_422_json_id
        log.debug("MOCK FUNCTION: {}, JSON_ID : '{}'".format(inspect.stack()[0][3], json_id))
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Tue, 25 Jul 2017 12:36:46 GMT', u'lab_type': u'sprint', u'states': [{u'_updated': u'Tue, 25 Jul 2017 13:31:17 GMT', u'lab': u'59773b5e58a5940001759c6e', u'build': {u'id': u'NetAct16_5_P8_vSphere_Updated_NE_S/W_updated_vSpehereLicenseInstalled'}, u'snapshot_id': u'SprintLab283-1483597803_additional', u'_created': u'Tue, 25 Jul 2017 13:18:22 GMT', u'_id': u'5977451e58a5940001759c72', u'_etag': u'68f884946354a5002cc41e64b8f988bbcd346011', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 25 Jul 2017 13:31:17 GMT', u'lab': u'59773b5e58a5940001759c6e', u'build': {u'id': u'NetAct_17.2_P8'}, u'snapshot_id': u'SprintLab283-1490852297', u'_created': u'Tue, 25 Jul 2017 13:18:22 GMT', u'_id': u'5977451e58a5940001759c73', u'_etag': u'80d055339da1aad78f27e9397be45dc874fd8e4e', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 25 Jul 2017 13:31:17 GMT', u'lab': u'59773b5e58a5940001759c6e', u'build': {u'id': u'NetAct_17.2_P8_w_bsc17_adapt'}, u'snapshot_id': u'SprintLab283-1499326517', u'_created': u'Tue, 25 Jul 2017 13:18:22 GMT', u'_id': u'5977451e58a5940001759c74', u'_etag': u'1e5cd875310864003a89f4b8b0d6e1f1363d1d09', u'snapshot_status': u'available'}], u'lab_name': u'sprintlab283', u'_links': {u'self': {u'href': u'labs/59773b5e58a5940001759c6e', u'title': u'Lab'}}, u'_created': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_id': u'59773b5e58a5940001759c6e', u'_etag': u'b5d52acba24b9c40a4cb8c639f5f17ca83ec634e'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"sprintlab283"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        elif json_id == 1:
            content = json.dumps({u'maxsnapshots': u'3', u'snapshots': [{u'comment': u'NetAct16_5_P8_vSphere_Updated_NE_S/W_updated_vSpehereLicenseInstalled', u'snapshotID': u'1435', u'envID': u'6692', u'date': u'1483597803', u'name': u'SprintLab283-1483597803'}, {u'comment': u'NetAct_17.2_P8', u'snapshotID': u'1726', u'envID': u'6692', u'date': u'1490852297', u'name': u'SprintLab283-1490852297'}, {u'comment': u'NetAct_17.2_P8_w_bsc17_adapt', u'snapshotID': u'2148', u'envID': u'6692', u'date': u'1499326517', u'name': u'SprintLab283-1499326517'}]})
            status_code = 200
        elif json_id == 2:
            content = json.dumps({u'_updated': u'Wed, 26 Jul 2017 06:22:12 GMT', u'_links': {u'self': {u'href': u'states/5977451e58a5940001759c72', u'title': u'State'}}, u'_created': u'Tue, 25 Jul 2017 13:18:22 GMT', u'_status': u'OK', u'_id': u'5977451e58a5940001759c72', u'_etag': u'f17f8fedd8aa85e8bc8e2d517eb08b600bb04f30'})
            status_code = 200
        elif json_id == 3:
            content = None
            status_code = 422
        elif json_id == 4:
            content = json.dumps({u'_updated': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_links': {u'self': {u'href': u'states/59773b5e58a5940001759c70', u'title': u'State'}}, u'_created': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_status': u'OK', u'_id': u'59773b5e58a5940001759c70', u'_etag': u'f5092cb020a1847060d0d9a409847efc2c4ca5e7'})
            status_code = 200
        elif json_id == 5:
            content = json.dumps({u'_updated': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_links': {u'self': {u'href': u'states/59773b5e58a5940001759c71', u'title': u'State'}}, u'_created': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_status': u'OK', u'_id': u'59773b5e58a5940001759c71', u'_etag': u'd16f3b25854bb7f06f88c48f87b403645854b63c'})
            status_code = 200
        self.mock_admin_migrate_snapshots_NOK_additional_snapshots_remove_failure_422_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|states|storage/snapshot/).*')
    def mock_api_admin_migrate_snapshots_NOK_lab_exists_but_name_syntax_not_valid_in_dca(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_admin_migrate_snapshots_NOK_lab_exists_but_name_syntax_not_valid_in_dca_json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Tue, 25 Jul 2017 12:36:46 GMT', u'lab_type': u'sprint', u'states': [{u'_updated': u'Tue, 25 Jul 2017 13:31:17 GMT', u'lab': u'59773b5e58a5940001759c6e', u'build': {u'id': u'NetAct16_5_P8_vSphere_Updated_NE_S/W_updated_vSpehereLicenseInstalled'}, u'snapshot_id': u'SprintLab283-1483597803', u'_created': u'Tue, 25 Jul 2017 13:18:22 GMT', u'_id': u'5977451e58a5940001759c72', u'_etag': u'68f884946354a5002cc41e64b8f988bbcd346011', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 25 Jul 2017 13:31:17 GMT', u'lab': u'59773b5e58a5940001759c6e', u'build': {u'id': u'NetAct_17.2_P8'}, u'snapshot_id': u'SprintLab283-1490852297', u'_created': u'Tue, 25 Jul 2017 13:18:22 GMT', u'_id': u'5977451e58a5940001759c73', u'_etag': u'80d055339da1aad78f27e9397be45dc874fd8e4e', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 25 Jul 2017 13:31:17 GMT', u'lab': u'59773b5e58a5940001759c6e', u'build': {u'id': u'NetAct_17.2_P8_w_bsc17_adapt'}, u'snapshot_id': u'SprintLab283-1499326517', u'_created': u'Tue, 25 Jul 2017 13:18:22 GMT', u'_id': u'5977451e58a5940001759c74', u'_etag': u'1e5cd875310864003a89f4b8b0d6e1f1363d1d09', u'snapshot_status': u'available'}], u'lab_name': u'sprintlab283', u'_links': {u'self': {u'href': u'labs/59773b5e58a5940001759c6e', u'title': u'Lab'}}, u'_created': u'Tue, 25 Jul 2017 12:36:46 GMT', u'_id': u'59773b5e58a5940001759c6e', u'_etag': u'b5d52acba24b9c40a4cb8c639f5f17ca83ec634e'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"sprintlab283"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        self.mock_admin_migrate_snapshots_NOK_lab_exists_but_name_syntax_not_valid_in_dca_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
        }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|states|storage/snapshot/).*')
    def mock_api_admin_remove_labs_OK_one_lab(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_admin_remove_labs_OK_one_lab_json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Tue, 25 Jul 2017 10:27:23 GMT', u'lab_type': u'vsprint', u'states': [{u'_updated': u'Tue, 25 Jul 2017 10:27:23 GMT', u'lab': u'59771d0be0a14a0001e20e94', u'build': {u'id': u'netact/product/99.17.03.0.112'}, u'snapshot_id': u'113456', u'_created': u'Tue, 25 Jul 2017 10:27:23 GMT', u'_id': u'59771d0be0a14a0001e20e95', u'_etag': u'14763706830d62ab4c40a655adefb61a087605e6', u'snapshot_status': u'available'}], u'lab_name': u'vSprint7801', u'_links': {u'self': {u'href': u'labs/59771d0be0a14a0001e20e94', u'title': u'Lab'}}, u'_created': u'Tue, 25 Jul 2017 10:27:23 GMT', u'_id': u'59771d0be0a14a0001e20e94', u'_etag': u'99299120da35a1ad0232a9e86145950f1dacb4d3'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"vSprint7801"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        elif self.mock_admin_remove_labs_OK_one_lab_json_id == 1:
            content = None
            status_code = 204
        self.mock_admin_remove_labs_OK_one_lab_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }


    def mock_api_admin_remove_labs_OK_one_lab_no_states(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_admin_remove_labs_OK_one_lab_no_states_json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Tue, 25 Jul 2017 10:27:23 GMT', u'lab_type': u'vsprint', u'lab_name': u'vSprint7801', u'_links': {u'self': {u'href': u'labs/59771d0be0a14a0001e20e94', u'title': u'Lab'}}, u'_created': u'Tue, 25 Jul 2017 10:27:23 GMT', u'_id': u'59771d0be0a14a0001e20e94', u'_etag': u'99299120da35a1ad0232a9e86145950f1dacb4d3'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"vSprint7801"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        elif self.mock_admin_remove_labs_OK_one_lab_no_states_json_id == 1:
            content = None
            status_code = 204
        self.mock_admin_remove_labs_OK_one_lab_no_states_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }


    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|states|storage/snapshot/).*')
    def mock_api_admin_remove_labs_OK_several_labs_all_OK(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_admin_remove_labs_OK_several_labs_all_OK_json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Thu, 27 Jul 2017 10:55:49 GMT', u'lab_type': u'vsprint', u'states': [{u'_updated': u'Thu, 27 Jul 2017 10:55:49 GMT', u'lab': u'5979c6b5e0a14a0001e20eae', u'build': {u'id': u'netact/product/99.17.03.0.112'}, u'snapshot_id': u'113456', u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20eaf', u'_etag': u'e740812095675343a6deb674152a32ad656b6b74', u'snapshot_status': u'available'}], u'lab_name': u'vSprint9163', u'_links': {u'self': {u'href': u'labs/5979c6b5e0a14a0001e20eae', u'title': u'Lab'}}, u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20eae', u'_etag': u'2daf82d809e06a0ef88fa3aa8a772b0205bac129'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"vSprint9163"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        elif self.mock_admin_remove_labs_OK_several_labs_all_OK_json_id == 1:
            content = None
            status_code = 204
        elif self.mock_admin_remove_labs_OK_several_labs_all_OK_json_id == 2:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Tue, 25 Jul 2017 10:27:22 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Tue, 25 Jul 2017 10:27:22 GMT', u'lab': u'59771d0ae0a14a0001e20e84', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'snapshot_id': u'956', u'_created': u'Tue, 25 Jul 2017 10:27:22 GMT', u'_id': u'59771d0ae0a14a0001e20e85', u'_etag': u'1d4315b22b52e47329f560ac7e3c661b09d89128', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab7677', u'_links': {u'self': {u'href': u'labs/59771d0ae0a14a0001e20e84', u'title': u'Lab'}}, u'_created': u'Tue, 25 Jul 2017 10:27:22 GMT', u'_id': u'59771d0ae0a14a0001e20e84', u'_etag': u'9d5e0071d755cec1460f3017a8924aa81d5843de'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab7677"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        elif self.mock_admin_remove_labs_OK_several_labs_all_OK_json_id == 3:
            content = None
            status_code = 204
        self.mock_admin_remove_labs_OK_several_labs_all_OK_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
        }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|states|reservations).*')
    def mock_api_admin_remove_labs_NOK_one_lab_one_NOK(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        json_id = self.mock_admin_remove_labs_NOK_one_lab_one_NOK_json_id
        if  json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Thu, 27 Jul 2017 13:38:07 GMT', u'lab_type': u'other', u'states': [{u'_updated': u'Thu, 27 Jul 2017 13:38:07 GMT', u'lab': u'5979ecbfe0a14a0001e20eb2', u'build': {u'id': u'cm_n17-2/system/6762'}, u'snapshot_id': u'456', u'_created': u'Thu, 27 Jul 2017 13:38:07 GMT', u'_id': u'5979ecbfe0a14a0001e20eb3', u'_etag': u'cf607760720f05b3174d6ff2f503b4aa20c1c228', u'snapshot_status': u'available'}], u'lab_name': u'SprintLab6080', u'_links': {u'self': {u'href': u'labs/5979ecbfe0a14a0001e20eb2', u'title': u'Lab'}}, u'_created': u'Thu, 27 Jul 2017 13:38:07 GMT', u'_id': u'5979ecbfe0a14a0001e20eb2', u'_etag': u'724d40ee6caefc21a3f56425dc7bb99b9a3c1004'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"SprintLab6080"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        elif  json_id == 1:
            content = json.dumps({u'_updated': u'Thu, 10 Aug 2017 05:12:10 GMT', u'_links': {u'self': {u'href': u'reservations/598beb2ae0a14a0001e20f94', u'title': u'Reservation'}}, u'_created': u'Thu, 10 Aug 2017 05:12:10 GMT', u'_status': u'OK', u'_id': u'598beb2ae0a14a0001e20f94', u'_etag': u'1c317047ccd3df7efcc833baad7ae1da8770be1e'})
            status_code = 200
        elif  json_id == 2:
            content = None
            status_code = 500
        self.mock_admin_remove_labs_NOK_one_lab_one_NOK_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|states|reservations).*')
    def mock_api_admin_remove_labs_NOK_several_labs_one_NOK(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_admin_remove_labs_NOK_several_labs_one_NOK_json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Thu, 27 Jul 2017 13:38:07 GMT', u'lab_type': u'other', u'states': [{u'_updated': u'Thu, 27 Jul 2017 13:38:07 GMT', u'lab': u'5979ecbfe0a14a0001e20eb2', u'build': {u'id': u'cm_n17-2/system/6762'}, u'snapshot_id': u'456', u'_created': u'Thu, 27 Jul 2017 13:38:07 GMT', u'_id': u'5979ecbfe0a14a0001e20eb3', u'_etag': u'cf607760720f05b3174d6ff2f503b4aa20c1c228', u'snapshot_status': u'available'}], u'lab_name': u'SprintLab6080', u'_links': {u'self': {u'href': u'labs/5979ecbfe0a14a0001e20eb2', u'title': u'Lab'}}, u'_created': u'Thu, 27 Jul 2017 13:38:07 GMT', u'_id': u'5979ecbfe0a14a0001e20eb2', u'_etag': u'724d40ee6caefc21a3f56425dc7bb99b9a3c1004'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"SprintLab6080"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        elif self.mock_admin_remove_labs_NOK_several_labs_one_NOK_json_id == 1:
            content = json.dumps({u'_updated': u'Thu, 10 Aug 2017 05:12:10 GMT', u'_links': {u'self': {u'href': u'reservations/598beb2ae0a14a0001e20f94', u'title': u'Reservation'}}, u'_created': u'Thu, 10 Aug 2017 05:12:10 GMT', u'_status': u'OK', u'_id': u'598beb2ae0a14a0001e20f94', u'_etag': u'1c317047ccd3df7efcc833baad7ae1da8770be1e'})
            status_code = 200
        elif self.mock_admin_remove_labs_NOK_several_labs_one_NOK_json_id == 2:
            content = None
            status_code = 204
        elif self.mock_admin_remove_labs_NOK_several_labs_one_NOK_json_id == 3:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Thu, 27 Jul 2017 13:38:08 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Thu, 27 Jul 2017 13:38:08 GMT', u'lab': u'5979ecc0e0a14a0001e20eb6', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'snapshot_id': u'956', u'_created': u'Thu, 27 Jul 2017 13:38:08 GMT', u'_id': u'5979ecc0e0a14a0001e20eb7', u'_etag': u'5641e94bc405906bc3fa6ee21713dff70cf5870c', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab9879', u'_links': {u'self': {u'href': u'labs/5979ecc0e0a14a0001e20eb6', u'title': u'Lab'}}, u'_created': u'Thu, 27 Jul 2017 13:38:08 GMT', u'_id': u'5979ecc0e0a14a0001e20eb6', u'_etag': u'd094269911b4aa839796f3eae0a5c0979a5d22cb'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab9879"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        elif self.mock_admin_remove_labs_NOK_several_labs_one_NOK_json_id == 4:
            content = json.dumps({u'_updated': u'Thu, 10 Aug 2017 05:12:10 GMT', u'_links': {u'self': {u'href': u'reservations/598beb2ae0a14a0001e20f94', u'title': u'Reservation'}}, u'_created': u'Thu, 10 Aug 2017 05:12:10 GMT', u'_status': u'OK', u'_id': u'598beb2ae0a14a0001e20f94', u'_etag': u'1c317047ccd3df7efcc833baad7ae1da8770be1e'})
            status_code = 200
        elif self.mock_admin_remove_labs_NOK_several_labs_one_NOK_json_id == 5:
            content = None
            status_code = 204
        elif self.mock_admin_remove_labs_NOK_several_labs_one_NOK_json_id == 6:
#            content = json.dumps({u'_items': [{u'status': u'reverting_state', u'_updated': u'Thu, 27 Jul 2017 10:55:49 GMT', u'states': [{u'_updated': u'Thu, 27 Jul 2017 10:55:49 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.166'}, u'snapshot_id': u'56', u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20e9d', u'_etag': u'f596e1ec27bcba752867ff3d12435ec8c61a7402', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab8610', u'_links': {u'self': {u'href': u'labs/5979c6b5e0a14a0001e20e9c', u'title': u'Lab'}}, u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20e9c', u'_etag': u'01991d4591635a4cdd3adb1726dab4448e297d9a'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab8610"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            print "PPP: '{}'".format(self.mock_admin_remove_labs_NOK_several_labs_one_NOK_json_id )
            content = json.dumps({u'_items': [{u'status': u'reverting_state', u'_updated': u'Thu, 27 Jul 2017 10:55:49 GMT', u'lab_type': u'vsprint', u'states': [{u'_updated': u'Thu, 27 Jul 2017 10:55:49 GMT', u'lab': u'5979c6b5e0a14a0001e20ea5', u'build': {u'id': u'netact/product/99.17.03.0.004'}, u'snapshot_id': u'7456', u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20ea6', u'_etag': u'e041a1b167ab67021911279bc1d9f3d16dbd5764', u'snapshot_status': u'available'}, {u'_updated': u'Thu, 27 Jul 2017 10:55:49 GMT', u'lab': u'5979c6b5e0a14a0001e20ea5', u'build': {u'id': u'netact/product/99.17.03.0.424'}, u'snapshot_id': u'7456', u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20ea7', u'_etag': u'e4fe48998722993975030dd309dbc7bd8d7e5d49', u'snapshot_status': u'available'}, {u'_updated': u'Thu, 27 Jul 2017 10:55:49 GMT', u'lab': u'5979c6b5e0a14a0001e20ea5', u'build': {u'id': u'netact/product/99.17.03.0.645'}, u'snapshot_id': u'7456', u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20ea8', u'_etag': u'24ddb737f362f040b4cceff19e6593152929f6ec', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab8610', u'_links': {u'self': {u'href': u'labs/5979c6b5e0a14a0001e20ea5', u'title': u'Lab'}}, u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'reservation': {u'username': u'testuser', u'_updated': u'Thu, 27 Jul 2017 10:55:49 GMT', u'lab': u'5979c6b5e0a14a0001e20ea5', u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20ea9', u'_etag': u'ac5a9fbbffccdbdd3a601b387c3cec6c50297437'}, u'_id': u'5979c6b5e0a14a0001e20ea5', u'_etag': u'abeef5f172662b7ff1a20089bf594c17e5e9bf0d'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab8610"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        elif self.mock_admin_remove_labs_NOK_several_labs_one_NOK_json_id == 7:
            content = json.dumps({u'_items': [{u'status': u'state_operation_failed', u'_updated': u'Thu, 27 Jul 2017 10:55:49 GMT', u'states': [{u'_updated': u'Thu, 27 Jul 2017 10:55:49 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.166'}, u'snapshot_id': u'56', u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20e9d', u'_etag': u'f596e1ec27bcba752867ff3d12435ec8c61a7402', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab8610', u'_links': {u'self': {u'href': u'labs/5979c6b5e0a14a0001e20e9c', u'title': u'Lab'}}, u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20e9c', u'_etag': u'01991d4591635a4cdd3adb1726dab4448e297d9a'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab8610"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        elif self.mock_admin_remove_labs_NOK_several_labs_one_NOK_json_id == 8:
            content = json.dumps({u'_updated': u'Thu, 10 Aug 2017 05:12:10 GMT', u'_links': {u'self': {u'href': u'reservations/598beb2ae0a14a0001e20f94', u'title': u'Reservation'}}, u'_created': u'Thu, 10 Aug 2017 05:12:10 GMT', u'_status': u'OK', u'_id': u'598beb2ae0a14a0001e20f94', u'_etag': u'1c317047ccd3df7efcc833baad7ae1da8770be1e'})
            status_code = 200
        elif self.mock_admin_remove_labs_NOK_several_labs_one_NOK_json_id == 9:
            content = None
            status_code = 204
        self.mock_admin_remove_labs_NOK_several_labs_one_NOK_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|states).*')
    def mock_api_admin_remove_labs_NOK_several_labs_all_NOK(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        status_code = 200
        if self.mock_admin_remove_labs_NOK_several_labs_all_NOK_json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'reverting_state', u'_updated': u'Thu, 27 Jul 2017 10:55:49 GMT', u'lab_type': u'vsprint', u'states': [{u'_updated': u'Thu, 27 Jul 2017 10:55:49 GMT', u'lab': u'5979c6b5e0a14a0001e20ea5', u'build': {u'id': u'netact/product/99.17.03.0.004'}, u'snapshot_id': u'7456', u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20ea6', u'_etag': u'e041a1b167ab67021911279bc1d9f3d16dbd5764', u'snapshot_status': u'available'}, {u'_updated': u'Thu, 27 Jul 2017 10:55:49 GMT', u'lab': u'5979c6b5e0a14a0001e20ea5', u'build': {u'id': u'netact/product/99.17.03.0.424'}, u'snapshot_id': u'7456', u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20ea7', u'_etag': u'e4fe48998722993975030dd309dbc7bd8d7e5d49', u'snapshot_status': u'available'}, {u'_updated': u'Thu, 27 Jul 2017 10:55:49 GMT', u'lab': u'5979c6b5e0a14a0001e20ea5', u'build': {u'id': u'netact/product/99.17.03.0.645'}, u'snapshot_id': u'7456', u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20ea8', u'_etag': u'24ddb737f362f040b4cceff19e6593152929f6ec', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab8610', u'_links': {u'self': {u'href': u'labs/5979c6b5e0a14a0001e20ea5', u'title': u'Lab'}}, u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'reservation': {u'username': u'testuser', u'_updated': u'Thu, 27 Jul 2017 10:55:49 GMT', u'lab': u'5979c6b5e0a14a0001e20ea5', u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20ea9', u'_etag': u'ac5a9fbbffccdbdd3a601b387c3cec6c50297437'}, u'_id': u'5979c6b5e0a14a0001e20ea5', u'_etag': u'abeef5f172662b7ff1a20089bf594c17e5e9bf0d'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab8610"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        elif self.mock_admin_remove_labs_NOK_several_labs_all_NOK_json_id == 1:
            content = json.dumps({u'_items': [{u'status': u'reverting_state', u'_updated': u'Thu, 27 Jul 2017 10:55:49 GMT', u'lab_type': u'vsprint', u'states': [{u'_updated': u'Thu, 27 Jul 2017 10:55:49 GMT', u'lab': u'5979c6b5e0a14a0001e20ea5', u'build': {u'id': u'netact/product/99.17.03.0.004'}, u'snapshot_id': u'7456', u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20ea6', u'_etag': u'e041a1b167ab67021911279bc1d9f3d16dbd5764', u'snapshot_status': u'available'}, {u'_updated': u'Thu, 27 Jul 2017 10:55:49 GMT', u'lab': u'5979c6b5e0a14a0001e20ea5', u'build': {u'id': u'netact/product/99.17.03.0.424'}, u'snapshot_id': u'7456', u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20ea7', u'_etag': u'e4fe48998722993975030dd309dbc7bd8d7e5d49', u'snapshot_status': u'available'}, {u'_updated': u'Thu, 27 Jul 2017 10:55:49 GMT', u'lab': u'5979c6b5e0a14a0001e20ea5', u'build': {u'id': u'netact/product/99.17.03.0.645'}, u'snapshot_id': u'7456', u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20ea8', u'_etag': u'24ddb737f362f040b4cceff19e6593152929f6ec', u'snapshot_status': u'available'}], u'lab_name': u'vSprint1429', u'_links': {u'self': {u'href': u'labs/5979c6b5e0a14a0001e20ea5', u'title': u'Lab'}}, u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'reservation': {u'username': u'testuser', u'_updated': u'Thu, 27 Jul 2017 10:55:49 GMT', u'lab': u'5979c6b5e0a14a0001e20ea5', u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20ea9', u'_etag': u'ac5a9fbbffccdbdd3a601b387c3cec6c50297437'}, u'_id': u'5979c6b5e0a14a0001e20ea5', u'_etag': u'abeef5f172662b7ff1a20089bf594c17e5e9bf0d'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"vSprint1429"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        elif self.mock_admin_remove_labs_NOK_several_labs_all_NOK_json_id == 2:
            content = json.dumps({u'_items': [{u'status': u'reverting_state', u'_updated': u'Tue, 25 Jul 2017 10:27:23 GMT', u'lab_type': u'vsprint', u'states': [{u'_updated': u'Tue, 25 Jul 2017 10:27:23 GMT', u'lab': u'59771d0be0a14a0001e20e8b', u'build': {u'id': u'netact/product/99.17.03.0.004'}, u'snapshot_id': u'7456', u'_created': u'Tue, 25 Jul 2017 10:27:23 GMT', u'_id': u'59771d0be0a14a0001e20e8c', u'_etag': u'e287c9ef4a55f678905ce822836292b1ebd732f7', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 25 Jul 2017 10:27:23 GMT', u'lab': u'59771d0be0a14a0001e20e8b', u'build': {u'id': u'netact/product/99.17.03.0.424'}, u'snapshot_id': u'7456', u'_created': u'Tue, 25 Jul 2017 10:27:23 GMT', u'_id': u'59771d0be0a14a0001e20e8d', u'_etag': u'7b919328dd71a640b3a6b8fa44696314c37b3f4a', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 25 Jul 2017 10:27:23 GMT', u'lab': u'59771d0be0a14a0001e20e8b', u'build': {u'id': u'netact/product/99.17.03.0.645'}, u'snapshot_id': u'7456', u'_created': u'Tue, 25 Jul 2017 10:27:23 GMT', u'_id': u'59771d0be0a14a0001e20e8e', u'_etag': u'dd72d1f6f6621770f083081635e989c165d947ef', u'snapshot_status': u'available'}], u'lab_name': u'vSprint8526', u'_links': {u'self': {u'href': u'labs/59771d0be0a14a0001e20e8b', u'title': u'Lab'}}, u'_created': u'Tue, 25 Jul 2017 10:27:23 GMT', u'reservation': {u'username': u'testuser', u'_updated': u'Tue, 25 Jul 2017 10:27:23 GMT', u'lab': u'59771d0be0a14a0001e20e8b', u'_created': u'Tue, 25 Jul 2017 10:27:23 GMT', u'_id': u'59771d0be0a14a0001e20e8f', u'_etag': u'a6abfc434a9aa0200ed4e2c69f4aee3c135e42db'}, u'_id': u'59771d0be0a14a0001e20e8b', u'_etag': u'50d2ff8aa6e6037570dc550db42af6f8dfe23d0d'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"vSprint8526"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        self.mock_admin_remove_labs_NOK_several_labs_all_NOK_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|states).*')
    def mock_api_admin_remove_labs_NOK_lab_does_not_exist(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_admin_remove_labs_NOK_lab_does_not_exist_json_id == 0:
            content = json.dumps({u'_items': [], u'_links': {u'self': {u'href': u'labs', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 0, u'page': 1}})
            status_code = 200
        self.mock_admin_remove_labs_NOK_lab_does_not_exist_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|states).*')
    def mock_api_admin_remove_labs_NOK_user_not_allowed_to_remove(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        content = ""
        if self.mock_admin_remove_labs_NOK_user_not_allowed_to_remove_json_id == 0:
            status_code = 200
        elif self.mock_admin_remove_labs_NOK_user_not_allowed_to_remove_json_id == 1:
            status_code = 200
        elif self.mock_admin_remove_labs_NOK_user_not_allowed_to_remove_json_id == 2:
            status_code = 200
        self.mock_admin_remove_labs_NOK_user_not_allowed_to_remove_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_admin_add_lab_OK_name_given(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_admin_add_lab_OK_name_given_json_id == 0:
            content = json.dumps({u'_items': [], u'_links': {u'self': {u'href': u'labs', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 0, u'page': 1}})
            status_code = 200
        elif self.mock_admin_add_lab_OK_name_given_json_id == 1:
            content = json.dumps({u'_updated': u'Fri, 28 Jul 2017 10:39:15 GMT', u'_links': {u'self': {u'href': u'labs/597b1453e0a14a0001e20ed2', u'title': u'Lab'}}, u'_created': u'Fri, 28 Jul 2017 10:39:15 GMT', u'_status': u'OK', u'_id': u'597b1453e0a14a0001e20ed2', u'_etag': u'3fdbc5a299de1294ace17427c74eb46905b5e58b'})
            status_code = 200
        self.mock_admin_add_lab_OK_name_given_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_admin_add_lab_OK_name_type_given(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_admin_add_lab_OK_name_type_given_json_id == 0:
            content = json.dumps({u'_items': [], u'_links': {u'self': {u'href': u'labs', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 0, u'page': 1}})
            status_code = 200
        elif self.mock_admin_add_lab_OK_name_type_given_json_id == 1:
            content = json.dumps({u'_updated': u'Fri, 28 Jul 2017 10:39:15 GMT', u'_links': {u'self': {u'href': u'labs/597b1453e0a14a0001e20ed2', u'title': u'Lab'}}, u'_created': u'Fri, 28 Jul 2017 10:39:15 GMT', u'_status': u'OK', u'_id': u'597b1453e0a14a0001e20ed2', u'_etag': u'3fdbc5a299de1294ace17427c74eb46905b5e58b'})
            status_code = 200
        self.mock_admin_add_lab_OK_name_type_given_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_admin_add_lab_OK_name_type_status_given(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_admin_add_lab_OK_name_type_status_given_json_id == 0:
            content = json.dumps({u'_items': [], u'_links': {u'self': {u'href': u'labs', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 0, u'page': 1}})
            status_code = 200
        elif self.mock_admin_add_lab_OK_name_type_status_given_json_id == 1:
            content = json.dumps({u'_updated': u'Fri, 28 Jul 2017 10:39:15 GMT', u'_links': {u'self': {u'href': u'labs/597b1453e0a14a0001e20ed2', u'title': u'Lab'}}, u'_created': u'Fri, 28 Jul 2017 10:39:15 GMT', u'_status': u'OK', u'_id': u'597b1453e0a14a0001e20ed2', u'_etag': u'3fdbc5a299de1294ace17427c74eb46905b5e58b'})
            status_code = 200
        self.mock_admin_add_lab_OK_name_type_status_given_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_admin_add_lab_NOK_lab_already_exists(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_admin_add_lab_NOK_lab_already_exists_json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Fri, 28 Jul 2017 10:39:15 GMT', u'lab_name': u'sprintlab283', u'_links': {u'self': {u'href': u'labs/597b1453e0a14a0001e20ed2', u'title': u'Lab'}}, u'_created': u'Fri, 28 Jul 2017 10:39:15 GMT', u'_id': u'597b1453e0a14a0001e20ed2', u'_etag': u'3fdbc5a299de1294ace17427c74eb46905b5e58b'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"sprintlab283"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        self.mock_admin_add_lab_NOK_lab_already_exists_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_admin_add_lab_NOK_invalid_lab_type(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_admin_add_lab_NOK_invalid_lab_type_json_id == 0:
            content = json.dumps({u'_items': [], u'_links': {u'self': {u'href': u'labs', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 0, u'page': 1}})
            status_code = 200
        elif self.mock_admin_add_lab_NOK_invalid_lab_type_json_id == 1:
            content = json.dumps({u'_updated': u'Fri, 28 Jul 2017 10:39:15 GMT', u'_links': {u'self': {u'href': u'labs/597b1453e0a14a0001e20ed2', u'title': u'Lab'}}, u'_created': u'Fri, 28 Jul 2017 10:39:15 GMT', u'_status': u'OK', u'_id': u'597b1453e0a14a0001e20ed2', u'_etag': u'3fdbc5a299de1294ace17427c74eb46905b5e58b'})
            status_code = 200
        self.mock_admin_add_lab_NOK_invalid_lab_type_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_admin_add_lab_NOK_invalid_lab_status(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_admin_add_lab_NOK_invalid_lab_status_json_id == 0:
            content = json.dumps({u'_items': [], u'_links': {u'self': {u'href': u'labs', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 0, u'page': 1}})
            status_code = 200
        elif self.mock_admin_add_lab_NOK_invalid_lab_status_json_id == 1:
            content = json.dumps({u'_updated': u'Fri, 28 Jul 2017 10:39:15 GMT', u'_links': {u'self': {u'href': u'labs/597b1453e0a14a0001e20ed2', u'title': u'Lab'}}, u'_created': u'Fri, 28 Jul 2017 10:39:15 GMT', u'_status': u'OK', u'_id': u'597b1453e0a14a0001e20ed2', u'_etag': u'3fdbc5a299de1294ace17427c74eb46905b5e58b'})
            status_code = 200
        self.mock_admin_add_lab_NOK_invalid_lab_status_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_admin_add_lab_NOK_username_not_valid(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_admin_add_lab_NOK_username_not_valid_json_id == 0:
            content = json.dumps({u'_items': [], u'_links': {u'self': {u'href': u'labs', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 0, u'page': 1}})
            status_code = 200
        elif self.mock_admin_add_lab_NOK_username_not_valid_json_id == 1:
            content = json.dumps({u'_updated': u'Fri, 28 Jul 2017 10:39:15 GMT', u'_links': {u'self': {u'href': u'labs/597b1453e0a14a0001e20ed2', u'title': u'Lab'}}, u'_created': u'Fri, 28 Jul 2017 10:39:15 GMT', u'_status': u'OK', u'_id': u'597b1453e0a14a0001e20ed2', u'_etag': u'3fdbc5a299de1294ace17427c74eb46905b5e58b'})
            status_code = 200
        self.mock_admin_add_lab_NOK_username_not_valid_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|states).*')
    def mock_api_create_snapshots_OK_one_snapshot(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_create_test_snapshots_OK_one_snapshot_json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Tue, 01 Aug 2017 05:26:50 GMT', u'lab_type': u'sprint', u'states': [{u'_updated': u'Tue, 01 Aug 2017 08:35:14 GMT', u'lab': u'5980111ae0a14a0001e20edf', u'build': {u'id': u'NetAct16_5_P8_vSphere_Updated_NE_S/W_updated_vSpehereLicenseInstalled'}, u'snapshot_id': u'SprintLab283-1483597803', u'_created': u'Tue, 01 Aug 2017 05:26:50 GMT', u'_id': u'5980111ae0a14a0001e20ee0', u'_etag': u'96fa0d41b2d28918e889e9ebf82fe575bf1f0f48', u'snapshot_status': u'queued'}], u'lab_name': u'sprintlab283', u'_links': {u'self': {u'href': u'labs/5980111ae0a14a0001e20edf', u'title': u'Lab'}}, u'_created': u'Tue, 01 Aug 2017 05:26:50 GMT', u'_id': u'5980111ae0a14a0001e20edf', u'_etag': u'db4e20e9f893e32570366e8397c85e65c8ed51ab'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"sprintlab283"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        elif self.mock_create_test_snapshots_OK_one_snapshot_json_id == 1:
            content = json.dumps({u'_updated': u'Wed, 02 Aug 2017 11:19:11 GMT', u'_links': {u'self': {u'href': u'states/5981b52fe0a14a0001e20f31', u'title': u'State'}}, u'_created': u'Wed, 02 Aug 2017 11:19:11 GMT', u'_status': u'OK', u'_id': u'5981b52fe0a14a0001e20f31', u'_etag': u'6733ea4099abcd7f9570d18ee4c6f01960376607'})
            status_code = 200
        self.mock_create_test_snapshots_OK_one_snapshot_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|states).*')
    def mock_api_create_snapshots_OK_several_snapshots(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_create_test_snapshots_OK_several_snapshots_json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Tue, 01 Aug 2017 05:26:50 GMT', u'lab_type': u'sprint', u'states': [{u'_updated': u'Tue, 01 Aug 2017 08:35:14 GMT', u'lab': u'5980111ae0a14a0001e20edf', u'build': {u'id': u'NetAct16_5_P8_vSphere_Updated_NE_S/W_updated_vSpehereLicenseInstalled'}, u'snapshot_id': u'SprintLab283-1483597803', u'_created': u'Tue, 01 Aug 2017 05:26:50 GMT', u'_id': u'5980111ae0a14a0001e20ee0', u'_etag': u'96fa0d41b2d28918e889e9ebf82fe575bf1f0f48', u'snapshot_status': u'queued'}, {u'_updated': u'Tue, 01 Aug 2017 05:26:50 GMT', u'lab': u'5980111ae0a14a0001e20edf', u'build': {u'id': u'NetAct_17.2_P8'}, u'snapshot_id': u'SprintLab283-1490852297', u'_created': u'Tue, 01 Aug 2017 05:26:50 GMT', u'_id': u'5980111ae0a14a0001e20ee1', u'_etag': u'8b5d77afb0607657787d83cec018059cf994e7b6', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 05:26:50 GMT', u'lab': u'5980111ae0a14a0001e20edf', u'build': {u'id': u'NetAct_17.2_P8_w_bsc17_adapt'}, u'snapshot_id': u'SprintLab283-1499326517', u'_created': u'Tue, 01 Aug 2017 05:26:50 GMT', u'_id': u'5980111ae0a14a0001e20ee2', u'_etag': u'e3128637fa661d563b1b4dad018e3068dd052ab0', u'snapshot_status': u'available'}], u'lab_name': u'sprintlab283', u'_links': {u'self': {u'href': u'labs/5980111ae0a14a0001e20edf', u'title': u'Lab'}}, u'_created': u'Tue, 01 Aug 2017 05:26:50 GMT', u'_id': u'5980111ae0a14a0001e20edf', u'_etag': u'db4e20e9f893e32570366e8397c85e65c8ed51ab'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"sprintlab283"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        elif self.mock_create_test_snapshots_OK_several_snapshots_json_id == 1:
            content = json.dumps({u'_updated': u'Wed, 02 Aug 2017 11:19:11 GMT', u'_links': {u'self': {u'href': u'states/5981b52fe0a14a0001e20f31', u'title': u'State'}}, u'_created': u'Wed, 02 Aug 2017 11:19:11 GMT', u'_status': u'OK', u'_id': u'5981b52fe0a14a0001e20f31', u'_etag': u'6733ea4099abcd7f9570d18ee4c6f01960376607'})
            status_code = 200
        elif self.mock_create_test_snapshots_OK_several_snapshots_json_id == 2:
            content = json.dumps({u'_updated': u'Wed, 02 Aug 2017 11:19:11 GMT', u'_links': {u'self': {u'href': u'states/5981b52fe0a14a0001e20f31', u'title': u'State'}}, u'_created': u'Wed, 02 Aug 2017 11:19:11 GMT', u'_status': u'OK', u'_id': u'5981b52fe0a14a0001e20f31', u'_etag': u'6733ea4099abcd7f9570d18ee4c6f01960376607'})
            status_code = 200
        elif self.mock_create_test_snapshots_OK_several_snapshots_json_id == 3:
            content = json.dumps({u'_updated': u'Wed, 02 Aug 2017 11:19:11 GMT', u'_links': {u'self': {u'href': u'states/5981b52fe0a14a0001e20f31', u'title': u'State'}}, u'_created': u'Wed, 02 Aug 2017 11:19:11 GMT', u'_status': u'OK', u'_id': u'5981b52fe0a14a0001e20f31', u'_etag': u'6733ea4099abcd7f9570d18ee4c6f01960376607'})
            status_code = 200
        self.mock_create_test_snapshots_OK_several_snapshots_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|states).*')
    def mock_api_create_snapshots_NOK_wrong_username(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_create_test_snapshots_NOK_wrong_username_json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Tue, 01 Aug 2017 05:26:50 GMT', u'lab_type': u'sprint', u'states': [{u'_updated': u'Tue, 01 Aug 2017 08:35:14 GMT', u'lab': u'5980111ae0a14a0001e20edf', u'build': {u'id': u'NetAct16_5_P8_vSphere_Updated_NE_S/W_updated_vSpehereLicenseInstalled'}, u'snapshot_id': u'SprintLab283-1483597803', u'_created': u'Tue, 01 Aug 2017 05:26:50 GMT', u'_id': u'5980111ae0a14a0001e20ee0', u'_etag': u'96fa0d41b2d28918e889e9ebf82fe575bf1f0f48', u'snapshot_status': u'queued'}, {u'_updated': u'Tue, 01 Aug 2017 05:26:50 GMT', u'lab': u'5980111ae0a14a0001e20edf', u'build': {u'id': u'NetAct_17.2_P8'}, u'snapshot_id': u'SprintLab283-1490852297', u'_created': u'Tue, 01 Aug 2017 05:26:50 GMT', u'_id': u'5980111ae0a14a0001e20ee1', u'_etag': u'8b5d77afb0607657787d83cec018059cf994e7b6', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 05:26:50 GMT', u'lab': u'5980111ae0a14a0001e20edf', u'build': {u'id': u'NetAct_17.2_P8_w_bsc17_adapt'}, u'snapshot_id': u'SprintLab283-1499326517', u'_created': u'Tue, 01 Aug 2017 05:26:50 GMT', u'_id': u'5980111ae0a14a0001e20ee2', u'_etag': u'e3128637fa661d563b1b4dad018e3068dd052ab0', u'snapshot_status': u'available'}], u'lab_name': u'sprintlab283', u'_links': {u'self': {u'href': u'labs/5980111ae0a14a0001e20edf', u'title': u'Lab'}}, u'_created': u'Tue, 01 Aug 2017 05:26:50 GMT', u'_id': u'5980111ae0a14a0001e20edf', u'_etag': u'db4e20e9f893e32570366e8397c85e65c8ed51ab'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"sprintlab283"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        elif self.mock_create_test_snapshots_NOK_wrong_username_json_id == 1:
            content = json.dumps({u'_updated': u'Wed, 02 Aug 2017 11:19:11 GMT', u'_links': {u'self': {u'href': u'states/5981b52fe0a14a0001e20f31', u'title': u'State'}}, u'_created': u'Wed, 02 Aug 2017 11:19:11 GMT', u'_status': u'OK', u'_id': u'5981b52fe0a14a0001e20f31', u'_etag': u'6733ea4099abcd7f9570d18ee4c6f01960376607'})
            status_code = 200
        elif self.mock_create_test_snapshots_NOK_wrong_username_json_id == 2:
            content = json.dumps({u'_updated': u'Wed, 02 Aug 2017 11:19:11 GMT', u'_links': {u'self': {u'href': u'states/5981b52fe0a14a0001e20f31', u'title': u'State'}}, u'_created': u'Wed, 02 Aug 2017 11:19:11 GMT', u'_status': u'OK', u'_id': u'5981b52fe0a14a0001e20f31', u'_etag': u'6733ea4099abcd7f9570d18ee4c6f01960376607'})
            status_code = 200
        elif self.mock_create_test_snapshots_NOK_wrong_username_json_id == 3:
            content = json.dumps({u'_updated': u'Wed, 02 Aug 2017 11:19:11 GMT', u'_links': {u'self': {u'href': u'states/5981b52fe0a14a0001e20f31', u'title': u'State'}}, u'_created': u'Wed, 02 Aug 2017 11:19:11 GMT', u'_status': u'OK', u'_id': u'5981b52fe0a14a0001e20f31', u'_etag': u'6733ea4099abcd7f9570d18ee4c6f01960376607'})
            status_code = 200
        self.mock_create_test_snapshots_NOK_wrong_username_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|states).*')
    def mock_api_create_snapshots_NOK_lab_does_not_exist(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_create_test_snapshots_NOK_lab_does_not_exist_json_id == 0:
            content = json.dumps({u'_items': [], u'_links': {u'self': {u'href': u'labs', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 0, u'page': 1}})
            status_code = 200
        self.mock_create_test_snapshots_NOK_lab_does_not_exist_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|states).*')
    def mock_api_create_snapshots_NOK_some_snapshots_successful(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_create_test_snapshots_NOK_some_snapshots_successful_json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Tue, 01 Aug 2017 05:26:50 GMT', u'lab_type': u'sprint', u'states': [{u'_updated': u'Tue, 01 Aug 2017 08:35:14 GMT', u'lab': u'5980111ae0a14a0001e20edf', u'build': {u'id': u'NetAct16_5_P8_vSphere_Updated_NE_S/W_updated_vSpehereLicenseInstalled'}, u'snapshot_id': u'SprintLab283-1483597803', u'_created': u'Tue, 01 Aug 2017 05:26:50 GMT', u'_id': u'5980111ae0a14a0001e20ee0', u'_etag': u'96fa0d41b2d28918e889e9ebf82fe575bf1f0f48', u'snapshot_status': u'queued'}, {u'_updated': u'Tue, 01 Aug 2017 05:26:50 GMT', u'lab': u'5980111ae0a14a0001e20edf', u'build': {u'id': u'NetAct_17.2_P8'}, u'snapshot_id': u'SprintLab283-1490852297', u'_created': u'Tue, 01 Aug 2017 05:26:50 GMT', u'_id': u'5980111ae0a14a0001e20ee1', u'_etag': u'8b5d77afb0607657787d83cec018059cf994e7b6', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 05:26:50 GMT', u'lab': u'5980111ae0a14a0001e20edf', u'build': {u'id': u'NetAct_17.2_P8_w_bsc17_adapt'}, u'snapshot_id': u'SprintLab283-1499326517', u'_created': u'Tue, 01 Aug 2017 05:26:50 GMT', u'_id': u'5980111ae0a14a0001e20ee2', u'_etag': u'e3128637fa661d563b1b4dad018e3068dd052ab0', u'snapshot_status': u'available'}], u'lab_name': u'sprintlab283', u'_links': {u'self': {u'href': u'labs/5980111ae0a14a0001e20edf', u'title': u'Lab'}}, u'_created': u'Tue, 01 Aug 2017 05:26:50 GMT', u'_id': u'5980111ae0a14a0001e20edf', u'_etag': u'db4e20e9f893e32570366e8397c85e65c8ed51ab'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"sprintlab283"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        elif self.mock_create_test_snapshots_NOK_some_snapshots_successful_json_id == 1:
            content = json.dumps({u'_updated': u'Wed, 02 Aug 2017 11:19:11 GMT', u'_links': {u'self': {u'href': u'states/5981b52fe0a14a0001e20f31', u'title': u'State'}}, u'_created': u'Wed, 02 Aug 2017 11:19:11 GMT', u'_status': u'OK', u'_id': u'5981b52fe0a14a0001e20f31', u'_etag': u'6733ea4099abcd7f9570d18ee4c6f01960376607'})
            status_code = 200
        elif self.mock_create_test_snapshots_NOK_some_snapshots_successful_json_id == 2:
            content = json.dumps({"_status": "ERR", "_issues": {"lab": "required field", "la": "unknown field"}, "_error": {"message": "Insertion failure: 1 document(s) contain(s) error(s)", "code": 422}})
            status_code = 422
        elif self.mock_create_test_snapshots_NOK_some_snapshots_successful_json_id == 3:
            content = json.dumps({u'_updated': u'Wed, 02 Aug 2017 11:19:11 GMT', u'_links': {u'self': {u'href': u'states/5981b52fe0a14a0001e20f31', u'title': u'State'}}, u'_created': u'Wed, 02 Aug 2017 11:19:11 GMT', u'_status': u'OK', u'_id': u'5981b52fe0a14a0001e20f31', u'_etag': u'6733ea4099abcd7f9570d18ee4c6f01960376607'})
            status_code = 200
        self.mock_create_test_snapshots_NOK_some_snapshots_successful_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|states).*')
    def mock_api_create_snapshots_NOK_all_snapshots_failed(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_create_test_snapshots_NOK_all_snapshots_failed_json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Tue, 01 Aug 2017 05:26:50 GMT', u'lab_type': u'sprint', u'states': [{u'_updated': u'Tue, 01 Aug 2017 08:35:14 GMT', u'lab': u'5980111ae0a14a0001e20edf', u'build': {u'id': u'NetAct16_5_P8_vSphere_Updated_NE_S/W_updated_vSpehereLicenseInstalled'}, u'snapshot_id': u'SprintLab283-1483597803', u'_created': u'Tue, 01 Aug 2017 05:26:50 GMT', u'_id': u'5980111ae0a14a0001e20ee0', u'_etag': u'96fa0d41b2d28918e889e9ebf82fe575bf1f0f48', u'snapshot_status': u'queued'}, {u'_updated': u'Tue, 01 Aug 2017 05:26:50 GMT', u'lab': u'5980111ae0a14a0001e20edf', u'build': {u'id': u'NetAct_17.2_P8'}, u'snapshot_id': u'SprintLab283-1490852297', u'_created': u'Tue, 01 Aug 2017 05:26:50 GMT', u'_id': u'5980111ae0a14a0001e20ee1', u'_etag': u'8b5d77afb0607657787d83cec018059cf994e7b6', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 05:26:50 GMT', u'lab': u'5980111ae0a14a0001e20edf', u'build': {u'id': u'NetAct_17.2_P8_w_bsc17_adapt'}, u'snapshot_id': u'SprintLab283-1499326517', u'_created': u'Tue, 01 Aug 2017 05:26:50 GMT', u'_id': u'5980111ae0a14a0001e20ee2', u'_etag': u'e3128637fa661d563b1b4dad018e3068dd052ab0', u'snapshot_status': u'available'}], u'lab_name': u'sprintlab283', u'_links': {u'self': {u'href': u'labs/5980111ae0a14a0001e20edf', u'title': u'Lab'}}, u'_created': u'Tue, 01 Aug 2017 05:26:50 GMT', u'_id': u'5980111ae0a14a0001e20edf', u'_etag': u'db4e20e9f893e32570366e8397c85e65c8ed51ab'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"sprintlab283"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        elif self.mock_create_test_snapshots_NOK_all_snapshots_failed_json_id == 1:
            content = json.dumps({"_status": "ERR", "_issues": {"lab": "required field", "la": "unknown field"}, "_error": {"message": "Insertion failure: 1 document(s) contain(s) error(s)", "code": 422}})
            status_code = 422
        elif self.mock_create_test_snapshots_NOK_all_snapshots_failed_json_id == 2:
            content = json.dumps({"_status": "ERR", "_issues": {"lab": "required field", "la": "unknown field"}, "_error": {"message": "Insertion failure: 1 document(s) contain(s) error(s)", "code": 422}})
            status_code = 422
        elif self.mock_create_test_snapshots_NOK_all_snapshots_failed_json_id == 3:
            content = json.dumps({"_status": "ERR", "_issues": {"lab": "required field", "la": "unknown field"}, "_error": {"message": "Insertion failure: 1 document(s) contain(s) error(s)", "code": 422}})
            status_code = 422
        self.mock_create_test_snapshots_NOK_all_snapshots_failed_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_admin_patch_item_OK_csv_one_parameter(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_admin_patch_item_OK_csv_one_parameter_json_id == 0:
            content = json.dumps({u'status': u'initializing', u'_updated': u'Thu, 03 Aug 2017 12:35:46 GMT', u'states': [u'5979c6b5e0a14a0001e20e9d', u'5980754ee0a14a0001e20eed', u'5980754ee0a14a0001e20eee', u'5980754ee0a14a0001e20eef', u'59807574e0a14a0001e20ef0', u'59807574e0a14a0001e20ef1', u'59807574e0a14a0001e20ef2'], u'lab_name': u'CloudLab984', u'_links': {u'self': {u'href': u'labs/5979c6b5e0a14a0001e20e9c', u'title': u'Lab'}, u'parent': {u'href': u'/', u'title': u'home'}, u'collection': {u'href': u'labs', u'title': u'labs'}}, u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20e9c', u'_etag': u'ffde6cd098eed63498eec8b614d502f0db785d81'})
            status_code = 200
        elif self.mock_admin_patch_item_OK_csv_one_parameter_json_id == 1:
            content = json.dumps({u'_updated': u'Wed, 02 Aug 2017 11:19:11 GMT', u'_links': {u'self': {u'href': u'states/5981b52fe0a14a0001e20f31', u'title': u'State'}}, u'_created': u'Wed, 02 Aug 2017 11:19:11 GMT', u'_status': u'OK', u'_id': u'5981b52fe0a14a0001e20f31', u'_etag': u'6733ea4099abcd7f9570d18ee4c6f01960376607'})
            status_code = 200
        elif self.mock_admin_patch_item_OK_csv_one_parameter_json_id == 2:
            content = json.dumps({u'status': u'initializing', u'_updated': u'Thu, 03 Aug 2017 12:53:50 GMT', u'states': [{u'_updated': u'Thu, 27 Jul 2017 10:55:49 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.166'}, u'snapshot_id': u'56', u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20e9d', u'_etag': u'f596e1ec27bcba752867ff3d12435ec8c61a7402', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:34:22 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.1585'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:34:22 GMT', u'_id': u'5980754ee0a14a0001e20eed', u'_etag': u'5139608d2c3157d4da0130aa10360eb3cc10dc0f', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:34:22 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.6694'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:34:22 GMT', u'_id': u'5980754ee0a14a0001e20eee', u'_etag': u'7c65ead19b22ff4d1eea616bd31be416fd8b0d36', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:34:22 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.2450'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:34:22 GMT', u'_id': u'5980754ee0a14a0001e20eef', u'_etag': u'e4536cd95c97c42807a46f221c01e0b2a57e711e', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:35:00 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.4258'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:35:00 GMT', u'_id': u'59807574e0a14a0001e20ef0', u'_etag': u'1acd4d917252fd4c46459227ed6e24f072a41979', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:35:00 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.8490'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:35:00 GMT', u'_id': u'59807574e0a14a0001e20ef1', u'_etag': u'b3619bf3bcc98c38a50878d3662698a2564237a4', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:35:00 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.1576'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:35:00 GMT', u'_id': u'59807574e0a14a0001e20ef2', u'_etag': u'3b7962e43352a408148376402c39771c1941b8ba', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab984', u'_links': {u'self': {u'href': u'labs/5979c6b5e0a14a0001e20e9c', u'title': u'Lab'}, u'parent': {u'href': u'/', u'title': u'home'}, u'collection': {u'href': u'labs?pretty=', u'title': u'labs'}}, u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20e9c', u'_etag': u'ef055e8452b25aae9df4b4af2aae2701fc60aa06'})
            status_code = 200
        self.mock_admin_patch_item_OK_csv_one_parameter_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(states).*')
    def mock_api_admin_patch_item_OK_csv_several_parameters(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_admin_patch_item_OK_csv_several_parameters_json_id == 0:
            content = json.dumps({u'_updated': u'Wed, 02 Aug 2017 11:19:11 GMT', u'_links': {u'self': {u'href': u'states/5981b52fe0a14a0001e20f31', u'title': u'State'}}, u'_created': u'Wed, 02 Aug 2017 11:19:11 GMT', u'_status': u'OK', u'_id': u'5981b52fe0a14a0001e20f31', u'_etag': u'6733ea4099abcd7f9570d18ee4c6f01960376607'})
            status_code = 200
        elif self.mock_admin_patch_item_OK_csv_several_parameters_json_id == 1:
            content = json.dumps({u'_updated': u'Fri, 04 Aug 2017 04:48:30 GMT', u'_links': {u'self': {u'href': u'labs/5979c6b5e0a14a0001e20e9c', u'title': u'Lab'}}, u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_status': u'OK', u'_id': u'5979c6b5e0a14a0001e20e9c', u'_etag': u'63aea804e553ff9610cceb641617f0a8fdaf9988'})
            status_code = 200
        elif self.mock_admin_patch_item_OK_csv_several_parameters_json_id == 2:
            content = json.dumps({u'status': u'initializing', u'_updated': u'Thu, 03 Aug 2017 12:53:50 GMT', u'states': [{u'_updated': u'Thu, 27 Jul 2017 10:55:49 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.166'}, u'snapshot_id': u'56', u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20e9d', u'_etag': u'f596e1ec27bcba752867ff3d12435ec8c61a7402', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:34:22 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.1585'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:34:22 GMT', u'_id': u'5980754ee0a14a0001e20eed', u'_etag': u'5139608d2c3157d4da0130aa10360eb3cc10dc0f', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:34:22 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.6694'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:34:22 GMT', u'_id': u'5980754ee0a14a0001e20eee', u'_etag': u'7c65ead19b22ff4d1eea616bd31be416fd8b0d36', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:34:22 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.2450'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:34:22 GMT', u'_id': u'5980754ee0a14a0001e20eef', u'_etag': u'e4536cd95c97c42807a46f221c01e0b2a57e711e', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:35:00 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.4258'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:35:00 GMT', u'_id': u'59807574e0a14a0001e20ef0', u'_etag': u'1acd4d917252fd4c46459227ed6e24f072a41979', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:35:00 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.8490'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:35:00 GMT', u'_id': u'59807574e0a14a0001e20ef1', u'_etag': u'b3619bf3bcc98c38a50878d3662698a2564237a4', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:35:00 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.1576'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:35:00 GMT', u'_id': u'59807574e0a14a0001e20ef2', u'_etag': u'3b7962e43352a408148376402c39771c1941b8ba', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab984', u'_links': {u'self': {u'href': u'labs/5979c6b5e0a14a0001e20e9c', u'title': u'Lab'}, u'parent': {u'href': u'/', u'title': u'home'}, u'collection': {u'href': u'labs?pretty=', u'title': u'labs'}}, u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20e9c', u'_etag': u'ef055e8452b25aae9df4b4af2aae2701fc60aa06'})
            status_code = 200
        self.mock_admin_patch_item_OK_csv_several_parameters_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_admin_patch_item_OK_json_one_parameter(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_admin_patch_item_OK_json_one_parameter_json_id == 0:
            content = json.dumps({u'status': u'initializing', u'_updated': u'Thu, 03 Aug 2017 12:35:46 GMT', u'states': [u'5979c6b5e0a14a0001e20e9d', u'5980754ee0a14a0001e20eed', u'5980754ee0a14a0001e20eee', u'5980754ee0a14a0001e20eef', u'59807574e0a14a0001e20ef0', u'59807574e0a14a0001e20ef1', u'59807574e0a14a0001e20ef2'], u'lab_name': u'CloudLab984', u'_links': {u'self': {u'href': u'labs/5979c6b5e0a14a0001e20e9c', u'title': u'Lab'}, u'parent': {u'href': u'/', u'title': u'home'}, u'collection': {u'href': u'labs', u'title': u'labs'}}, u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20e9c', u'_etag': u'ffde6cd098eed63498eec8b614d502f0db785d81'})
            status_code = 200
        elif self.mock_admin_patch_item_OK_json_one_parameter_json_id == 1:
            content = json.dumps({u'_updated': u'Wed, 02 Aug 2017 11:19:11 GMT', u'_links': {u'self': {u'href': u'labs/5981b52fe0a14a0001e20f31', u'title': u'State'}}, u'_created': u'Wed, 02 Aug 2017 11:19:11 GMT', u'_status': u'OK', u'_id': u'5981b52fe0a14a0001e20f31', u'_etag': u'6733ea4099abcd7f9570d18ee4c6f01960376607'})
            status_code = 200
        elif self.mock_admin_patch_item_OK_json_one_parameter_json_id == 2:
            content = json.dumps({u'status': u'initializing', u'_updated': u'Thu, 03 Aug 2017 12:53:50 GMT', u'states': [{u'_updated': u'Thu, 27 Jul 2017 10:55:49 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.166'}, u'snapshot_id': u'56', u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20e9d', u'_etag': u'f596e1ec27bcba752867ff3d12435ec8c61a7402', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:34:22 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.1585'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:34:22 GMT', u'_id': u'5980754ee0a14a0001e20eed', u'_etag': u'5139608d2c3157d4da0130aa10360eb3cc10dc0f', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:34:22 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.6694'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:34:22 GMT', u'_id': u'5980754ee0a14a0001e20eee', u'_etag': u'7c65ead19b22ff4d1eea616bd31be416fd8b0d36', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:34:22 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.2450'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:34:22 GMT', u'_id': u'5980754ee0a14a0001e20eef', u'_etag': u'e4536cd95c97c42807a46f221c01e0b2a57e711e', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:35:00 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.4258'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:35:00 GMT', u'_id': u'59807574e0a14a0001e20ef0', u'_etag': u'1acd4d917252fd4c46459227ed6e24f072a41979', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:35:00 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.8490'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:35:00 GMT', u'_id': u'59807574e0a14a0001e20ef1', u'_etag': u'b3619bf3bcc98c38a50878d3662698a2564237a4', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:35:00 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.1576'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:35:00 GMT', u'_id': u'59807574e0a14a0001e20ef2', u'_etag': u'3b7962e43352a408148376402c39771c1941b8ba', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab984', u'_links': {u'self': {u'href': u'labs/5979c6b5e0a14a0001e20e9c', u'title': u'Lab'}, u'parent': {u'href': u'/', u'title': u'home'}, u'collection': {u'href': u'labs?pretty=', u'title': u'labs'}}, u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20e9c', u'_etag': u'ef055e8452b25aae9df4b4af2aae2701fc60aa06'})
            status_code = 200
        self.mock_admin_patch_item_OK_json_one_parameter_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_admin_patch_item_OK_json_several_parameters(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_admin_patch_item_OK_json_several_parameters_json_id == 0:
            content = json.dumps({u'status': u'initializing', u'_updated': u'Thu, 03 Aug 2017 12:35:46 GMT', u'states': [u'5979c6b5e0a14a0001e20e9d', u'5980754ee0a14a0001e20eed', u'5980754ee0a14a0001e20eee', u'5980754ee0a14a0001e20eef', u'59807574e0a14a0001e20ef0', u'59807574e0a14a0001e20ef1', u'59807574e0a14a0001e20ef2'], u'lab_name': u'CloudLab984', u'_links': {u'self': {u'href': u'labs/5979c6b5e0a14a0001e20e9c', u'title': u'Lab'}, u'parent': {u'href': u'/', u'title': u'home'}, u'collection': {u'href': u'labs', u'title': u'labs'}}, u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20e9c', u'_etag': u'ffde6cd098eed63498eec8b614d502f0db785d81'})
            status_code = 200
        elif self.mock_admin_patch_item_OK_json_several_parameters_json_id == 1:
            content = json.dumps({u'_updated': u'Wed, 02 Aug 2017 11:19:11 GMT', u'_links': {u'self': {u'href': u'labs/5981b52fe0a14a0001e20f31', u'title': u'State'}}, u'_created': u'Wed, 02 Aug 2017 11:19:11 GMT', u'_status': u'OK', u'_id': u'5981b52fe0a14a0001e20f31', u'_etag': u'6733ea4099abcd7f9570d18ee4c6f01960376607'})
            status_code = 200
        elif self.mock_admin_patch_item_OK_json_several_parameters_json_id == 2:
            content = json.dumps({u'status': u'initializing', u'_updated': u'Thu, 03 Aug 2017 12:53:50 GMT', u'states': [{u'_updated': u'Thu, 27 Jul 2017 10:55:49 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.166'}, u'snapshot_id': u'56', u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20e9d', u'_etag': u'f596e1ec27bcba752867ff3d12435ec8c61a7402', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:34:22 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.1585'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:34:22 GMT', u'_id': u'5980754ee0a14a0001e20eed', u'_etag': u'5139608d2c3157d4da0130aa10360eb3cc10dc0f', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:34:22 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.6694'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:34:22 GMT', u'_id': u'5980754ee0a14a0001e20eee', u'_etag': u'7c65ead19b22ff4d1eea616bd31be416fd8b0d36', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:34:22 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.2450'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:34:22 GMT', u'_id': u'5980754ee0a14a0001e20eef', u'_etag': u'e4536cd95c97c42807a46f221c01e0b2a57e711e', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:35:00 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.4258'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:35:00 GMT', u'_id': u'59807574e0a14a0001e20ef0', u'_etag': u'1acd4d917252fd4c46459227ed6e24f072a41979', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:35:00 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.8490'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:35:00 GMT', u'_id': u'59807574e0a14a0001e20ef1', u'_etag': u'b3619bf3bcc98c38a50878d3662698a2564237a4', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:35:00 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.1576'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:35:00 GMT', u'_id': u'59807574e0a14a0001e20ef2', u'_etag': u'3b7962e43352a408148376402c39771c1941b8ba', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab984', u'_links': {u'self': {u'href': u'labs/5979c6b5e0a14a0001e20e9c', u'title': u'Lab'}, u'parent': {u'href': u'/', u'title': u'home'}, u'collection': {u'href': u'labs?pretty=', u'title': u'labs'}}, u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20e9c', u'_etag': u'ef055e8452b25aae9df4b4af2aae2701fc60aa06'})
            status_code = 200
        self.mock_admin_patch_item_OK_json_several_parameters_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_admin_patch_item_NOK_wrong_username(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        content = ""
        status_code = 200
        self.mock_admin_patch_item_NOK_wrong_username_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_admin_patch_item_NOK_item_does_not_exist(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_admin_patch_item_NOK_item_does_not_exist_json_id == 0:
            content = json.dumps({u'_status': u'ERR', u'_error': {u'message': u'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.', u'code': 404}})
            status_code = 404
        self.mock_admin_patch_item_NOK_item_does_not_exist_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_admin_patch_item_NOK_csv_parameter_error(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_admin_patch_item_NOK_csv_parameter_error_json_id == 0:
            content = json.dumps({u'status': u'initializing', u'_updated': u'Fri, 04 Aug 2017 08:04:45 GMT', u'states': [u'5979c6b5e0a14a0001e20e9d', u'5980754ee0a14a0001e20eed', u'5980754ee0a14a0001e20eee', u'5980754ee0a14a0001e20eef', u'59807574e0a14a0001e20ef0', u'59807574e0a14a0001e20ef1', u'59807574e0a14a0001e20ef2'], u'lab_name': u'mylabi', u'_links': {u'self': {u'href': u'labs/5979c6b5e0a14a0001e20e9c', u'title': u'Lab'}, u'parent': {u'href': u'/', u'title': u'home'}, u'collection': {u'href': u'labs', u'title': u'labs'}}, u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20e9c', u'_etag': u'd77828daa69e3b8a398c19b1d8845892bb0dea77'})
            status_code = 200
        elif self.mock_admin_patch_item_NOK_csv_parameter_error_json_id == 1:
            content = json.dumps({u'_status': u'ERR', u'_issues': {u'invalid_parameter': u'unknown field'}})
            status_code = 200
        self.mock_admin_patch_item_NOK_csv_parameter_error_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_admin_patch_item_NOK_json_parameter_error(self, url, request):
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if self.mock_admin_patch_item_NOK_json_parameter_error_json_id == 0:
            content = json.dumps({u'status': u'initializing', u'_updated': u'Thu, 03 Aug 2017 12:35:46 GMT', u'states': [u'5979c6b5e0a14a0001e20e9d', u'5980754ee0a14a0001e20eed', u'5980754ee0a14a0001e20eee', u'5980754ee0a14a0001e20eef', u'59807574e0a14a0001e20ef0', u'59807574e0a14a0001e20ef1', u'59807574e0a14a0001e20ef2'], u'lab_name': u'CloudLab984', u'_links': {u'self': {u'href': u'labs/5979c6b5e0a14a0001e20e9c', u'title': u'Lab'}, u'parent': {u'href': u'/', u'title': u'home'}, u'collection': {u'href': u'labs', u'title': u'labs'}}, u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20e9c', u'_etag': u'ffde6cd098eed63498eec8b614d502f0db785d81'})
            status_code = 200
        elif self.mock_admin_patch_item_NOK_json_parameter_error_json_id == 1:
            content = json.dumps({u'_updated': u'Wed, 02 Aug 2017 11:19:11 GMT', u'_links': {u'self': {u'href': u'states/5981b52fe0a14a0001e20f31', u'title': u'State'}}, u'_created': u'Wed, 02 Aug 2017 11:19:11 GMT', u'_status': u'OK', u'_id': u'5981b52fe0a14a0001e20f31', u'_etag': u'6733ea4099abcd7f9570d18ee4c6f01960376607'})
            status_code = 200
        elif self.mock_admin_patch_item_NOK_json_parameter_error_json_id == 2:
            content = json.dumps({u'status': u'initializing', u'_updated': u'Thu, 03 Aug 2017 12:53:50 GMT', u'states': [{u'_updated': u'Thu, 27 Jul 2017 10:55:49 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.166'}, u'snapshot_id': u'56', u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20e9d', u'_etag': u'f596e1ec27bcba752867ff3d12435ec8c61a7402', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:34:22 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.1585'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:34:22 GMT', u'_id': u'5980754ee0a14a0001e20eed', u'_etag': u'5139608d2c3157d4da0130aa10360eb3cc10dc0f', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:34:22 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.6694'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:34:22 GMT', u'_id': u'5980754ee0a14a0001e20eee', u'_etag': u'7c65ead19b22ff4d1eea616bd31be416fd8b0d36', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:34:22 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.2450'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:34:22 GMT', u'_id': u'5980754ee0a14a0001e20eef', u'_etag': u'e4536cd95c97c42807a46f221c01e0b2a57e711e', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:35:00 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.4258'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:35:00 GMT', u'_id': u'59807574e0a14a0001e20ef0', u'_etag': u'1acd4d917252fd4c46459227ed6e24f072a41979', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:35:00 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.8490'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:35:00 GMT', u'_id': u'59807574e0a14a0001e20ef1', u'_etag': u'b3619bf3bcc98c38a50878d3662698a2564237a4', u'snapshot_status': u'available'}, {u'_updated': u'Tue, 01 Aug 2017 12:35:00 GMT', u'lab': u'5979c6b5e0a14a0001e20e9c', u'build': {u'id': u'netact/product/99.17.03.0.1576'}, u'snapshot_id': u'3456', u'_created': u'Tue, 01 Aug 2017 12:35:00 GMT', u'_id': u'59807574e0a14a0001e20ef2', u'_etag': u'3b7962e43352a408148376402c39771c1941b8ba', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab984', u'_links': {u'self': {u'href': u'labs/5979c6b5e0a14a0001e20e9c', u'title': u'Lab'}, u'parent': {u'href': u'/', u'title': u'home'}, u'collection': {u'href': u'labs?pretty=', u'title': u'labs'}}, u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20e9c', u'_etag': u'ef055e8452b25aae9df4b4af2aae2701fc60aa06'})
            status_code = 200
        self.mock_admin_patch_item_NOK_json_parameter_error_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_admin_data_backup_OK(self, url, request):
        json_id = self.mock_admin_data_backup_OK_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'status': u'initializing', u'_updated': u'Thu, 03 Aug 2017 12:35:46 GMT', u'states': [u'5979c6b5e0a14a0001e20e9d', u'5980754ee0a14a0001e20eed', u'5980754ee0a14a0001e20eee', u'5980754ee0a14a0001e20eef', u'59807574e0a14a0001e20ef0', u'59807574e0a14a0001e20ef1', u'59807574e0a14a0001e20ef2'], u'lab_name': u'CloudLab984', u'_links': {u'self': {u'href': u'labs/5979c6b5e0a14a0001e20e9c', u'title': u'Lab'}, u'parent': {u'href': u'/', u'title': u'home'}, u'collection': {u'href': u'labs', u'title': u'labs'}}, u'_created': u'Thu, 27 Jul 2017 10:55:49 GMT', u'_id': u'5979c6b5e0a14a0001e20e9c', u'_etag': u'ffde6cd098eed63498eec8b614d502f0db785d81'})
            status_code = 200
        self.mock_admin_data_backup_OK_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|reservations).*')
    def mock_api_admin_reserve_labs_OK_one_lab(self, url, request):
        json_id = self.mock_admin_reserve_labs_OK_one_lab_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c46', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'snapshot_id': u'956', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c47', u'_etag': u'5d3caaa6279ea58be11b7032be22c1ae743e2314', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab6128', u'_links': {u'self': {u'href': u'labs/599ad1c3e0a14a0001e21c46', u'title': u'Lab'}}, u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c46', u'_etag': u'322bf6a9fa610f583b4558b9b667841e86192935'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab6128"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 1:
            content = json.dumps({u'_updated': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_links': {u'self': {u'href': u'reservations/599adc45e0a14a0001e21c5c', u'title': u'Reservation'}}, u'_created': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_status': u'OK', u'_id': u'599adc45e0a14a0001e21c5c', u'_etag': u'9dccf9c6811967be34282ea2be69abdb79b2917a'})
            status_code = 200
        self.mock_admin_reserve_labs_OK_one_lab_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|reservations).*')
    def mock_api_admin_reserve_labs_OK_several_labs(self, url, request):
        json_id = self.mock_admin_reserve_labs_OK_several_labs_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c46', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'snapshot_id': u'956', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c47', u'_etag': u'5d3caaa6279ea58be11b7032be22c1ae743e2314', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab6128', u'_links': {u'self': {u'href': u'labs/599ad1c3e0a14a0001e21c46', u'title': u'Lab'}}, u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c46', u'_etag': u'322bf6a9fa610f583b4558b9b667841e86192935'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab6128"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 1:
            content = json.dumps({u'_updated': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_links': {u'self': {u'href': u'reservations/599adc45e0a14a0001e21c5c', u'title': u'Reservation'}}, u'_created': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_status': u'OK', u'_id': u'599adc45e0a14a0001e21c5c', u'_etag': u'9dccf9c6811967be34282ea2be69abdb79b2917a'})
            status_code = 200
        if json_id == 2:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c46', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'snapshot_id': u'956', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c47', u'_etag': u'5d3caaa6279ea58be11b7032be22c1ae743e2314', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab6128', u'_links': {u'self': {u'href': u'labs/599ad1c3e0a14a0001e21c46', u'title': u'Lab'}}, u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c46', u'_etag': u'322bf6a9fa610f583b4558b9b667841e86192935'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab6128"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 3:
            content = json.dumps({u'_updated': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_links': {u'self': {u'href': u'reservations/599adc45e0a14a0001e21c5c', u'title': u'Reservation'}}, u'_created': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_status': u'OK', u'_id': u'599adc45e0a14a0001e21c5c', u'_etag': u'9dccf9c6811967be34282ea2be69abdb79b2917a'})
            status_code = 200
        if json_id == 4:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c46', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'snapshot_id': u'956', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c47', u'_etag': u'5d3caaa6279ea58be11b7032be22c1ae743e2314', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab6128', u'_links': {u'self': {u'href': u'labs/599ad1c3e0a14a0001e21c46', u'title': u'Lab'}}, u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c46', u'_etag': u'322bf6a9fa610f583b4558b9b667841e86192935'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab6128"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 5:
            content = json.dumps({u'_updated': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_links': {u'self': {u'href': u'reservations/599adc45e0a14a0001e21c5c', u'title': u'Reservation'}}, u'_created': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_status': u'OK', u'_id': u'599adc45e0a14a0001e21c5c', u'_etag': u'9dccf9c6811967be34282ea2be69abdb79b2917a'})
            status_code = 200
        self.mock_admin_reserve_labs_OK_several_labs_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|reservations).*')
    def mock_api_admin_reserve_labs_OK_one_lab_with_force(self, url, request):
        json_id = self.mock_admin_reserve_labs_OK_one_lab_with_force_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c46', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'snapshot_id': u'956', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c47', u'_etag': u'5d3caaa6279ea58be11b7032be22c1ae743e2314', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab6128', u'_links': {u'self': {u'href': u'labs/599ad1c3e0a14a0001e21c46', u'title': u'Lab'}}, u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c46', u'_etag': u'322bf6a9fa610f583b4558b9b667841e86192935'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab6128"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 1:
            content = json.dumps({u'_updated': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_links': {u'self': {u'href': u'reservations/599adc45e0a14a0001e21c5c', u'title': u'Reservation'}}, u'_created': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_status': u'OK', u'_id': u'599adc45e0a14a0001e21c5c', u'_etag': u'9dccf9c6811967be34282ea2be69abdb79b2917a'})
            status_code = 200
        self.mock_admin_reserve_labs_OK_one_lab_with_force_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|reservations).*')
    def mock_api_admin_reserve_labs_OK_several_labs_with_force(self, url, request):
        json_id = self.mock_admin_reserve_labs_OK_several_labs_with_force_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c46', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'snapshot_id': u'956', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c47', u'_etag': u'5d3caaa6279ea58be11b7032be22c1ae743e2314', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab6128', u'_links': {u'self': {u'href': u'labs/599ad1c3e0a14a0001e21c46', u'title': u'Lab'}}, u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c46', u'_etag': u'322bf6a9fa610f583b4558b9b667841e86192935'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab6128"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 1:
            content = json.dumps({u'_updated': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_links': {u'self': {u'href': u'reservations/599adc45e0a14a0001e21c5c', u'title': u'Reservation'}}, u'_created': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_status': u'OK', u'_id': u'599adc45e0a14a0001e21c5c', u'_etag': u'9dccf9c6811967be34282ea2be69abdb79b2917a'})
            status_code = 200
        if json_id == 2:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c46', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'snapshot_id': u'956', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c47', u'_etag': u'5d3caaa6279ea58be11b7032be22c1ae743e2314', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab6128', u'_links': {u'self': {u'href': u'labs/599ad1c3e0a14a0001e21c46', u'title': u'Lab'}}, u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c46', u'_etag': u'322bf6a9fa610f583b4558b9b667841e86192935'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab6128"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 3:
            content = json.dumps({u'_updated': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_links': {u'self': {u'href': u'reservations/599adc45e0a14a0001e21c5c', u'title': u'Reservation'}}, u'_created': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_status': u'OK', u'_id': u'599adc45e0a14a0001e21c5c', u'_etag': u'9dccf9c6811967be34282ea2be69abdb79b2917a'})
            status_code = 200
        if json_id == 4:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c46', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'snapshot_id': u'956', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c47', u'_etag': u'5d3caaa6279ea58be11b7032be22c1ae743e2314', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab6128', u'_links': {u'self': {u'href': u'labs/599ad1c3e0a14a0001e21c46', u'title': u'Lab'}}, u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c46', u'_etag': u'322bf6a9fa610f583b4558b9b667841e86192935'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab6128"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 5:
            content = json.dumps({u'_updated': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_links': {u'self': {u'href': u'reservations/599adc45e0a14a0001e21c5c', u'title': u'Reservation'}}, u'_created': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_status': u'OK', u'_id': u'599adc45e0a14a0001e21c5c', u'_etag': u'9dccf9c6811967be34282ea2be69abdb79b2917a'})
            status_code = 200
        self.mock_admin_reserve_labs_OK_several_labs_with_force_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|reservations).*')
    def mock_api_admin_reserve_labs_OK_one_lab_reserved_by_admin_with_force(self, url, request):
        json_id = self.mock_admin_reserve_labs_OK_one_lab_reserved_by_admin_with_force_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'reverting_state', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'states': [{u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c44', u'build': {u'id': u'netact/product/99.17.03.0.166'}, u'snapshot_id': u'56', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c45', u'_etag': u'18eae4a9515c08c723fd58fb35bec35f32dc59ee', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab5920', u'_links': {u'self': {u'href': u'labs/599ad1c3e0a14a0001e21c44', u'title': u'Lab'}}, u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'reservation': {u'username': u'admin', u'_updated': u'Mon, 21 Aug 2017 12:53:43 GMT', u'lab': u'599ad1c3e0a14a0001e21c44', u'_created': u'Mon, 21 Aug 2017 12:53:43 GMT', u'message': u'Lab reserved for maintanance work.', u'_id': u'599ad7d7e0a14a0001e21c5b', u'_etag': u'0fe9dd2dc3e3729af2abf015e2414509aa042112'}, u'_id': u'599ad1c3e0a14a0001e21c44', u'_etag': u'd3fb415f2eb060335e6309574fc19c2228d8a78d'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab5920"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 1:
            content = None
            status_code = 204
        if json_id == 2:
            content = json.dumps({u'_updated': u'Tue, 22 Aug 2017 07:38:01 GMT', u'_links': {u'self': {u'href': u'reservations/599bdf593973960001d91ab0', u'title': u'Reservation'}}, u'_created': u'Tue, 22 Aug 2017 07:38:01 GMT', u'_status': u'OK', u'_id': u'599bdf593973960001d91ab0', u'_etag': u'81e4bee0dd961edcbfe3448266259ebf2b3957fc'})
            status_code = 200
        self.mock_admin_reserve_labs_OK_one_lab_reserved_by_admin_with_force_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|reservations).*')
    def mock_api_admin_reserve_labs_OK_one_lab_reserved_by_other_user_with_force(self, url, request):
        json_id = self.mock_admin_reserve_labs_OK_one_lab_reserved_by_other_user_with_force_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'reverting_state', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'states': [{u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c44', u'build': {u'id': u'netact/product/99.17.03.0.166'}, u'snapshot_id': u'56', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c45', u'_etag': u'18eae4a9515c08c723fd58fb35bec35f32dc59ee', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab5920', u'_links': {u'self': {u'href': u'labs/599ad1c3e0a14a0001e21c44', u'title': u'Lab'}}, u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'reservation': {u'username': u'Pertti Keinonen', u'_updated': u'Mon, 21 Aug 2017 12:53:43 GMT', u'lab': u'599ad1c3e0a14a0001e21c44', u'_created': u'Mon, 21 Aug 2017 12:53:43 GMT', u'message': u'Lab reserved for maintanance work.', u'_id': u'599ad7d7e0a14a0001e21c5b', u'_etag': u'0fe9dd2dc3e3729af2abf015e2414509aa042112'}, u'_id': u'599ad1c3e0a14a0001e21c44', u'_etag': u'd3fb415f2eb060335e6309574fc19c2228d8a78d'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab5920"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 1:
            content = None
            status_code = 204
        if json_id == 2:
            content = json.dumps({u'_updated': u'Tue, 22 Aug 2017 07:38:01 GMT', u'_links': {u'self': {u'href': u'reservations/599bdf593973960001d91ab0', u'title': u'Reservation'}}, u'_created': u'Tue, 22 Aug 2017 07:38:01 GMT', u'_status': u'OK', u'_id': u'599bdf593973960001d91ab0', u'_etag': u'81e4bee0dd961edcbfe3448266259ebf2b3957fc'})
            status_code = 200
        self.mock_admin_reserve_labs_OK_one_lab_reserved_by_other_user_with_force_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|reservations).*')
    def mock_api_admin_reserve_labs_OK_all_labs_reserved_by_other_user_with_force(self, url, request):
        json_id = self.mock_admin_reserve_labs_OK_all_labs_reserved_by_other_user_with_force_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'reverting_state', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'states': [{u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c44', u'build': {u'id': u'netact/product/99.17.03.0.166'}, u'snapshot_id': u'56', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c45', u'_etag': u'18eae4a9515c08c723fd58fb35bec35f32dc59ee', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab5920', u'_links': {u'self': {u'href': u'labs/599ad1c3e0a14a0001e21c44', u'title': u'Lab'}}, u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'reservation': {u'username': u'Pertti Keinonen', u'_updated': u'Mon, 21 Aug 2017 12:53:43 GMT', u'lab': u'599ad1c3e0a14a0001e21c44', u'_created': u'Mon, 21 Aug 2017 12:53:43 GMT', u'message': u'Lab reserved for maintanance work.', u'_id': u'599ad7d7e0a14a0001e21c5b', u'_etag': u'0fe9dd2dc3e3729af2abf015e2414509aa042112'}, u'_id': u'599ad1c3e0a14a0001e21c44', u'_etag': u'd3fb415f2eb060335e6309574fc19c2228d8a78d'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab5920"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 1:
            content = None
            status_code = 204
        if json_id == 2:
            content = json.dumps({u'_updated': u'Tue, 22 Aug 2017 07:38:01 GMT', u'_links': {u'self': {u'href': u'reservations/599bdf593973960001d91ab0', u'title': u'Reservation'}}, u'_created': u'Tue, 22 Aug 2017 07:38:01 GMT', u'_status': u'OK', u'_id': u'599bdf593973960001d91ab0', u'_etag': u'81e4bee0dd961edcbfe3448266259ebf2b3957fc'})
            status_code = 200
        if json_id == 3:
            content = json.dumps({u'_items': [{u'status': u'reverting_state', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'states': [{u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c44', u'build': {u'id': u'netact/product/99.17.03.0.166'}, u'snapshot_id': u'56', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c45', u'_etag': u'18eae4a9515c08c723fd58fb35bec35f32dc59ee', u'snapshot_status': u'available'}], u'lab_name': u'vsp0044', u'_links': {u'self': {u'href': u'labs/599ad1c3e0a14a0001e21c44', u'title': u'Lab'}}, u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'reservation': {u'username': u'Pertti Keinonen', u'_updated': u'Mon, 21 Aug 2017 12:53:43 GMT', u'lab': u'599ad1c3e0a14a0001e21c44', u'_created': u'Mon, 21 Aug 2017 12:53:43 GMT', u'message': u'Lab reserved for maintanance work.', u'_id': u'599ad7d7e0a14a0001e21c5b', u'_etag': u'0fe9dd2dc3e3729af2abf015e2414509aa042112'}, u'_id': u'599ad1c3e0a14a0001e21c44', u'_etag': u'd3fb415f2eb060335e6309574fc19c2228d8a78d'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab5920"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 4:
            content = None
            status_code = 204
        if json_id == 5:
            content = json.dumps({u'_updated': u'Tue, 22 Aug 2017 07:38:01 GMT', u'_links': {u'self': {u'href': u'reservations/599bdf593973960001d91ab0', u'title': u'Reservation'}}, u'_created': u'Tue, 22 Aug 2017 07:38:01 GMT', u'_status': u'OK', u'_id': u'599bdf593973960001d91ab0', u'_etag': u'81e4bee0dd961edcbfe3448266259ebf2b3957fc'})
            status_code = 200
        if json_id == 6:
            content = json.dumps({u'_items': [{u'status': u'reverting_state', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'states': [{u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c44', u'build': {u'id': u'netact/product/99.17.03.0.166'}, u'snapshot_id': u'56', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c45', u'_etag': u'18eae4a9515c08c723fd58fb35bec35f32dc59ee', u'snapshot_status': u'available'}], u'lab_name': u'sprintlab0098', u'_links': {u'self': {u'href': u'labs/599ad1c3e0a14a0001e21c44', u'title': u'Lab'}}, u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'reservation': {u'username': u'Pertti Keinonen', u'_updated': u'Mon, 21 Aug 2017 12:53:43 GMT', u'lab': u'599ad1c3e0a14a0001e21c44', u'_created': u'Mon, 21 Aug 2017 12:53:43 GMT', u'message': u'Lab reserved for maintanance work.', u'_id': u'599ad7d7e0a14a0001e21c5b', u'_etag': u'0fe9dd2dc3e3729af2abf015e2414509aa042112'}, u'_id': u'599ad1c3e0a14a0001e21c44', u'_etag': u'd3fb415f2eb060335e6309574fc19c2228d8a78d'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab5920"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 7:
            content = None
            status_code = 204
        if json_id == 8:
            content = json.dumps({u'_updated': u'Tue, 22 Aug 2017 07:38:01 GMT', u'_links': {u'self': {u'href': u'reservations/599bdf593973960001d91ab0', u'title': u'Reservation'}}, u'_created': u'Tue, 22 Aug 2017 07:38:01 GMT', u'_status': u'OK', u'_id': u'599bdf593973960001d91ab0', u'_etag': u'81e4bee0dd961edcbfe3448266259ebf2b3957fc'})
            status_code = 200
        self.mock_admin_reserve_labs_OK_all_labs_reserved_by_other_user_with_force_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|reservations).*')
    def mock_api_admin_reserve_labs_NOK_one_lab(self, url, request):
        json_id = self.mock_admin_reserve_labs_NOK_one_lab_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'reverting_state', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab_type': u'vsprint', u'states': [{u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c4d', u'build': {u'id': u'netact/product/99.17.03.0.004'}, u'snapshot_id': u'7456', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c4e', u'_etag': u'478554cb3d72a02b40290cb927680af668d35feb', u'snapshot_status': u'available'}, {u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c4d', u'build': {u'id': u'netact/product/99.17.03.0.424'}, u'snapshot_id': u'7456', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c4f', u'_etag': u'461bfd2b3c28faaf96ae33ca5e823d3f1b40085c', u'snapshot_status': u'available'}, {u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c4d', u'build': {u'id': u'netact/product/99.17.03.0.645'}, u'snapshot_id': u'7456', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c50', u'_etag': u'2bc5a49e008606ca2199eece2bf4f7aebb91f9bb', u'snapshot_status': u'available'}], u'lab_name': u'vSprint1803', u'_links': {u'self': {u'href': u'labs/599ad1c3e0a14a0001e21c4d', u'title': u'Lab'}}, u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'reservation': {u'username': u'testuser', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c4d', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c51', u'_etag': u'ef80b4c46420b4dcac5d56ef458ceb2faed1daf9'}, u'_id': u'599ad1c3e0a14a0001e21c4d', u'_etag': u'766fb79ef18895e2df4530304bf0d5e233034e08'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"vSprint1803"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        self.mock_admin_reserve_labs_NOK_one_lab_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|reservations).*')
    def mock_api_admin_reserve_labs_NOK_several_labs_one_NOK(self, url, request):
        json_id = self.mock_admin_reserve_labs_NOK_several_labs_one_NOK_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c46', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'snapshot_id': u'956', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c47', u'_etag': u'5d3caaa6279ea58be11b7032be22c1ae743e2314', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab6128', u'_links': {u'self': {u'href': u'labs/599ad1c3e0a14a0001e21c46', u'title': u'Lab'}}, u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c46', u'_etag': u'322bf6a9fa610f583b4558b9b667841e86192935'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab6128"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 1:
            content = json.dumps({u'_updated': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_links': {u'self': {u'href': u'reservations/599adc45e0a14a0001e21c5c', u'title': u'Reservation'}}, u'_created': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_status': u'OK', u'_id': u'599adc45e0a14a0001e21c5c', u'_etag': u'9dccf9c6811967be34282ea2be69abdb79b2917a'})
            status_code = 200
        if json_id == 2:
            content = json.dumps({u'_items': [{u'status': u'reverting_state', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab_type': u'vsprint', u'states': [{u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c4d', u'build': {u'id': u'netact/product/99.17.03.0.004'}, u'snapshot_id': u'7456', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c4e', u'_etag': u'478554cb3d72a02b40290cb927680af668d35feb', u'snapshot_status': u'available'}, {u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c4d', u'build': {u'id': u'netact/product/99.17.03.0.424'}, u'snapshot_id': u'7456', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c4f', u'_etag': u'461bfd2b3c28faaf96ae33ca5e823d3f1b40085c', u'snapshot_status': u'available'}, {u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c4d', u'build': {u'id': u'netact/product/99.17.03.0.645'}, u'snapshot_id': u'7456', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c50', u'_etag': u'2bc5a49e008606ca2199eece2bf4f7aebb91f9bb', u'snapshot_status': u'available'}], u'lab_name': u'vSprint1803', u'_links': {u'self': {u'href': u'labs/599ad1c3e0a14a0001e21c4d', u'title': u'Lab'}}, u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'reservation': {u'username': u'testuser', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c4d', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c51', u'_etag': u'ef80b4c46420b4dcac5d56ef458ceb2faed1daf9'}, u'_id': u'599ad1c3e0a14a0001e21c4d', u'_etag': u'766fb79ef18895e2df4530304bf0d5e233034e08'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"vSprint1803"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 3:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c46', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'snapshot_id': u'956', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c47', u'_etag': u'5d3caaa6279ea58be11b7032be22c1ae743e2314', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab6128', u'_links': {u'self': {u'href': u'labs/599ad1c3e0a14a0001e21c46', u'title': u'Lab'}}, u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c46', u'_etag': u'322bf6a9fa610f583b4558b9b667841e86192935'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab6128"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 4:
            content = json.dumps({u'_updated': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_links': {u'self': {u'href': u'reservations/599adc45e0a14a0001e21c5c', u'title': u'Reservation'}}, u'_created': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_status': u'OK', u'_id': u'599adc45e0a14a0001e21c5c', u'_etag': u'9dccf9c6811967be34282ea2be69abdb79b2917a'})
            status_code = 200
        self.mock_admin_reserve_labs_NOK_several_labs_one_NOK_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|reservations).*')
    def mock_api_admin_reserve_labs_NOK_several_labs_all_NOK(self, url, request):
        json_id = self.mock_admin_reserve_labs_NOK_several_labs_all_NOK_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'reverting_state', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab_type': u'vsprint', u'states': [{u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c4d', u'build': {u'id': u'netact/product/99.17.03.0.004'}, u'snapshot_id': u'7456', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c4e', u'_etag': u'478554cb3d72a02b40290cb927680af668d35feb', u'snapshot_status': u'available'}, {u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c4d', u'build': {u'id': u'netact/product/99.17.03.0.424'}, u'snapshot_id': u'7456', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c4f', u'_etag': u'461bfd2b3c28faaf96ae33ca5e823d3f1b40085c', u'snapshot_status': u'available'}, {u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c4d', u'build': {u'id': u'netact/product/99.17.03.0.645'}, u'snapshot_id': u'7456', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c50', u'_etag': u'2bc5a49e008606ca2199eece2bf4f7aebb91f9bb', u'snapshot_status': u'available'}], u'lab_name': u'vSprint1803', u'_links': {u'self': {u'href': u'labs/599ad1c3e0a14a0001e21c4d', u'title': u'Lab'}}, u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'reservation': {u'username': u'testuser', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c4d', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c51', u'_etag': u'ef80b4c46420b4dcac5d56ef458ceb2faed1daf9'}, u'_id': u'599ad1c3e0a14a0001e21c4d', u'_etag': u'766fb79ef18895e2df4530304bf0d5e233034e08'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"vSprint1803"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 1:
            content = json.dumps({u'_items': [], u'_links': {u'self': {u'href': u'labs', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 0, u'page': 1}})

            status_code = 200
        if json_id == 2:
            content = json.dumps({u'_items': [], u'_links': {u'self': {u'href': u'labs', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 0, u'page': 1}})

            status_code = 200
        self.mock_admin_reserve_labs_NOK_several_labs_all_NOK_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|reservations).*')
    def mock_api_admin_reserve_labs_NOK_several_labs_one_NOK_with_force(self, url, request):
        json_id = self.mock_admin_reserve_labs_NOK_several_labs_one_NOK_with_force_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c46', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'snapshot_id': u'956', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c47', u'_etag': u'5d3caaa6279ea58be11b7032be22c1ae743e2314', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab6128', u'_links': {u'self': {u'href': u'labs/599ad1c3e0a14a0001e21c46', u'title': u'Lab'}}, u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c46', u'_etag': u'322bf6a9fa610f583b4558b9b667841e86192935'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab6128"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 1:
            content = json.dumps({u'_updated': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_links': {u'self': {u'href': u'reservations/599adc45e0a14a0001e21c5c', u'title': u'Reservation'}}, u'_created': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_status': u'OK', u'_id': u'599adc45e0a14a0001e21c5c', u'_etag': u'9dccf9c6811967be34282ea2be69abdb79b2917a'})
            status_code = 200
        if json_id == 2:
            content = json.dumps({u'_items': [{u'status': u'reverting_state', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'states': [{u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c44', u'build': {u'id': u'netact/product/99.17.03.0.166'}, u'snapshot_id': u'56', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c45', u'_etag': u'18eae4a9515c08c723fd58fb35bec35f32dc59ee', u'snapshot_status': u'available'}], u'lab_name': u'vsp0044', u'_links': {u'self': {u'href': u'labs/599ad1c3e0a14a0001e21c44', u'title': u'Lab'}}, u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'reservation': {u'username': u'Pertti Keinonen', u'_updated': u'Mon, 21 Aug 2017 12:53:43 GMT', u'lab': u'599ad1c3e0a14a0001e21c44', u'_created': u'Mon, 21 Aug 2017 12:53:43 GMT', u'message': u'Lab reserved for maintanance work.', u'_id': u'599ad7d7e0a14a0001e21c5b', u'_etag': u'0fe9dd2dc3e3729af2abf015e2414509aa042112'}, u'_id': u'599ad1c3e0a14a0001e21c44', u'_etag': u'd3fb415f2eb060335e6309574fc19c2228d8a78d'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab5920"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 3:
            content = None
            status_code = 422
        if json_id == 4:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c46', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'snapshot_id': u'956', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c47', u'_etag': u'5d3caaa6279ea58be11b7032be22c1ae743e2314', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab6128', u'_links': {u'self': {u'href': u'labs/599ad1c3e0a14a0001e21c46', u'title': u'Lab'}}, u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c46', u'_etag': u'322bf6a9fa610f583b4558b9b667841e86192935'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab6128"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 5:
            content = json.dumps({u'_updated': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_links': {u'self': {u'href': u'reservations/599adc45e0a14a0001e21c5c', u'title': u'Reservation'}}, u'_created': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_status': u'OK', u'_id': u'599adc45e0a14a0001e21c5c', u'_etag': u'9dccf9c6811967be34282ea2be69abdb79b2917a'})
            status_code = 200
        self.mock_admin_reserve_labs_NOK_several_labs_one_NOK_with_force_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|reservations).*')
    def mock_api_admin_reserve_labs_NOK_several_labs_all_NOK_with_force(self, url, request):
        json_id = self.mock_admin_reserve_labs_NOK_several_labs_all_NOK_with_force_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c46', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'snapshot_id': u'956', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c47', u'_etag': u'5d3caaa6279ea58be11b7032be22c1ae743e2314', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab6128', u'_links': {u'self': {u'href': u'labs/599ad1c3e0a14a0001e21c46', u'title': u'Lab'}}, u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c46', u'_etag': u'322bf6a9fa610f583b4558b9b667841e86192935'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab6128"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 1:
            content = {}
            status_code = 500
        if json_id == 2:
            content = json.dumps({u'_items': [{u'status': u'reverting_state', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'states': [{u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c44', u'build': {u'id': u'netact/product/99.17.03.0.166'}, u'snapshot_id': u'56', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c45', u'_etag': u'18eae4a9515c08c723fd58fb35bec35f32dc59ee', u'snapshot_status': u'available'}], u'lab_name': u'vsp0044', u'_links': {u'self': {u'href': u'labs/599ad1c3e0a14a0001e21c44', u'title': u'Lab'}}, u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'reservation': {u'username': u'Pertti Keinonen', u'_updated': u'Mon, 21 Aug 2017 12:53:43 GMT', u'lab': u'599ad1c3e0a14a0001e21c44', u'_created': u'Mon, 21 Aug 2017 12:53:43 GMT', u'message': u'Lab reserved for maintanance work.', u'_id': u'599ad7d7e0a14a0001e21c5b', u'_etag': u'0fe9dd2dc3e3729af2abf015e2414509aa042112'}, u'_id': u'599ad1c3e0a14a0001e21c44', u'_etag': u'd3fb415f2eb060335e6309574fc19c2228d8a78d'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab5920"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 3:
            content = None
            status_code = 422
        if json_id == 4:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c46', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'snapshot_id': u'956', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c47', u'_etag': u'5d3caaa6279ea58be11b7032be22c1ae743e2314', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab6128', u'_links': {u'self': {u'href': u'labs/599ad1c3e0a14a0001e21c46', u'title': u'Lab'}}, u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c46', u'_etag': u'322bf6a9fa610f583b4558b9b667841e86192935'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab6128"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 5:
            content = json.dumps({u'_updated': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_links': {u'self': {u'href': u'reservations/599adc45e0a14a0001e21c5c', u'title': u'Reservation'}}, u'_created': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_status': u'OK', u'_id': u'599adc45e0a14a0001e21c5c', u'_etag': u'9dccf9c6811967be34282ea2be69abdb79b2917a'})
            status_code = 200
        self.mock_admin_reserve_labs_NOK_several_labs_all_NOK_with_force_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|reservations).*')
    def mock_api_admin_reserve_labs_NOK_lab_does_not_exist(self, url, request):
        json_id = self.mock_admin_reserve_labs_NOK_lab_does_not_exist_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [], u'_links': {u'self': {u'href': u'labs', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 0, u'page': 1}})

            status_code = 200
        self.mock_admin_reserve_labs_NOK_lab_does_not_exist_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|reservations).*')
    def mock_api_admin_reserve_labs_NOK_user_not_allowed_to_reserve(self, url, request):
        json_id = self.mock_admin_reserve_labs_NOK_user_not_allowed_to_reserve_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c46', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'snapshot_id': u'956', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c47', u'_etag': u'5d3caaa6279ea58be11b7032be22c1ae743e2314', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab6128', u'_links': {u'self': {u'href': u'labs/599ad1c3e0a14a0001e21c46', u'title': u'Lab'}}, u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c46', u'_etag': u'322bf6a9fa610f583b4558b9b667841e86192935'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab6128"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 1:
            content = json.dumps({u'_updated': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_links': {u'self': {u'href': u'reservations/599adc45e0a14a0001e21c5c', u'title': u'Reservation'}}, u'_created': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_status': u'OK', u'_id': u'599adc45e0a14a0001e21c5c', u'_etag': u'9dccf9c6811967be34282ea2be69abdb79b2917a'})
            status_code = 200
        self.mock_admin_reserve_labs_NOK_user_not_allowed_to_reserve_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|reservations).*')
    def mock_api_admin_reserve_labs_NOK_lab_already_reserved(self, url, request):
        json_id = self.mock_admin_reserve_labs_NOK_lab_already_reserved_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'reverting_state', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'states': [{u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c44', u'build': {u'id': u'netact/product/99.17.03.0.166'}, u'snapshot_id': u'56', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c45', u'_etag': u'18eae4a9515c08c723fd58fb35bec35f32dc59ee', u'snapshot_status': u'available'}], u'lab_name': u'sprintlab0098', u'_links': {u'self': {u'href': u'labs/599ad1c3e0a14a0001e21c44', u'title': u'Lab'}}, u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'reservation': {u'username': u'Pertti Keinonen', u'_updated': u'Mon, 21 Aug 2017 12:53:43 GMT', u'lab': u'599ad1c3e0a14a0001e21c44', u'_created': u'Mon, 21 Aug 2017 12:53:43 GMT', u'message': u'Lab reserved for maintanance work.', u'_id': u'599ad7d7e0a14a0001e21c5b', u'_etag': u'0fe9dd2dc3e3729af2abf015e2414509aa042112'}, u'_id': u'599ad1c3e0a14a0001e21c44', u'_etag': u'd3fb415f2eb060335e6309574fc19c2228d8a78d'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab5920"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        self.mock_admin_reserve_labs_NOK_lab_already_reserved_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|reservations).*')
    def mock_api_admin_reserve_labs_NOK_exception(self, url, request):
        json_id = self.mock_admin_reserve_labs_NOK_exception_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': u''})
            status_code = 200
        self.mock_admin_reserve_labs_NOK_exception_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|reservations|states).*')
    def mock_api_admin_remove_snapshots_OK_one_snapshot(self, url, request):
        json_id = self.mock_admin_remove_snapshots_OK_one_snapshot_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        self._assert_force_in_url('states|labs|reservations', url, False)
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Tue, 22 Aug 2017 12:32:08 GMT', u'lab_type': u'vsprint', u'states': [{u'_updated': u'Tue, 22 Aug 2017 12:32:08 GMT', u'lab': u'599c24483973960001d91d6a', u'build': {u'id': u'netact/product/99.17.03.0.112'}, u'snapshot_id': u'113456', u'_created': u'Tue, 22 Aug 2017 12:32:08 GMT', u'_id': u'599c24483973960001d91d6b', u'_etag': u'38c3d7c19b817c2a052b731895ed2edf5d740cea', u'snapshot_status': u'available'}], u'lab_name': u'vSprint7489', u'_links': {u'self': {u'href': u'labs/599c24483973960001d91d6a', u'title': u'Lab'}}, u'_created': u'Tue, 22 Aug 2017 12:32:08 GMT', u'_id': u'599c24483973960001d91d6a', u'_etag': u'0aafa68db2f614aaa9e77018406da01b5b80e200'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"vSprint7489"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 1:
            content = json.dumps({u'_updated': u'Wed, 23 Aug 2017 08:39:32 GMT', u'_links': {u'self': {u'href': u'reservations/599d3f443973960001d91d6d', u'title': u'Reservation'}}, u'_created': u'Wed, 23 Aug 2017 08:39:32 GMT', u'_status': u'OK', u'_id': u'599d3f443973960001d91d6d', u'_etag': u'bafce54ac005360d45bab47a2193305ca3c01de3'})
            status_code = 200
        if json_id == 2:
            content = None
            status_code = 204
        self.mock_admin_remove_snapshots_OK_one_snapshot_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|reservations|states).*')
    def mock_api_admin_remove_snapshots_OK_several_snapshots(self, url, request):
        json_id = self.mock_admin_remove_snapshots_OK_several_snapshots_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        self._assert_force_in_url('states|labs|reservations', url, False)
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Tue, 22 Aug 2017 12:32:08 GMT', u'lab_type': u'vsprint', u'states': [{u'_updated': u'Tue, 22 Aug 2017 12:32:08 GMT', u'lab': u'599c24483973960001d91d6a', u'build': {u'id': u'netact/product/99.17.03.0.112'}, u'snapshot_id': u'113456', u'_created': u'Tue, 22 Aug 2017 12:32:08 GMT', u'_id': u'599c24483973960001d91d6b', u'_etag': u'38c3d7c19b817c2a052b731895ed2edf5d740cea', u'snapshot_status': u'available'},{u'_updated': u'Tue, 22 Aug 2017 12:32:08 GMT', u'lab': u'599c24483973960001d91d6a', u'build': {u'id': u'netact/product/99.17.03.0.112'}, u'snapshot_id': u'3456', u'_created': u'Tue, 22 Aug 2017 12:32:08 GMT', u'_id': u'599c24483973960001d91d6b', u'_etag': u'38c3d7c19b817c2a052b731895ed2edf5d740cea', u'snapshot_status': u'available'},{u'_updated': u'Tue, 22 Aug 2017 12:32:08 GMT', u'lab': u'599c24483973960001d91d6a', u'build': {u'id': u'netact/product/99.17.03.0.112'}, u'snapshot_id': u'66777', u'_created': u'Tue, 22 Aug 2017 12:32:08 GMT', u'_id': u'599c24483973960001d91d6b', u'_etag': u'38c3d7c19b817c2a052b731895ed2edf5d740cea', u'snapshot_status': u'available'}], u'lab_name': u'vSprint7489', u'_links': {u'self': {u'href': u'labs/599c24483973960001d91d6a', u'title': u'Lab'}}, u'_created': u'Tue, 22 Aug 2017 12:32:08 GMT', u'_id': u'599c24483973960001d91d6a', u'_etag': u'0aafa68db2f614aaa9e77018406da01b5b80e200'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"vSprint7489"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 1:
            content = json.dumps({u'_updated': u'Wed, 23 Aug 2017 08:39:32 GMT', u'_links': {u'self': {u'href': u'reservations/599d3f443973960001d91d6d', u'title': u'Reservation'}}, u'_created': u'Wed, 23 Aug 2017 08:39:32 GMT', u'_status': u'OK', u'_id': u'599d3f443973960001d91d6d', u'_etag': u'bafce54ac005360d45bab47a2193305ca3c01de3'})
            status_code = 200
        if json_id == 2:
            content = None
            status_code = 204
        if json_id == 3:
            content = None
            status_code = 204
        if json_id == 4:
            content = None
            status_code = 204
        self.mock_admin_remove_snapshots_OK_several_snapshots_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|reservations|states).*')
    def mock_api_admin_remove_snapshots_OK_one_snapshot_with_force(self, url, request):
        json_id = self.mock_admin_remove_snapshots_OK_one_snapshot_with_force_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        self._assert_force_in_url('states', url)
        self._assert_force_in_url('labs|reservations', url, False)
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Tue, 22 Aug 2017 12:32:08 GMT', u'lab_type': u'vsprint', u'states': [{u'_updated': u'Tue, 22 Aug 2017 12:32:08 GMT', u'lab': u'599c24483973960001d91d6a', u'build': {u'id': u'netact/product/99.17.03.0.112'}, u'snapshot_id': u'113456', u'_created': u'Tue, 22 Aug 2017 12:32:08 GMT', u'_id': u'599c24483973960001d91d6b', u'_etag': u'38c3d7c19b817c2a052b731895ed2edf5d740cea', u'snapshot_status': u'available'}], u'lab_name': u'vSprint7489', u'_links': {u'self': {u'href': u'labs/599c24483973960001d91d6a', u'title': u'Lab'}}, u'_created': u'Tue, 22 Aug 2017 12:32:08 GMT', u'_id': u'599c24483973960001d91d6a', u'_etag': u'0aafa68db2f614aaa9e77018406da01b5b80e200'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"vSprint7489"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 1:
            content = json.dumps({u'_updated': u'Wed, 23 Aug 2017 08:39:32 GMT', u'_links': {u'self': {u'href': u'reservations/599d3f443973960001d91d6d', u'title': u'Reservation'}}, u'_created': u'Wed, 23 Aug 2017 08:39:32 GMT', u'_status': u'OK', u'_id': u'599d3f443973960001d91d6d', u'_etag': u'bafce54ac005360d45bab47a2193305ca3c01de3'})
            status_code = 200
        if json_id == 2:
            content = None
            status_code = 204
        self.mock_admin_remove_snapshots_OK_one_snapshot_with_force_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|reservations|states).*')
    def mock_api_admin_remove_snapshots_OK_several_snapshots_with_force(self, url, request):
        json_id = self.mock_admin_remove_snapshots_OK_several_snapshots_with_force_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        self._assert_force_in_url('states', url)
        self._assert_force_in_url('labs|reservations', url, False)
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Tue, 22 Aug 2017 12:32:08 GMT', u'lab_type': u'vsprint', u'states': [{u'_updated': u'Tue, 22 Aug 2017 12:32:08 GMT', u'lab': u'599c24483973960001d91d6a', u'build': {u'id': u'netact/product/99.17.03.0.112'}, u'snapshot_id': u'113456', u'_created': u'Tue, 22 Aug 2017 12:32:08 GMT', u'_id': u'599c24483973960001d91d6b', u'_etag': u'38c3d7c19b817c2a052b731895ed2edf5d740cea', u'snapshot_status': u'available'},{u'_updated': u'Tue, 22 Aug 2017 12:32:08 GMT', u'lab': u'599c24483973960001d91d6a', u'build': {u'id': u'netact/product/99.17.03.0.112'}, u'snapshot_id': u'3456', u'_created': u'Tue, 22 Aug 2017 12:32:08 GMT', u'_id': u'599c24483973960001d91d6b', u'_etag': u'38c3d7c19b817c2a052b731895ed2edf5d740cea', u'snapshot_status': u'available'},{u'_updated': u'Tue, 22 Aug 2017 12:32:08 GMT', u'lab': u'599c24483973960001d91d6a', u'build': {u'id': u'netact/product/99.17.03.0.112'}, u'snapshot_id': u'66777', u'_created': u'Tue, 22 Aug 2017 12:32:08 GMT', u'_id': u'599c24483973960001d91d6b', u'_etag': u'38c3d7c19b817c2a052b731895ed2edf5d740cea', u'snapshot_status': u'available'}], u'lab_name': u'vSprint7489', u'_links': {u'self': {u'href': u'labs/599c24483973960001d91d6a', u'title': u'Lab'}}, u'_created': u'Tue, 22 Aug 2017 12:32:08 GMT', u'_id': u'599c24483973960001d91d6a', u'_etag': u'0aafa68db2f614aaa9e77018406da01b5b80e200'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"vSprint7489"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 1:
            content = json.dumps({u'_updated': u'Wed, 23 Aug 2017 08:39:32 GMT', u'_links': {u'self': {u'href': u'reservations/599d3f443973960001d91d6d', u'title': u'Reservation'}}, u'_created': u'Wed, 23 Aug 2017 08:39:32 GMT', u'_status': u'OK', u'_id': u'599d3f443973960001d91d6d', u'_etag': u'bafce54ac005360d45bab47a2193305ca3c01de3'})
            status_code = 200
        if json_id == 2:
            content = None
            status_code = 204
        if json_id == 3:
            content = None
            status_code = 204
        if json_id == 4:
            content = None
            status_code = 204
        self.mock_admin_remove_snapshots_OK_several_snapshots_with_force_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|reservations|states).*')
    def mock_api_admin_remove_snapshots_NOK_several_snapshots_one_NOK(self, url, request):
        json_id = self.mock_admin_remove_snapshots_NOK_several_snapshots_one_NOK_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Tue, 22 Aug 2017 12:32:08 GMT', u'lab_type': u'vsprint', u'states': [{u'_updated': u'Tue, 22 Aug 2017 12:32:08 GMT', u'lab': u'599c24483973960001d91d6a', u'build': {u'id': u'netact/product/99.17.03.0.112'}, u'snapshot_id': u'113456', u'_created': u'Tue, 22 Aug 2017 12:32:08 GMT', u'_id': u'599c24483973960001d91d6b', u'_etag': u'38c3d7c19b817c2a052b731895ed2edf5d740cea', u'snapshot_status': u'available'},{u'_updated': u'Tue, 22 Aug 2017 12:32:08 GMT', u'lab': u'599c24483973960001d91d6a', u'build': {u'id': u'netact/product/99.17.03.0.112'}, u'snapshot_id': u'3456', u'_created': u'Tue, 22 Aug 2017 12:32:08 GMT', u'_id': u'599c24483973960001d91d6b', u'_etag': u'38c3d7c19b817c2a052b731895ed2edf5d740cea', u'snapshot_status': u'available'},{u'_updated': u'Tue, 22 Aug 2017 12:32:08 GMT', u'lab': u'599c24483973960001d91d6a', u'build': {u'id': u'netact/product/99.17.03.0.112'}, u'snapshot_id': u'66777', u'_created': u'Tue, 22 Aug 2017 12:32:08 GMT', u'_id': u'599c24483973960001d91d6b', u'_etag': u'38c3d7c19b817c2a052b731895ed2edf5d740cea', u'snapshot_status': u'available'}], u'lab_name': u'vSprint7489', u'_links': {u'self': {u'href': u'labs/599c24483973960001d91d6a', u'title': u'Lab'}}, u'_created': u'Tue, 22 Aug 2017 12:32:08 GMT', u'_id': u'599c24483973960001d91d6a', u'_etag': u'0aafa68db2f614aaa9e77018406da01b5b80e200'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"vSprint7489"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 1:
            content = json.dumps({u'_updated': u'Wed, 23 Aug 2017 08:39:32 GMT', u'_links': {u'self': {u'href': u'reservations/599d3f443973960001d91d6d', u'title': u'Reservation'}}, u'_created': u'Wed, 23 Aug 2017 08:39:32 GMT', u'_status': u'OK', u'_id': u'599d3f443973960001d91d6d', u'_etag': u'bafce54ac005360d45bab47a2193305ca3c01de3'})
            status_code = 200
        if json_id == 2:
            content = None
            status_code = 204
        if json_id == 3:
            content = None
            status_code = 204
        if json_id == 4:
            content = None
            status_code = 204
        self.mock_admin_remove_snapshots_NOK_several_snapshots_one_NOK_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|reservations|states).*')
    def mock_api_admin_remove_snapshots_NOK_several_snapshots_all_NOK(self, url, request):
        json_id = self.mock_admin_remove_snapshots_NOK_several_snapshots_all_NOK_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Tue, 22 Aug 2017 12:32:08 GMT', u'lab_type': u'vsprint', u'states': [{u'_updated': u'Tue, 22 Aug 2017 12:32:08 GMT', u'lab': u'599c24483973960001d91d6a', u'build': {u'id': u'netact/product/99.17.03.0.112'}, u'snapshot_id': u'113456', u'_created': u'Tue, 22 Aug 2017 12:32:08 GMT', u'_id': u'599c24483973960001d91d6b', u'_etag': u'38c3d7c19b817c2a052b731895ed2edf5d740cea', u'snapshot_status': u'available'},{u'_updated': u'Tue, 22 Aug 2017 12:32:08 GMT', u'lab': u'599c24483973960001d91d6a', u'build': {u'id': u'netact/product/99.17.03.0.112'}, u'snapshot_id': u'3456', u'_created': u'Tue, 22 Aug 2017 12:32:08 GMT', u'_id': u'599c24483973960001d91d6b', u'_etag': u'38c3d7c19b817c2a052b731895ed2edf5d740cea', u'snapshot_status': u'available'},{u'_updated': u'Tue, 22 Aug 2017 12:32:08 GMT', u'lab': u'599c24483973960001d91d6a', u'build': {u'id': u'netact/product/99.17.03.0.112'}, u'snapshot_id': u'66777', u'_created': u'Tue, 22 Aug 2017 12:32:08 GMT', u'_id': u'599c24483973960001d91d6b', u'_etag': u'38c3d7c19b817c2a052b731895ed2edf5d740cea', u'snapshot_status': u'available'}], u'lab_name': u'vSprint7489', u'_links': {u'self': {u'href': u'labs/599c24483973960001d91d6a', u'title': u'Lab'}}, u'_created': u'Tue, 22 Aug 2017 12:32:08 GMT', u'_id': u'599c24483973960001d91d6a', u'_etag': u'0aafa68db2f614aaa9e77018406da01b5b80e200'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"vSprint7489"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 1:
            content = json.dumps({u'_updated': u'Wed, 23 Aug 2017 08:39:32 GMT', u'_links': {u'self': {u'href': u'reservations/599d3f443973960001d91d6d', u'title': u'Reservation'}}, u'_created': u'Wed, 23 Aug 2017 08:39:32 GMT', u'_status': u'OK', u'_id': u'599d3f443973960001d91d6d', u'_etag': u'bafce54ac005360d45bab47a2193305ca3c01de3'})
            status_code = 200
        if json_id == 2:
            content = None
            status_code = 422
        if json_id == 3:
            content = None
            status_code = 500
        if json_id == 4:
            content = None
            status_code = 204
        self.mock_admin_remove_snapshots_NOK_several_snapshots_all_NOK_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|reservations|states).*')
    def mock_api_admin_remove_snapshots_NOK_several_snapshots_one_NOK_with_force(self, url, request):
        json_id = self.mock_admin_remove_snapshots_NOK_several_snapshots_one_NOK_with_force_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        self._assert_force_in_url('states', url)
        self._assert_force_in_url('labs|reservations', url, False)
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Tue, 22 Aug 2017 12:32:08 GMT', u'lab_type': u'vsprint', u'states': [{u'_updated': u'Tue, 22 Aug 2017 12:32:08 GMT', u'lab': u'599c24483973960001d91d6a', u'build': {u'id': u'netact/product/99.17.03.0.112'}, u'snapshot_id': u'113456', u'_created': u'Tue, 22 Aug 2017 12:32:08 GMT', u'_id': u'599c24483973960001d91d6b', u'_etag': u'38c3d7c19b817c2a052b731895ed2edf5d740cea', u'snapshot_status': u'available'},{u'_updated': u'Tue, 22 Aug 2017 12:32:08 GMT', u'lab': u'599c24483973960001d91d6a', u'build': {u'id': u'netact/product/99.17.03.0.112'}, u'snapshot_id': u'3456', u'_created': u'Tue, 22 Aug 2017 12:32:08 GMT', u'_id': u'599c24483973960001d91d6b', u'_etag': u'38c3d7c19b817c2a052b731895ed2edf5d740cea', u'snapshot_status': u'available'},{u'_updated': u'Tue, 22 Aug 2017 12:32:08 GMT', u'lab': u'599c24483973960001d91d6a', u'build': {u'id': u'netact/product/99.17.03.0.112'}, u'snapshot_id': u'66777', u'_created': u'Tue, 22 Aug 2017 12:32:08 GMT', u'_id': u'599c24483973960001d91d6b', u'_etag': u'38c3d7c19b817c2a052b731895ed2edf5d740cea', u'snapshot_status': u'available'}], u'lab_name': u'vSprint7489', u'_links': {u'self': {u'href': u'labs/599c24483973960001d91d6a', u'title': u'Lab'}}, u'_created': u'Tue, 22 Aug 2017 12:32:08 GMT', u'_id': u'599c24483973960001d91d6a', u'_etag': u'0aafa68db2f614aaa9e77018406da01b5b80e200'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"vSprint7489"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 1:
            content = json.dumps({u'_updated': u'Wed, 23 Aug 2017 08:39:32 GMT', u'_links': {u'self': {u'href': u'reservations/599d3f443973960001d91d6d', u'title': u'Reservation'}}, u'_created': u'Wed, 23 Aug 2017 08:39:32 GMT', u'_status': u'OK', u'_id': u'599d3f443973960001d91d6d', u'_etag': u'bafce54ac005360d45bab47a2193305ca3c01de3'})
            status_code = 200
        if json_id == 2:
            content = None
            status_code = 500
        if json_id == 3:
            content = None
            status_code = 204
        if json_id == 4:
            content = None
            status_code = 204
        self.mock_admin_remove_snapshots_NOK_several_snapshots_one_NOK_with_force_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs|reservations|states.*force).*')
    def mock_api_admin_remove_snapshots_NOK_several_snapshots_all_NOK_with_force(self, url, request):
        json_id = self.mock_admin_remove_snapshots_NOK_several_snapshots_all_NOK_with_force_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        self._assert_force_in_url('states', url)
        self._assert_force_in_url('labs|reservations', url, False)
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Tue, 22 Aug 2017 12:32:08 GMT', u'lab_type': u'vsprint', u'states': [{u'_updated': u'Tue, 22 Aug 2017 12:32:08 GMT', u'lab': u'599c24483973960001d91d6a', u'build': {u'id': u'netact/product/99.17.03.0.112'}, u'snapshot_id': u'113456', u'_created': u'Tue, 22 Aug 2017 12:32:08 GMT', u'_id': u'599c24483973960001d91d6b', u'_etag': u'38c3d7c19b817c2a052b731895ed2edf5d740cea', u'snapshot_status': u'available'},{u'_updated': u'Tue, 22 Aug 2017 12:32:08 GMT', u'lab': u'599c24483973960001d91d6a', u'build': {u'id': u'netact/product/99.17.03.0.112'}, u'snapshot_id': u'3456', u'_created': u'Tue, 22 Aug 2017 12:32:08 GMT', u'_id': u'599c24483973960001d91d6b', u'_etag': u'38c3d7c19b817c2a052b731895ed2edf5d740cea', u'snapshot_status': u'available'},{u'_updated': u'Tue, 22 Aug 2017 12:32:08 GMT', u'lab': u'599c24483973960001d91d6a', u'build': {u'id': u'netact/product/99.17.03.0.112'}, u'snapshot_id': u'66777', u'_created': u'Tue, 22 Aug 2017 12:32:08 GMT', u'_id': u'599c24483973960001d91d6b', u'_etag': u'38c3d7c19b817c2a052b731895ed2edf5d740cea', u'snapshot_status': u'available'}], u'lab_name': u'vSprint7489', u'_links': {u'self': {u'href': u'labs/599c24483973960001d91d6a', u'title': u'Lab'}}, u'_created': u'Tue, 22 Aug 2017 12:32:08 GMT', u'_id': u'599c24483973960001d91d6a', u'_etag': u'0aafa68db2f614aaa9e77018406da01b5b80e200'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"vSprint7489"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 1:
            content = json.dumps({u'_updated': u'Wed, 23 Aug 2017 08:39:32 GMT', u'_links': {u'self': {u'href': u'reservations/599d3f443973960001d91d6d', u'title': u'Reservation'}}, u'_created': u'Wed, 23 Aug 2017 08:39:32 GMT', u'_status': u'OK', u'_id': u'599d3f443973960001d91d6d', u'_etag': u'bafce54ac005360d45bab47a2193305ca3c01de3'})
            status_code = 200
        if json_id == 2:
            content = json.dumps({u'_status': u'ERR', u'_error': {u'message': u'To edit a document its etag must be provided using the If-Match header', u'code': 428}})
            status_code = 428
        if json_id == 3:
            content = None
            status_code = 204
        if json_id == 4:
            content = None
            status_code = 204
        self.mock_admin_remove_snapshots_NOK_several_snapshots_all_NOK_with_force_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_admin_remove_snapshots_NOK_lab_does_not_exist(self, url, request):
        json_id = self.mock_admin_remove_snapshots_NOK_lab_does_not_exist_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [], u'_links': {u'self': {u'href': u'labs', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 0, u'page': 1}})
            status_code = 200
        self.mock_admin_remove_snapshots_NOK_lab_does_not_exist_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_admin_remove_snapshots_NOK_user_not_allowed_to_remove(self, url, request):
        json_id = self.mock_admin_remove_snapshots_NOK_user_not_allowed_to_remove_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c46', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'snapshot_id': u'956', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c47', u'_etag': u'5d3caaa6279ea58be11b7032be22c1ae743e2314', u'snapshot_status': u'available'}], u'lab_name': u'CloudLab6128', u'_links': {u'self': {u'href': u'labs/599ad1c3e0a14a0001e21c46', u'title': u'Lab'}}, u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c46', u'_etag': u'322bf6a9fa610f583b4558b9b667841e86192935'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab6128"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        if json_id == 1:
            content = json.dumps({u'_updated': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_links': {u'self': {u'href': u'reservations/599adc45e0a14a0001e21c5c', u'title': u'Reservation'}}, u'_created': u'Mon, 21 Aug 2017 13:12:37 GMT', u'_status': u'OK', u'_id': u'599adc45e0a14a0001e21c5c', u'_etag': u'9dccf9c6811967be34282ea2be69abdb79b2917a'})
            status_code = 200
        self.mock_admin_remove_snapshots_NOK_user_not_allowed_to_remove_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_admin_remove_snapshots_NOK_lab_already_reserved(self, url, request):
        json_id = self.mock_admin_remove_snapshots_NOK_lab_already_reserved_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'reverting_state', u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'states': [{u'_updated': u'Mon, 21 Aug 2017 12:27:47 GMT', u'lab': u'599ad1c3e0a14a0001e21c44', u'build': {u'id': u'netact/product/99.17.03.0.166'}, u'snapshot_id': u'56', u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'_id': u'599ad1c3e0a14a0001e21c45', u'_etag': u'18eae4a9515c08c723fd58fb35bec35f32dc59ee', u'snapshot_status': u'available'}], u'lab_name': u'sprintlab0098', u'_links': {u'self': {u'href': u'labs/599ad1c3e0a14a0001e21c44', u'title': u'Lab'}}, u'_created': u'Mon, 21 Aug 2017 12:27:47 GMT', u'reservation': {u'username': u'Pertti Keinonen', u'_updated': u'Mon, 21 Aug 2017 12:53:43 GMT', u'lab': u'599ad1c3e0a14a0001e21c44', u'_created': u'Mon, 21 Aug 2017 12:53:43 GMT', u'message': u'Lab reserved for maintanance work.', u'_id': u'599ad7d7e0a14a0001e21c5b', u'_etag': u'0fe9dd2dc3e3729af2abf015e2414509aa042112'}, u'_id': u'599ad1c3e0a14a0001e21c44', u'_etag': u'd3fb415f2eb060335e6309574fc19c2228d8a78d'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab5920"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        self.mock_admin_remove_snapshots_NOK_lab_already_reserved_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_admin_remove_snapshots_NOK_operation_cancelled_in_question(self, url, request):
        json_id = self.mock_admin_remove_snapshots_NOK_operation_cancelled_in_question_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = None
            status_code = 200
        self.mock_admin_remove_snapshots_NOK_operation_cancelled_in_question_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }


    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_show_admin_server_access_data_ok_no_data_all_labs(self, url, request):
        json_id = self.mock_show_admin_server_access_data_ok_no_data_all_labs_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab6128"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        self.mock_show_admin_server_access_data_ok_no_data_all_labs_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_show_admin_server_access_data_nok_no_data_one_lab(self, url, request):
        json_id = self.mock_show_admin_server_access_data_nok_no_data_one_lab_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab6128"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        self.mock_show_admin_server_access_data_nok_no_data_one_lab_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_show_admin_server_access_data_nok_no_data_one_lab_with_snap(self, url, request):
        json_id = self.mock_show_admin_server_access_data_nok_no_data_one_lab_with_snap_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"CloudLab6128"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        self.mock_show_admin_server_access_data_nok_no_data_one_lab_with_snap_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }


    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_show_admin_server_access_data_ok_only_lab_data_all_labs(self, url, request):
        json_id = self.mock_show_admin_server_access_data_ok_only_lab_data_all_labs_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Mon, 26 Feb 2018 07:15:51 GMT', u'lab_type': u'sprint', u'lab_name': u'sprintlab245', u'_links': {u'self': {u'href': u'labs/5a93b427ac18db000121435e', u'title': u'Lab'}}, u'_created': u'Mon, 26 Feb 2018 07:15:51 GMT', u'_id': u'5a93b427ac18db000121435e', u'_etag': u'd0ec2c5001709bbbb3ea13d3ad26bec88c3f59a7'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"sprintlab245"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        self.mock_show_admin_server_access_data_ok_only_lab_data_all_labs_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_show_admin_server_access_data_ok_only_lab_data_one_lab(self, url, request):
        json_id = self.mock_show_admin_server_access_data_ok_only_lab_data_one_lab_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Mon, 26 Feb 2018 07:15:51 GMT', u'lab_type': u'sprint', u'lab_name': u'sprintlab245', u'_links': {u'self': {u'href': u'labs/5a93b427ac18db000121435e', u'title': u'Lab'}}, u'_created': u'Mon, 26 Feb 2018 07:15:51 GMT', u'_id': u'5a93b427ac18db000121435e', u'_etag': u'd0ec2c5001709bbbb3ea13d3ad26bec88c3f59a7'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"sprintlab245"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        self.mock_show_admin_server_access_data_ok_only_lab_data_one_lab_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_show_admin_server_access_data_nok_only_lab_data_one_lab_with_snap(self, url, request):
        json_id = self.mock_show_admin_server_access_data_nok_only_lab_data_one_lab_with_snap_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Mon, 26 Feb 2018 07:15:51 GMT', u'lab_type': u'sprint', u'lab_name': u'sprintlab245', u'_links': {u'self': {u'href': u'labs/5a93b427ac18db000121435e', u'title': u'Lab'}}, u'_created': u'Mon, 26 Feb 2018 07:15:51 GMT', u'_id': u'5a93b427ac18db000121435e', u'_etag': u'd0ec2c5001709bbbb3ea13d3ad26bec88c3f59a7'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"sprintlab245"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        self.mock_show_admin_server_access_data_nok_only_lab_data_one_lab_with_snap_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_show_admin_server_access_data_ok_one_lab_data_snaps_empty(self, url, request):
        json_id = self.mock_show_admin_server_access_data_ok_one_lab_data_snaps_empty_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Mon, 26 Feb 2018 07:15:51 GMT', u'lab_type': u'sprint', u'lab_name': u'sprintlab245', u'states': [], u'_links': {u'self': {u'href': u'labs/5a93b427ac18db000121435e', u'title': u'Lab'}}, u'_created': u'Mon, 26 Feb 2018 07:15:51 GMT', u'_id': u'5a93b427ac18db000121435e', u'_etag': u'd0ec2c5001709bbbb3ea13d3ad26bec88c3f59a7'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"sprintlab245"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        self.mock_show_admin_server_access_data_ok_one_lab_data_snaps_empty_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_show_admin_server_access_data_ok_one_lab_data_one_snaps(self, url, request):
        json_id = self.mock_show_admin_server_access_data_ok_one_lab_data_one_snaps_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Mon, 26 Feb 2018 07:15:51 GMT', u'lab_type': u'sprint', u'lab_name': u'sprintlab245', u'states': [{u'_updated': u'Thu, 08 Mar 2018 06:05:20 GMT', u'lab': u'5aa0d2a0ac18db0001214417', u'build': {u'id': u'cm_n17-2/system/6762'}, u'snapshot_id': u'456', u'admin_server_access': {u'username': u'root', u'host': u'SprintLab314vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5aa0d2a0ac18db0001214418', u'_etag': u'3f04f12ebac26e1ba5bc3a3ee63b4efcdc2be661', u'snapshot_status': u'available', u'_created': u'Thu, 08 Mar 2018 06:05:20 GMT'}], u'_links': {u'self': {u'href': u'labs/5a93b427ac18db000121435e', u'title': u'Lab'}}, u'_created': u'Mon, 26 Feb 2018 07:15:51 GMT', u'_id': u'5a93b427ac18db000121435e', u'_etag': u'd0ec2c5001709bbbb3ea13d3ad26bec88c3f59a7'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"sprintlab245"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        self.mock_show_admin_server_access_data_ok_one_lab_data_one_snaps_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_show_admin_server_access_data_ok_one_lab_data_several_snaps(self, url, request):
        json_id = self.mock_show_admin_server_access_data_ok_one_lab_data_several_snaps_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Mon, 26 Feb 2018 07:15:51 GMT', u'lab_type': u'sprint', u'lab_name': u'sprintlab245', u'states': [{u'_updated': u'Thu, 08 Mar 2018 06:05:20 GMT', u'lab': u'5aa0d2a0ac18db000121441d', u'build': {u'id': u'netact/product/99.17.03.0.003'}, u'snapshot_id': u'8456', u'admin_server_access': {u'username': u'root', u'host': u'vSprint2260vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5aa0d2a0ac18db000121441e', u'_etag': u'06a54c1dd9e818cb93cc38bfd8b25f31140ae010', u'snapshot_status': u'available', u'_created': u'Thu, 08 Mar 2018 06:05:20 GMT'}, {u'_updated': u'Thu, 08 Mar 2018 06:05:20 GMT', u'lab': u'5aa0d2a0ac18db000121441d', u'build': {u'id': u'netact/product/99.17.03.0.022'}, u'snapshot_id': u'8456', u'admin_server_access': {u'username': u'root', u'host': u'vSprint2260vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5aa0d2a0ac18db000121441f', u'_etag': u'e1b9c02e00991cce5dfc958658f8939681a483b9', u'snapshot_status': u'available', u'_created': u'Thu, 08 Mar 2018 06:05:20 GMT'}, {u'_updated': u'Thu, 08 Mar 2018 06:05:20 GMT', u'lab': u'5aa0d2a0ac18db000121441d', u'build': {u'id': u'netact/product/99.17.03.0.145'}, u'snapshot_id': u'8456', u'admin_server_access': {u'username': u'root', u'host': u'vSprint2260vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5aa0d2a0ac18db0001214420', u'_etag': u'10f5357f1c34cc5e57d7b9a8293da278821994d1', u'snapshot_status': u'available', u'_created': u'Thu, 08 Mar 2018 06:05:20 GMT'}, {u'_updated': u'Thu, 08 Mar 2018 06:05:20 GMT', u'lab': u'5aa0d2a0ac18db0001214417', u'build': {u'id': u'cm_n17-2/system/6762'}, u'snapshot_id': u'456', u'admin_server_access': {u'username': u'root', u'host': u'SprintLab314vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5aa0d2a0ac18db0001214418', u'_etag': u'3f04f12ebac26e1ba5bc3a3ee63b4efcdc2be661', u'snapshot_status': u'available', u'_created': u'Thu, 08 Mar 2018 06:05:20 GMT'},], u'_links': {u'self': {u'href': u'labs/5a93b427ac18db000121435e', u'title': u'Lab'},}, u'_created': u'Mon, 26 Feb 2018 07:15:51 GMT', u'_id': u'5a93b427ac18db000121435e', u'_etag': u'd0ec2c5001709bbbb3ea13d3ad26bec88c3f59a7'}], u'_links': {u'self': {u'href': u'labs?where={"lab_name":"sprintlab245"}', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 1, u'page': 1}})
            status_code = 200
        self.mock_show_admin_server_access_data_ok_one_lab_data_several_snaps_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_show_admin_server_access_data_ok_mass_labs_data(self, url, request):
        json_id = self.mock_show_admin_server_access_data_ok_mass_labs_data_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))
        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Thu, 08 Mar 2018 06:05:20 GMT', u'lab_type': u'sprint', u'states': [{u'_updated': u'Thu, 08 Mar 2018 06:05:20 GMT', u'lab': u'5aa0d2a0ac18db0001214415', u'build': {u'id': u'cm_n17-5/system/3426'}, u'snapshot_id': u'3456', u'admin_server_access': {u'username': u'root', u'host': u'SprintLab576vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5aa0d2a0ac18db0001214416', u'_etag': u'fada7a831596703d25d4953af22a545fc10f30cc', u'snapshot_status': u'available', u'_created': u'Thu, 08 Mar 2018 06:05:20 GMT'}], u'lab_name': u'SprintLab576', u'_links': {u'self': {u'href': u'labs/5aa0d2a0ac18db0001214415', u'title': u'Lab'}}, u'_created': u'Thu, 08 Mar 2018 06:05:20 GMT', u'_id': u'5aa0d2a0ac18db0001214415', u'_etag': u'98606bc2f8b75b9f155fc2f2bae03538ef874ddd'}, {u'status': u'ready', u'_updated': u'Thu, 08 Mar 2018 06:05:20 GMT', u'lab_type': u'other', u'states': [], u'lab_name': u'SprintLab314', u'_links': {u'self': {u'href': u'labs/5aa0d2a0ac18db0001214417', u'title': u'Lab'}}, u'_created': u'Thu, 08 Mar 2018 06:05:20 GMT', u'_id': u'5aa0d2a0ac18db0001214417', u'_etag': u'19f8832a9058380322a5b1bb0af90af94c2384ea'}, {u'status': u'reverting_state', u'_updated': u'Thu, 08 Mar 2018 06:05:20 GMT', u'states': [{u'_updated': u'Thu, 08 Mar 2018 06:05:20 GMT', u'lab': u'5aa0d2a0ac18db0001214419', u'build': {u'id': u'netact/product/99.17.03.0.166'}, u'snapshot_id': u'56', u'admin_server_access': {u'username': u'root', u'host': u'CloudLab416vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5aa0d2a0ac18db000121441a', u'_etag': u'bbaf886f348701eba05cbd208b8371432ef311b5', u'snapshot_status': u'available', u'_created': u'Thu, 08 Mar 2018 06:05:20 GMT'}], u'lab_name': u'CloudLab416', u'_links': {u'self': {u'href': u'labs/5aa0d2a0ac18db0001214419', u'title': u'Lab'}}, u'_created': u'Thu, 08 Mar 2018 06:05:20 GMT', u'_id': u'5aa0d2a0ac18db0001214419', u'_etag': u'cf100153f5dfb34f9a4f9e81300ca320dffb0f82'}, {u'status': u'ready', u'_updated': u'Thu, 08 Mar 2018 06:05:20 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Thu, 08 Mar 2018 06:05:20 GMT', u'lab': u'5aa0d2a0ac18db000121441b', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'snapshot_id': u'956', u'admin_server_access': {u'username': u'root', u'host': u'CloudLab9021vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5aa0d2a0ac18db000121441c', u'_etag': u'e8b4b270e47d51ccfda6b62608dd81760f8fdf92', u'snapshot_status': u'available', u'_created': u'Thu, 08 Mar 2018 06:05:20 GMT'}], u'lab_name': u'CloudLab9021', u'_links': {u'self': {u'href': u'labs/5aa0d2a0ac18db000121441b', u'title': u'Lab'}}, u'_created': u'Thu, 08 Mar 2018 06:05:20 GMT', u'_id': u'5aa0d2a0ac18db000121441b', u'_etag': u'83b460b3300654639f8b9dedc35ae31c3034da6c'}, {u'status': u'state_operation_failed', u'_updated': u'Thu, 08 Mar 2018 06:05:20 GMT', u'lab_type': u'vsprint', u'states': [{u'_updated': u'Thu, 08 Mar 2018 06:05:20 GMT', u'lab': u'5aa0d2a0ac18db000121441d', u'build': {u'id': u'netact/product/99.17.03.0.003'}, u'snapshot_id': u'8456', u'admin_server_access': {u'username': u'root', u'host': u'vSprint2260vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5aa0d2a0ac18db000121441e', u'_etag': u'06a54c1dd9e818cb93cc38bfd8b25f31140ae010', u'snapshot_status': u'available', u'_created': u'Thu, 08 Mar 2018 06:05:20 GMT'}, {u'_updated': u'Thu, 08 Mar 2018 06:05:20 GMT', u'lab': u'5aa0d2a0ac18db000121441d', u'build': {u'id': u'netact/product/99.17.03.0.022'}, u'snapshot_id': u'8456', u'admin_server_access': {u'username': u'root', u'host': u'vSprint2260vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5aa0d2a0ac18db000121441f', u'_etag': u'e1b9c02e00991cce5dfc958658f8939681a483b9', u'snapshot_status': u'available', u'_created': u'Thu, 08 Mar 2018 06:05:20 GMT'}, {u'_updated': u'Thu, 08 Mar 2018 06:05:20 GMT', u'lab': u'5aa0d2a0ac18db000121441d', u'build': {u'id': u'netact/product/99.17.03.0.145'}, u'snapshot_id': u'8456', u'admin_server_access': {u'username': u'root', u'host': u'vSprint2260vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5aa0d2a0ac18db0001214420', u'_etag': u'10f5357f1c34cc5e57d7b9a8293da278821994d1', u'snapshot_status': u'available', u'_created': u'Thu, 08 Mar 2018 06:05:20 GMT'}], u'lab_name': u'vSprint2260', u'_links': {u'self': {u'href': u'labs/5aa0d2a0ac18db000121441d', u'title': u'Lab'}}, u'_created': u'Thu, 08 Mar 2018 06:05:20 GMT', u'reservation': {u'username': u'testuser', u'_updated': u'Thu, 08 Mar 2018 06:05:20 GMT', u'lab': u'5aa0d2a0ac18db000121441d', u'_created': u'Thu, 08 Mar 2018 06:05:20 GMT', u'_id': u'5aa0d2a0ac18db0001214421', u'_etag': u'277158a7d09bd7903268e19360a291fcfef18e59'}, u'_id': u'5aa0d2a0ac18db000121441d', u'_etag': u'e938c01c900539b7132e5fe66947236fd57cb0cd'}, {u'status': u'reverting_state', u'_updated': u'Thu, 08 Mar 2018 06:05:20 GMT', u'lab_type': u'vsprint', u'states': [{u'_updated': u'Thu, 08 Mar 2018 06:05:20 GMT', u'lab': u'5aa0d2a0ac18db0001214422', u'build': {u'id': u'netact/product/99.17.03.0.004'}, u'snapshot_id': u'7456', u'admin_server_access': {u'username': u'root', u'host': u'vSprint5403vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5aa0d2a0ac18db0001214423', u'_etag': u'd9b20f7594c54c01ff8d1ddadb88afb7e4a265ff', u'snapshot_status': u'available', u'_created': u'Thu, 08 Mar 2018 06:05:20 GMT'}, {u'_updated': u'Thu, 08 Mar 2018 06:05:20 GMT', u'lab': u'5aa0d2a0ac18db0001214422', u'build': {u'id': u'netact/product/99.17.03.0.424'}, u'snapshot_id': u'7456', u'admin_server_access': {u'username': u'root', u'host': u'vSprint5403vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5aa0d2a0ac18db0001214424', u'_etag': u'97df8a002c82cede274eeeb1134749570b8b9499', u'snapshot_status': u'available', u'_created': u'Thu, 08 Mar 2018 06:05:20 GMT'}, {u'_updated': u'Thu, 08 Mar 2018 06:05:20 GMT', u'lab': u'5aa0d2a0ac18db0001214422', u'build': {u'id': u'netact/product/99.17.03.0.645'}, u'snapshot_id': u'7456', u'admin_server_access': {u'username': u'root', u'host': u'vSprint5403vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5aa0d2a0ac18db0001214425', u'_etag': u'9461047912f758bebea408126f8449c16de44e94', u'snapshot_status': u'available', u'_created': u'Thu, 08 Mar 2018 06:05:20 GMT'}], u'lab_name': u'vSprint5403', u'_links': {u'self': {u'href': u'labs/5aa0d2a0ac18db0001214422', u'title': u'Lab'}}, u'_created': u'Thu, 08 Mar 2018 06:05:20 GMT', u'reservation': {u'username': u'testuser', u'_updated': u'Thu, 08 Mar 2018 06:05:20 GMT', u'lab': u'5aa0d2a0ac18db0001214422', u'_created': u'Thu, 08 Mar 2018 06:05:20 GMT', u'_id': u'5aa0d2a0ac18db0001214426', u'_etag': u'e2030b52afdbcf3667dc7a45e3e24a8609deac4d'}, u'_id': u'5aa0d2a0ac18db0001214422', u'_etag': u'87d5f46a4189bb657eeda688503392fee68a53f4'}, {u'status': u'ready', u'_updated': u'Thu, 08 Mar 2018 06:05:20 GMT', u'lab_type': u'vsprint', u'states': [{u'_updated': u'Thu, 08 Mar 2018 06:05:20 GMT', u'lab': u'5aa0d2a0ac18db0001214427', u'build': {u'id': u'netact/product/99.17.03.0.303'}, u'snapshot_id': u'22456', u'admin_server_access': {u'username': u'root', u'host': u'SprintLab2354vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5aa0d2a0ac18db0001214428', u'_etag': u'7ced559d4a8f0b057705b80579d6ad3a12d50061', u'snapshot_status': u'available', u'_created': u'Thu, 08 Mar 2018 06:05:20 GMT'}, {u'_updated': u'Thu, 08 Mar 2018 06:05:20 GMT', u'lab': u'5aa0d2a0ac18db0001214427', u'build': {u'id': u'netact/product/99.17.03.0.522'}, u'snapshot_id': u'22456', u'admin_server_access': {u'username': u'root', u'host': u'SprintLab2354vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5aa0d2a0ac18db0001214429', u'_etag': u'4ed56e018390396d787fea9937d64522e682f31a', u'snapshot_status': u'available', u'_created': u'Thu, 08 Mar 2018 06:05:20 GMT'}, {u'_updated': u'Thu, 08 Mar 2018 06:05:20 GMT', u'lab': u'5aa0d2a0ac18db0001214427', u'build': {u'id': u'netact/product/99.17.03.0.645'}, u'snapshot_id': u'22456', u'admin_server_access': {u'username': u'root', u'host': u'SprintLab2354vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5aa0d2a0ac18db000121442a', u'_etag': u'dea919472c460efaae3ba05e131d053c24bbc7b2', u'snapshot_status': u'available', u'_created': u'Thu, 08 Mar 2018 06:05:20 GMT'}], u'lab_name': u'SprintLab2354', u'_links': {u'self': {u'href': u'labs/5aa0d2a0ac18db0001214427', u'title': u'Lab'}}, u'_created': u'Thu, 08 Mar 2018 06:05:20 GMT', u'_id': u'5aa0d2a0ac18db0001214427', u'_etag': u'8dfb25cbc1ef47bd02707eeb211c0ebf0b725909'}, {u'status': u'ready', u'_updated': u'Thu, 08 Mar 2018 06:05:20 GMT', u'lab_type': u'vsprint', u'states': [{u'_updated': u'Thu, 08 Mar 2018 06:05:20 GMT', u'lab': u'5aa0d2a0ac18db000121442b', u'build': {u'id': u'netact/product/99.17.03.0.112'}, u'snapshot_id': u'113456', u'admin_server_access': {u'username': u'root', u'host': u'vSprint2368vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5aa0d2a0ac18db000121442c', u'_etag': u'ae5e5e02b34cfe8e3f8232d5c94d777f9f05909f', u'snapshot_status': u'available', u'_created': u'Thu, 08 Mar 2018 06:05:20 GMT'}], u'lab_name': u'vSprint2368', u'_links': {u'self': {u'href': u'labs/5aa0d2a0ac18db000121442b', u'title': u'Lab'}}, u'_created': u'Thu, 08 Mar 2018 06:05:20 GMT', u'_id': u'5aa0d2a0ac18db000121442b', u'_etag': u'b0c5d68ff243392441bcee1605fdd619ec4922c8'}], u'_links': {u'self': {u'href': u'labs', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 8, u'page': 1}})
            status_code = 200
        self.mock_show_admin_server_access_data_ok_mass_labs_data_json_id += 1
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
               }

    @urlmatch(netloc=r'.*fakeserver.*', path=r'.*(labs).*')
    def mock_api_mock_show_snapshot_OK_one_snapshot_unavailable_data(self, url, request):
        json_id = self.mock_show_snapshot_OK_one_snapshot_unavailable_data_json_id
        log.debug("MOCK FUNCTION: {}".format(inspect.stack()[0][3]))

        if json_id == 0:
            content = json.dumps({u'_items': [{u'status': u'ready', u'_updated': u'Tue, 14 Aug 2018 10:12:57 GMT', u'previously_reverted_state': {u'_updated': u'Tue, 14 Aug 2018 06:54:55 GMT', u'lab': u'5b727cbf4f7e99000179b2df', u'build': {u'id': u'cm_n17-5/system/3426'}, u'snapshot_id': u'3456', u'admin_server_access': {u'username': u'root', u'host': u'SprintLab311vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5b727cbf4f7e99000179b2e0', u'_etag': u'cefc0c0e074cd219fa67c651c42deaa5c536abd4', u'snapshot_status': u'available', u'_created': u'Tue, 14 Aug 2018 06:54:55 GMT'}, u'lab_type': u'sprint', u'states': [], u'lab_name': u'SprintLab311', u'_links': {u'self': {u'href': u'labs/5b727cbf4f7e99000179b2df', u'title': u'Lab'}}, u'_created': u'Tue, 14 Aug 2018 06:54:55 GMT', u'reservation': {u'username': u'admin', u'_updated': u'Tue, 14 Aug 2018 10:12:27 GMT', u'lab': u'5b727cbf4f7e99000179b2df', u'_created': u'Tue, 14 Aug 2018 10:12:27 GMT', u'message': u'akselioltaalakesalla18', u'_id': u'5b72ab0b4f7e990001edc07f', u'_etag': u'02e81b7b9d5b45fceb1dfd9ff50f0fdd800600ea'}, u'_id': u'5b727cbf4f7e99000179b2df', u'_etag': u'2814ce5ccc743fa5c756ade00252ad8d82a52ca3'}, {u'status': u'ready', u'_updated': u'Tue, 14 Aug 2018 06:54:55 GMT', u'lab_type': u'other', u'states': [{u'_updated': u'Tue, 14 Aug 2018 06:54:55 GMT', u'lab': u'5b727cbf4f7e99000179b2e1', u'build': {u'id': u'cm_n17-2/system/6762'}, u'snapshot_id': u'456', u'admin_server_access': {u'username': u'root', u'host': u'SprintLab6936vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5b727cbf4f7e99000179b2e2', u'_etag': u'6bbbefd13fd3af726dc6f930bd1327bfa36059dd', u'snapshot_status': u'available', u'_created': u'Tue, 14 Aug 2018 06:54:55 GMT'}], u'lab_name': u'SprintLab6936', u'_links': {u'self': {u'href': u'labs/5b727cbf4f7e99000179b2e1', u'title': u'Lab'}}, u'_created': u'Tue, 14 Aug 2018 06:54:55 GMT', u'_id': u'5b727cbf4f7e99000179b2e1', u'_etag': u'afc6990628c4f5e847f59f0c067fe86aaa5d65ad'}, {u'status': u'reverting_state', u'_updated': u'Tue, 14 Aug 2018 06:54:55 GMT', u'states': [{u'_updated': u'Tue, 14 Aug 2018 06:54:55 GMT', u'lab': u'5b727cbf4f7e99000179b2e3', u'build': {u'id': u'netact/product/99.17.03.0.166'}, u'snapshot_id': u'56', u'admin_server_access': {u'username': u'root', u'host': u'CloudLab3672vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5b727cbf4f7e99000179b2e4', u'_etag': u'fa047276a013f9ca7d7d93d341a9d221413b56e2', u'snapshot_status': u'available', u'_created': u'Tue, 14 Aug 2018 06:54:55 GMT'}], u'lab_name': u'CloudLab3672', u'_links': {u'self': {u'href': u'labs/5b727cbf4f7e99000179b2e3', u'title': u'Lab'}}, u'_created': u'Tue, 14 Aug 2018 06:54:55 GMT', u'_id': u'5b727cbf4f7e99000179b2e3', u'_etag': u'399d975093f195593c373b673a09a117cbf758cb'}, {u'status': u'ready', u'_updated': u'Tue, 14 Aug 2018 06:54:55 GMT', u'lab_type': u'cloud', u'states': [{u'_updated': u'Tue, 14 Aug 2018 06:54:55 GMT', u'lab': u'5b727cbf4f7e99000179b2e5', u'build': {u'id': u'netact/product/99.17.03.0.123'}, u'snapshot_id': u'956', u'admin_server_access': {u'username': u'root', u'host': u'CloudLab6700vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5b727cbf4f7e99000179b2e6', u'_etag': u'935fafae0219ca3984ffe336f2a1322e605e6ba9', u'snapshot_status': u'available', u'_created': u'Tue, 14 Aug 2018 06:54:55 GMT'}], u'lab_name': u'CloudLab6700', u'_links': {u'self': {u'href': u'labs/5b727cbf4f7e99000179b2e5', u'title': u'Lab'}}, u'_created': u'Tue, 14 Aug 2018 06:54:55 GMT', u'_id': u'5b727cbf4f7e99000179b2e5', u'_etag': u'5b2ffa6948ce074a7f2ba5c2f174d7ae1183c8ba'}, {u'status': u'state_operation_failed', u'_updated': u'Tue, 14 Aug 2018 06:54:55 GMT', u'lab_type': u'vsprint', u'states': [{u'_updated': u'Tue, 14 Aug 2018 06:54:55 GMT', u'lab': u'5b727cbf4f7e99000179b2e7', u'build': {u'id': u'netact/product/99.17.03.0.003'}, u'snapshot_id': u'8456', u'admin_server_access': {u'username': u'root', u'host': u'vSprint9711vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5b727cbf4f7e99000179b2e8', u'_etag': u'6ec6a9783b1322ff25f67a6a5aae8610ae8ffe7c', u'snapshot_status': u'available', u'_created': u'Tue, 14 Aug 2018 06:54:55 GMT'}, {u'_updated': u'Tue, 14 Aug 2018 06:54:55 GMT', u'lab': u'5b727cbf4f7e99000179b2e7', u'build': {u'id': u'netact/product/99.17.03.0.022'}, u'snapshot_id': u'8456', u'admin_server_access': {u'username': u'root', u'host': u'vSprint9711vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5b727cbf4f7e99000179b2e9', u'_etag': u'8342b34d996e51739173a87a7eeb66a3cd531efd', u'snapshot_status': u'available', u'_created': u'Tue, 14 Aug 2018 06:54:55 GMT'}, {u'_updated': u'Tue, 14 Aug 2018 06:54:55 GMT', u'lab': u'5b727cbf4f7e99000179b2e7', u'build': {u'id': u'netact/product/99.17.03.0.145'}, u'snapshot_id': u'8456', u'admin_server_access': {u'username': u'root', u'host': u'vSprint9711vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5b727cbf4f7e99000179b2ea', u'_etag': u'92dfe04483fd2f3467dff71244f937c7203e4124', u'snapshot_status': u'available', u'_created': u'Tue, 14 Aug 2018 06:54:55 GMT'}], u'lab_name': u'vSprint9711', u'_links': {u'self': {u'href': u'labs/5b727cbf4f7e99000179b2e7', u'title': u'Lab'}}, u'_created': u'Tue, 14 Aug 2018 06:54:55 GMT', u'reservation': {u'username': u'testuser', u'_updated': u'Tue, 14 Aug 2018 06:54:55 GMT', u'lab': u'5b727cbf4f7e99000179b2e7', u'_created': u'Tue, 14 Aug 2018 06:54:55 GMT', u'_id': u'5b727cbf4f7e99000179b2eb', u'_etag': u'ddd026f6b53577c0c03284e977562dec8f546ab5'}, u'_id': u'5b727cbf4f7e99000179b2e7', u'_etag': u'c79d93122f1920b018cc5d17ee65d3adb4c89a2c'}, {u'status': u'reverting_state', u'_updated': u'Tue, 14 Aug 2018 06:54:56 GMT', u'lab_type': u'vsprint', u'states': [{u'_updated': u'Tue, 14 Aug 2018 06:54:56 GMT', u'lab': u'5b727cc04f7e99000179b2ec', u'build': {u'id': u'netact/product/99.17.03.0.004'}, u'snapshot_id': u'7456', u'admin_server_access': {u'username': u'root', u'host': u'vSprint6935vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5b727cc04f7e99000179b2ed', u'_etag': u'f7a510e69f735e8d06046f69e202db5a2ebf4736', u'snapshot_status': u'available', u'_created': u'Tue, 14 Aug 2018 06:54:56 GMT'}, {u'_updated': u'Tue, 14 Aug 2018 06:54:56 GMT', u'lab': u'5b727cc04f7e99000179b2ec', u'build': {u'id': u'netact/product/99.17.03.0.424'}, u'snapshot_id': u'7456', u'admin_server_access': {u'username': u'root', u'host': u'vSprint6935vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5b727cc04f7e99000179b2ee', u'_etag': u'd008fa58ea9c00a9f52d6a88fdbe8d5992154797', u'snapshot_status': u'available', u'_created': u'Tue, 14 Aug 2018 06:54:56 GMT'}, {u'_updated': u'Tue, 14 Aug 2018 06:54:56 GMT', u'lab': u'5b727cc04f7e99000179b2ec', u'build': {u'id': u'netact/product/99.17.03.0.645'}, u'snapshot_id': u'7456', u'admin_server_access': {u'username': u'root', u'host': u'vSprint6935vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5b727cc04f7e99000179b2ef', u'_etag': u'c4f53e0658431753799b79ac9c62d94f7064429c', u'snapshot_status': u'available', u'_created': u'Tue, 14 Aug 2018 06:54:56 GMT'}], u'lab_name': u'vSprint6935', u'_links': {u'self': {u'href': u'labs/5b727cc04f7e99000179b2ec', u'title': u'Lab'}}, u'_created': u'Tue, 14 Aug 2018 06:54:56 GMT', u'reservation': {u'username': u'testuser', u'_updated': u'Tue, 14 Aug 2018 06:54:56 GMT', u'lab': u'5b727cc04f7e99000179b2ec', u'_created': u'Tue, 14 Aug 2018 06:54:56 GMT', u'_id': u'5b727cc04f7e99000179b2f0', u'_etag': u'7bd763c08d2618182e84a3ed53c45f5160a11424'}, u'_id': u'5b727cc04f7e99000179b2ec', u'_etag': u'58b12715d8edfe06aae0a7968b2e300f129427ad'}, {u'status': u'ready', u'_updated': u'Tue, 14 Aug 2018 10:12:31 GMT', u'previously_reverted_state': {u'_updated': u'Tue, 14 Aug 2018 06:54:56 GMT', u'lab': u'5b727cc04f7e99000179b2f1', u'build': {u'id': u'netact/product/99.17.03.0.303'}, u'snapshot_id': u'22456', u'admin_server_access': {u'username': u'root', u'host': u'SprintLab4761vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5b727cc04f7e99000179b2f2', u'_etag': u'38cbc58ac4065285d442f503626e53c227b0ef4e', u'snapshot_status': u'available', u'_created': u'Tue, 14 Aug 2018 06:54:56 GMT'}, u'lab_type': u'vsprint', u'states': [{u'_updated': u'Tue, 14 Aug 2018 06:54:56 GMT', u'lab': u'5b727cc04f7e99000179b2f1', u'build': {u'id': u'netact/product/99.17.03.0.303'}, u'snapshot_id': u'22456', u'admin_server_access': {u'username': u'root', u'host': u'SprintLab4761vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5b727cc04f7e99000179b2f2', u'_etag': u'38cbc58ac4065285d442f503626e53c227b0ef4e', u'snapshot_status': u'available', u'_created': u'Tue, 14 Aug 2018 06:54:56 GMT'}, {u'_updated': u'Tue, 14 Aug 2018 06:54:56 GMT', u'lab': u'5b727cc04f7e99000179b2f1', u'build': {u'id': u'netact/product/99.17.03.0.522'}, u'snapshot_id': u'22456', u'admin_server_access': {u'username': u'root', u'host': u'SprintLab4761vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5b727cc04f7e99000179b2f3', u'_etag': u'e50855c6510462a5ec808275f66ca40a0d32be0c', u'snapshot_status': u'available', u'_created': u'Tue, 14 Aug 2018 06:54:56 GMT'}, {u'_updated': u'Tue, 14 Aug 2018 06:54:56 GMT', u'lab': u'5b727cc04f7e99000179b2f1', u'build': {u'id': u'netact/product/99.17.03.0.645'}, u'snapshot_id': u'22456', u'admin_server_access': {u'username': u'root', u'host': u'SprintLab4761vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5b727cc04f7e99000179b2f4', u'_etag': u'e97421e3e36264f62310309462a360cc4642f607', u'snapshot_status': u'available', u'_created': u'Tue, 14 Aug 2018 06:54:56 GMT'}], u'lab_name': u'SprintLab4761', u'_links': {u'self': {u'href': u'labs/5b727cc04f7e99000179b2f1', u'title': u'Lab'}}, u'_created': u'Tue, 14 Aug 2018 06:54:56 GMT', u'reservation': {u'username': u'admin', u'_updated': u'Tue, 14 Aug 2018 10:11:59 GMT', u'lab': u'5b727cc04f7e99000179b2f1', u'_created': u'Tue, 14 Aug 2018 10:11:59 GMT', u'message': u'akseliolikesatoissa18taalla', u'_id': u'5b72aaef4f7e990001edc07d', u'_etag': u'0aef104a784648e3568eac44b4c5ddb9298df5c5'}, u'_id': u'5b727cc04f7e99000179b2f1', u'_etag': u'69e568c6c385976b5e81dbf1e3d2a5ce1eb12fc2'}, {u'status': u'ready', u'_updated': u'Tue, 14 Aug 2018 06:54:56 GMT', u'lab_type': u'vsprint', u'states': [{u'_updated': u'Tue, 14 Aug 2018 06:54:56 GMT', u'lab': u'5b727cc04f7e99000179b2f5', u'build': {u'id': u'netact/product/99.17.03.0.112'}, u'snapshot_id': u'113456', u'admin_server_access': {u'username': u'root', u'host': u'vSprint972vm1.netact.nsn-rdnet.net', u'password': u'nasroot', u'protocol': u'ssh', u'port': 22}, u'_id': u'5b727cc04f7e99000179b2f6', u'_etag': u'c3ab56df7448a61eec3469743e404cd40ab7cc7f', u'snapshot_status': u'available', u'_created': u'Tue, 14 Aug 2018 06:54:56 GMT'}], u'lab_name': u'vSprint972', u'_links': {u'self': {u'href': u'labs/5b727cc04f7e99000179b2f5', u'title': u'Lab'}}, u'_created': u'Tue, 14 Aug 2018 06:54:56 GMT', u'_id': u'5b727cc04f7e99000179b2f5', u'_etag': u'f84c425c0fcf34415c352ad4dedd4ac14fa91a90'}], u'_links': {u'self': {u'href': u'labs', u'title': u'labs'}, u'parent': {u'href': u'/', u'title': u'home'}}, u'_meta': {u'max_results': 25, u'total': 8, u'page': 1}})
            status_code = 0
        return {'status_code': status_code,
                'content': content,
                'headers': {'content-type': 'application/json'}
                }


    ###############################################################################################################
    # FUNCTIONS
    ###############################################################################################################

    def _trace_test_name(self, func_name, argv):
        cmdline = "python client.py "
        if argv:
            for arg in argv:
                cmdline += arg + " "
        log.debug('*'*80)
        log.debug("TEST: {}({})".
                  format(str(func_name), str(argv)))
        log.debug("      {}".format(cmdline))
        log.debug('*'*80)

    def _command_line_operation_check(self, test_name, argv,
                                      except_name, except_msg,
                                      stdout_data=None,
                                      stdout_not_match_data=None,
                                      outfile=None,
                                      logfile=None):
        self._trace_test_name(test_name, argv)
        log.debug("Expected results  [{}:{}:{}]".
                  format(except_name, except_msg, stdout_data))

        try:
            client.execute_command_line(client.parse_command_line(argv))
        except except_name as e:
            log.debug("EXCEPTION: [e.type:{},e.message:{}]".
                      format(type(e), e.message))
            self.assertEqual(except_msg, e.message)
            raise
        finally:
            self._assert_stdout_value(stdout_data, stdout_not_match_data, outfile)
            self._assert_logfile_data(logfile)

    def _assert_stdout_value(self, stdout_data, stdout_not_match_data, outfile=None):
        source = "stdout"
        if outfile:
            stdout_value = self._read_data_from_file(outfile)
            source = " from file {}".format(outfile)
        else:
            stdout_value = sys.stdout.getvalue()
            stdout_value += sys.stderr.getvalue()
        log.debug("STDOUT src:'{}' value:\n'{}'".format(source, str(stdout_value)))
        if stdout_data:
            value_wo_newline = stdout_value.replace("\n", "")
            self.assertRegexpMatches(value_wo_newline, stdout_data)
        if stdout_not_match_data:
            self.assertNotRegexpMatches(stdout_value, stdout_not_match_data)

    def _assert_logfile_data(self, logfile=None):
        source = ""
        if logfile:
            log_data = self._read_data_from_file(logfile)
            source = " from file {}".format(logfile, log_data)
            log.info(source)

    def _assert_force_in_url(self, match_str, url, positive=True):
        force_str = 'force'
        match = re.compile(match_str)
        if match.search(url.path):
            if positive:
                self.assertEqual(url.query, force_str)
            else:
                self.assertNotEqual(url.query, force_str)

    def _assert_param_exists_in_request_data(self, param, url, request, positive=True):
        ERROR_FORMAT = "Request data failure: '{}' can {} be found from '{}' body: '{}'"
        param_exists = False
        dict_data = json.loads(request.body)
        if param in dict_data:
            param_exists = True
        else:
            match = re.compile(param)
            if match.search(request.body):
                param_exists = True
        if positive:
            self.assertTrue(param_exists, ERROR_FORMAT.format(param, "not", url.path, request.body))
        else:
            self.assertFalse(param_exists, ERROR_FORMAT.format(param, "", url.path, request.body))

    def _read_data_from_file(self, outfile):
        content = ""
        with open(outfile, 'r') as content_file:
            content = content_file.read()
            log.info(" *** Reading data from file '{}'".format(outfile))
            log.info("      content: '{}'".format(content))
        return content










    ############################################################################################
    # Test functions
    ############################################################################################

    def test_clear_env_variables_OK(self):
        client.clear_env_variables()

    def test_load_json_content_OK(self):
        expected_results = {"ee": "dd"}
        content = json.dumps({"ee": "dd"})
        result = client.load_json_content(content)
        self.assertEqual(result, expected_results)

    def test_load_json_content_NOK_invalid_data(self):
        with self.assertRaises(AttributeError):
            content = {"ee", "dd"}
            result = client.load_json_content(content)
            log.info(result)

    def test_parse_command_line_no_params(self):
        with self.assertRaises(SystemExit):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               [''], SystemExit, 2,
                                               "invalid choice:.*'release-lab'")

    def test_parse_command_line_no_params2(self):
        with self.assertRaises(SystemExit):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               None, SystemExit, 2)

    def test_parse_command_line_help_params(self):
        with self.assertRaises(SystemExit):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['-h'], SystemExit, 0,
                                               "{request-lab,release-lab,change-lab-reservation,pr")

    def test_parse_command_line_help2_params(self):
        with self.assertRaises(SystemExit):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--help'], SystemExit, 0,
                                               "{request-lab,release-lab,change-lab-reservation,pr")

    def test_parse_command_line_wrong_operation(self):
        with self.assertRaises(SystemExit):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['show_labs'], SystemExit, 2,
                                               "invalid choice:")

    def test_parse_command_line_show_labs_no_username(self):
        with self.assertRaises(SystemExit):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['show-labs'], SystemExit, 2,
                                               "error: argument -u/--username is required")

    def test_parse_command_line_create_test_labs_ok(self):
        with HTTMock(self.mock_api_create_labs_OK):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['-u', 'tester', '-url', url, 'create-test-labs'], SystemExit, 0,
                                               "")

    def test_parse_command_line_show_labs_ok(self):
        with HTTMock(self.mock_api_labs_OK):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['-u', 'tester', '-url', url, 'show-labs'], SystemExit, 0,
                                               "NA17_2 to NA17_5 upgrade tefst")

    def test_parse_command_line_show_labs_with_html_ouput(self):
        with HTTMock(self.mock_api_labs_OK):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-url', url, '-o', 'HTML', 'show-labs'
                                                ], SystemExit, 0,
                                               '.*><p>netact/product/99.17.03.0.123</p></td><td>RESERVED</td><td>taako</td><td>queued_for_initialization</td></tr><tr valign="top"><td>CloudLab1247</td><td style="text-align:left" valign="top" ><p>netact/product/99.17.03.0.123</p></td><td>RESERVED</td><td>taako</td><.*')

    def test_parse_command_line_show_labs_with_html_ouput_when_there_are_no_labs_in_pool(self):
        with HTTMock(self.mock_api_labs_NOK_lab_not_found):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-url', url, '-o', 'HTML', 'show-labs'
                                                ], SystemExit, 0,
                                               '.*>Lab status</th></tr> </table> </div> </body> </html>')

    def test_parse_command_line_show_labs_ok_into_file(self):
        with HTTMock(self.mock_api_labs_OK):
            outfile = "testfile_show_labs.txt"
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['-u', 'tester', '-f', outfile, '-url', url, 'show-labs'], SystemExit, 0,
                                               "NA17_2 to NA17_5 upgrade tefst",
                                               None,
                                               outfile)
            os.remove(outfile)

    def test_parse_command_line_show_labs_ok_verbose_mode(self):
        with HTTMock(self.mock_api_labs_OK):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['-u', 'tester', '-v', '-url', url, 'show-labs'], SystemExit, 0,
                                               "Lab_id: labs/[A-Fa-f0-9]+ ,.*host: 'sprintlab302vm1.*password: 'admin',")

    def test_parse_command_line_show_labs_ok_paging_test(self):
        with HTTMock(self.mock_api_labs_OK_paging_case):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['-u', 'tester', '-url', url, 'show-labs'], SystemExit, 0,
                                               "NA17_2 to NA17_5 upgrade tefst")

    def test_parse_command_line_show_labs_ok_filtered_by_FREE(self):
        with HTTMock(self.mock_api_labs_OK):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['-u', 'tester', '-url', url, 'show-labs', '--filtered-by', 'FREE'], SystemExit, 0,
                                               "(FREE.*CloudLab472)",
                                               "RESERVED")

    def test_parse_command_line_show_labs_ok_filtered_by_RESERVED(self):
        with HTTMock(self.mock_api_labs_OK):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['-u', 'tester', '-url', url, 'show-labs', '--filtered-by', 'RESERVED'], SystemExit, 0,
                                               "(RESERVED.*CloudLab247)",
                                               "FREE")

    def test_parse_command_line_show_labs_ok_reservation_null(self):
        with HTTMock(self.mock_api_labs_OK_reservation_null):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['-u', 'tester', '-url', url, 'show-labs'], SystemExit, 0,
                                               "NA17_2 to NA17_5 upgrade tefst")

    def test_parse_command_line_show_labs_help(self):
        with self.assertRaises(SystemExit):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', 'show-labs', '-h'], SystemExit, 0,
                                               "Shows labs in lab state service")

    def test_parse_command_line_show_labs_help2(self):
        with self.assertRaises(SystemExit):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', 'show-labs', '--help'], SystemExit, 0,
                                               "Shows labs in lab state service")

    def test_parse_command_line_show_labs_with_lab_name_no_value(self):
        with self.assertRaises(SystemExit):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', 'show-labs', '--lab-name'], SystemExit, 2,
                                               "argument -lab/--lab-name: expected one argument")

    def test_parse_command_line_show_labs_with_lab_name_non_existent_lab(self):
        with HTTMock(self.mock_api_labs_NOK_lab_not_found):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-url', url, 'show-labs',
                                                '--lab-name', 'NOT_EXIST_LAB_NAME'], SystemExit, 0,
                                               "LAB: .* does not exist")


    def test_parse_command_line_request_lab_with_help(self):
        with self.assertRaises(SystemExit):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', 'request-lab', '-h'], SystemExit, 0,
                                               "Allocates lab from lab state service")

    def test_parse_command_line_request_lab_without_query(self):
        with self.assertRaises(SystemExit):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', 'request-lab'], SystemExit, 2,
                                               "error: argument -q/--state-search-query is required")

    def test_parse_command_line_request_lab_with_no_query(self):
        with self.assertRaises(SystemExit):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', 'request-lab', '-q'], SystemExit, 2,
                                               "error: argument -q/--state-search-query: expected one argument")

    def test_parse_command_line_request_lab_without_message(self):
        with self.assertRaises(SystemExit):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', 'request-lab',
                                                '-q', '{\"build.id\":\"NetAct17.2\"}'], SystemExit, 2,
                                               "error: argument -m/--message is required")

    def test_parse_command_line_request_lab_with_no_message(self):
        with self.assertRaises(SystemExit):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', 'request-lab',
                                                '-q', '{\"build.id\":\"NetAct17.2\"}', '-m'], SystemExit, 2,
                                               "error: argument -m/--message: expected one argument")

    def test_parse_command_line_request_lab_OK_lab_available_in_4_secs(self):
        with HTTMock(self.mock_api_request_lab_OK_lab_allocated):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-url', url, 'request-lab',
                                                '-q', '{\"build.id\":\"NetAct17.2\"}',
                                                '-m', 'Unit test request, allocation ', '-wait', '4'], SystemExit, 0,
                                               "LAB: CloudLab655")

    def test_parse_command_line_request_lab_OK_lab_allocated_with_lab_search_query(self):
        with HTTMock(self.mock_api_request_lab_OK_lab_allocated_with_lab_search_query):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-url', url, 'request-lab',
                                                '-q', '{\"build.id\":\"NetAct17.2\"}', '-lq', '{\"lab_type\":\"cloud\"}',
                                                '-m', 'Unit test request, allocation ', '-wait', '4'], SystemExit, 0,
                                               "LAB: CloudLab655")

    def test_parse_command_line_request_lab_OK_no_lab_available_in_2_secs(self):
        with HTTMock(self.mock_api_request_lab_OK_no_lab_available):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-url', url, 'request-lab',
                                                '-q', '{\"build.id\":\"NetAct17.2\"}',
                                                '-m', 'Unit test request, allocation ', '-wait', '2'], SystemExit, 0,
                                               "LAB: <none>.*Exit code: '1'")

    def test_parse_command_line_request_lab_NOK_lab_available_snapshot_failed(self):
        with HTTMock(self.mock_api_request_lab_NOK_lab_allocated_snapshot_failed):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-url', url, 'request-lab',
                                                '-q', '{\"build.id\":\"NetAct17.2\"}',
                                                '-m', 'Unit test request, allocation ', '-wait', '4'], SystemExit, 0,
                                               "LAB: CloudLab655.*reverting snapshot failed.*Exit code: '1'")

    def test_parse_command_line_request_lab_NOK_invalid_query(self):
        with HTTMock(self.mock_api_request_lab_NOK_invalid_query):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-url', url, 'request-lab',
                                                '-q', '{\"build.id\":\"NetAct17.2\"',
                                                '-m', 'Unit test request, allocation ', '-wait', '2'], SystemExit, 0,
                                               "LAB: <none>.*check query.*Exit code: '1'")

    def test_parse_command_line_request_lab_NOK_timeout_no_lab_available(self):
        with HTTMock(self.mock_api_request_lab_NOK_timeout_no_lab_available):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-url', url, 'request-lab',
                                                '-q', '{\"build.id\":\"NetAct17.2\"}',
                                                '-m', 'Unit test request, allocation ', '-wait', '2'], SystemExit, 0,
                                               "LAB: <none>.*'no_lab_available.*Exit code: '1'")

    def test_parse_command_line_release_lab_NOK_no_lab_available(self):
        with HTTMock(self.mock_api_release_lab_NOK_lab_not_found):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-url', url, 'release-lab',
                                                '-lab', 'LAB_NAME_NOT_EXISTS'], SystemExit, 0,
                                               "### ERROR: 'LAB_NAME_NOT_EXISTS' does not exist!.*Exit code: '1'")

    def test_parse_command_line_release_lab_NOK_lab_is_not_reserved(self):
        with HTTMock(self.mock_api_release_lab_NOK_lab_is_not_reserved):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-url', url, 'release-lab',
                                                '-lab', 'CloudLab133'], SystemExit, 0,
                                               "### ERROR: 'CloudLab133' is not currently reserved!.*Exit code: '1'")

    def test_parse_command_line_release_lab_NOK_lab_is_not_reserved_2(self):
        with HTTMock(self.mock_api_release_lab_NOK_lab_is_not_reserved_2):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-url', url, 'release-lab',
                                                '-lab', 'CloudLab133'], SystemExit, 0,
                                               "### ERROR: 'CloudLab133' is not currently reserved!")

    def test_parse_command_line_release_lab_NOK_lab_reserved_by_another_user(self):
        with HTTMock(self.mock_api_release_lab_NOK_reserved_by_another_user):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-url', url, 'release-lab',
                                                '-lab', 'CloudLab1640'], SystemExit, 0,
                                               "### ERROR: 'CloudLab1640' is currently reserved by another user: 'root'!")

    def test_parse_command_line_release_lab_NOK_server_precondition_failure(self):
        with HTTMock(self.mock_api_release_lab_NOK_server_precondition_failure):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-url', url, 'release-lab',
                                                '-lab', 'CloudLab1640'], SystemExit, 0,
                                               "ERROR: Precondition failure in removing 'reservations.*Exit code: '1'")

    def test_parse_command_line_release_lab_server_precondition_ignored(self):
        # Mock checking for query arg '?force'
        with HTTMock(self.mock_api_release_lab_server_precondition_ignored):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-url', url, 'release-lab', '-f',
                                                '-lab', 'CloudLab1640'], SystemExit, 0,
                                               "Released lab: 'CloudLab1640' \(.*\) Exit code: '0")

    def test_parse_command_line_release_lab_OK(self):
        with HTTMock(self.mock_api_release_lab_OK):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-url', url, 'release-lab',
                                                '-lab', 'CloudLab1640'], SystemExit, 0,
                                               "Released lab: 'CloudLab1640'")

    def test_parse_command_line_preserve_state_NOK_illegal_wait_time_o(self):
        with HTTMock(self.mock_api_release_lab_OK):
            with self.assertRaises(SystemExit):
                self._command_line_operation_check(inspect.stack()[0][3],
                                                   ['--username', 'tester', '-url', url, 'preserve-state',
                                                    '-lab', 'CloudLab1640', '--wait-time', 'o'], SystemExit, 2,
                                                   "invalid check_wait_time value: 'o'")

    def test_parse_command_line_preserve_state_NOK_illegal_wait_time_567r(self):
        with HTTMock(self.mock_api_release_lab_OK):
            with self.assertRaises(SystemExit):
                self._command_line_operation_check(inspect.stack()[0][3],
                                                   ['--username', 'tester', '-url', url, 'preserve-state',
                                                    '-lab', 'CloudLab1640', '--wait-time', '567r'], SystemExit, 2,
                                                   "invalid check_wait_time value: '567r'")

    def test_parse_command_line_preserve_state_NOK_illegal_wait_time_zero(self):
        with HTTMock(self.mock_api_release_lab_OK):
            with self.assertRaises(SystemExit):
                self._command_line_operation_check(inspect.stack()[0][3],
                                                   ['--username', 'tester', '-url', url, 'preserve-state',
                                                    '-lab', 'CloudLab1640', '--wait-time', '0'], SystemExit, 2,
                                                   "'--wait-time' value '0' out of range")

    def test_parse_command_line_preserve_state_NOK_previously_reverted_state_missing(self):
        with HTTMock(self.mock_api_release_lab_OK):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-url', url, 'preserve-state',
                                                '-lab', 'CloudLab1640', '--wait-time', '1'], SystemExit, 0,
                                               "### ERROR: 'Previously reverted state' is missing")

    def test_parse_command_line_preserve_state_NOK_lab_reserved_by_another_user(self):
        with HTTMock(self.mock_api_preserve_state_NOK_lab_reserved_by_another_user):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-url', url, 'preserve-state',
                                                '-lab', 'CloudLab1640', '--wait-time', '1'], SystemExit, 0,
                                               "### ERROR: 'CloudLab1640' is currently reserved by another user: 'another_tester'! Exit code: '1'")

    def test_parse_command_line_preserve_state_NOK_snapshot_status_error(self):
        with HTTMock(self.mock_api_preserve_state_NOK_snapshot_status_error):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-url', url, 'preserve-state',
                                                '-lab', 'CloudLab1640', '--wait-time', '4',
                                                '--set-attribute', 'build.id=netact/product/99.17.03.0.335572'], SystemExit, 0,
                                               "Snapshot error.*Exit code: '1'")

    def test_parse_command_line_preserve_state_NOK_exception_error(self):
        with self.assertRaises(ValueError):
            with HTTMock(self.mock_api_preserve_state_NOK_snapshot_status_error):
                self._command_line_operation_check(inspect.stack()[0][3],
                                                   ['--username', 'tester', '-url', url, 'preserve-state',
                                                    '-lab', 'CloudLab1640', '--wait-time', '4',
                                                    '--set-attribute', 'build.id:netact/product/99.17.03.0.335572'], SystemExit, 0,
                                                   "dictionary update sequence element.*Exit code: '1'")

    def test_parse_command_line_preserve_state_OK_set_attribute(self):
        with HTTMock(self.mock_api_preserve_state_OK):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-url', url, 'preserve-state',
                                                '-lab', 'CloudLab1640', '--wait-time', '4',
                                                '--set-attribute', 'build.id=netact/product/99.17.03.0.335572'], SystemExit, 0,
                                               "Snapshot taken from lab: 'CloudLab1640'.*Exit code: '0'")

    def test_parse_command_line_preserve_state_OK_append_attribute_trigger_and_exit(self):
        with HTTMock(self.mock_api_preserve_state_OK):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-url', url, 'preserve-state',
                                                '-lab', 'CloudLab1640', '--wait-time', '4',
                                                '--append-to-list', 'integrated_nes=[MRBTS-223]', '-t'], SystemExit, 0,
                                               "Snapshot operation has been triggered in lab:.*Exit code: '0'")

    def test_parse_command_line_preserve_state_OK_delete_attribute(self):
        with HTTMock(self.mock_api_preserve_state_OK):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-url', url, 'preserve-state',
                                                '-lab', 'CloudLab1640', '--wait-time', '4',
                                                '--delete-attribute', 'build.id'], SystemExit, 0,
                                               "Snapshot taken from lab: 'CloudLab1640'")

    def test_parse_command_line_show_item_OK_lab(self):
        with HTTMock(self.mock_api_labs_OK):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-url', url, 'show-item',
                                                'labs/58d8c8401df07900010ddd7c'], SystemExit, 0,
                                               "\"_id\": \"58d8c8401df07900010ddd7c\"")

    def test_parse_command_line_show_item_NOK_lab(self):
        with self.assertRaises(exceptions.HTTPError):
            with HTTMock(self.mock_api_error_404):
                self._command_line_operation_check(inspect.stack()[0][3],
                                                   ['--username', 'tester', '-url', url, 'show-item',
                                                    'labs/58d8c8401df07900010ddd7'], SystemExit, 0,
                                                   "404 Client Error: None for url")

    def test_parse_command_line_show_schema_OK(self):
        with HTTMock(self.mock_api_show_schema_OK):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-url', url, 'show-schema'], SystemExit, 0,
                                               "\"labs\": {\"status\":")

    def test_parse_command_line_show_schema_OK_labs_only(self):
        with HTTMock(self.mock_api_show_schema_OK):
            outfile = "testfile_labs_only.txt"
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-f', outfile, '-url', url, 'show-schema', '-i', 'labs'], SystemExit, 0,
                                               "\"labs\": {\"status\":", "", outfile)
            os.remove(outfile)

    def test_parse_command_line_show_schema_NOK_not_supported_item_name(self):
        with self.assertRaises(SystemExit):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-url', url, 'show-schema', '-i', 'not_supported'], SystemExit, 2,
                                               "-i/--schema_item: invalid choice: 'not_supported'")

    def test_parse_command_line_show_schema_NOK(self):
        with self.assertRaises(exceptions.HTTPError):
            with HTTMock(self.mock_api_error_404):
                self._command_line_operation_check(inspect.stack()[0][3],
                                                   ['--username', 'tester', '-url', url, 'show-item',
                                                    'labs/58d8c8401df07900010ddd7'], SystemExit, 0,
                                                   "404 Client Error: None for url")

    def test_http_errors_for_request_lab(self):
        with self.assertRaises(exceptions.HTTPError):
            with HTTMock(self.mock_api_error_401):
                self._command_line_operation_check(inspect.stack()[0][3],
                                                   ['--username', 'tester', '-url', url, 'request-lab',
                                                    '-q', '{\"build.id\":\"NetAct17.2\"}',
                                                    '-m', 'Unit test request, allocation ', '-wait', '4'], SystemExit, 0,
                                                   "401 Client Error")

        with self.assertRaises(exceptions.HTTPError):
            with HTTMock(self.mock_api_error_500):
                self._command_line_operation_check(inspect.stack()[0][3],
                                                   ['--username', 'tester', '-url', url, 'request-lab',
                                                    '-q', '{\"build.id\":\"NetAct17.2\"}', '-m', 'Unit test request, allocation ', '-wait', '4'], SystemExit, 0,
                                                   "401 Client Error")

        with self.assertRaises(exceptions.HTTPError):
            with HTTMock(self.mock_api_error_404):
                self._command_line_operation_check(inspect.stack()[0][3],
                                                   ['--username', 'tester', '-url', url, 'request-lab',
                                                    '-q', '{\"build.id\":\"NetAct17.2\"}',
                                                    '-m', 'Unit test request, allocation ', '-wait', '4'], SystemExit, 0,
                                                   "401 Client Error")

    def test_http_errors_for_release_lab(self):
        with self.assertRaises(exceptions.HTTPError):
            with HTTMock(self.mock_api_error_401):
                self._command_line_operation_check(inspect.stack()[0][3],
                                                   ['--username', 'tester', '-url', url, 'release-lab',
                                                    '-lab', 'CloudLab1640'], SystemExit, 0,
                                                   "401 Client Error")

        with self.assertRaises(exceptions.HTTPError):
            with HTTMock(self.mock_api_error_500):
                self._command_line_operation_check(inspect.stack()[0][3],
                                                   ['--username', 'tester', '-url', url, 'release-lab',
                                                    '-lab', 'CloudLab1640'], SystemExit, 0,
                                                   "401 Client Error")

        with self.assertRaises(exceptions.HTTPError):
            with HTTMock(self.mock_api_error_401):
                self._command_line_operation_check(inspect.stack()[0][3],
                                                   ['--username', 'tester', '-url', url, 'release-lab',
                                                    '-lab', 'CloudLab1640'], SystemExit, 0,
                                                   "401 Client Error")

    def test_http_errors_for_show_labs(self):
        with self.assertRaises(exceptions.HTTPError):
            with HTTMock(self.mock_api_error_401):
                self._command_line_operation_check(inspect.stack()[0][3],
                                                   ['--username', 'tester', '-url', url, 'show-labs'], SystemExit, 0,
                                                   "401 Client Error")

        with self.assertRaises(exceptions.HTTPError):
            with HTTMock(self.mock_api_error_500):
                self._command_line_operation_check(inspect.stack()[0][3],
                                                   ['--username', 'tester', '-url', url, 'show-labs',
                                                    '-lab', 'CloudLab1640'], SystemExit, 0,
                                                   "500 Server Error")

        with self.assertRaises(exceptions.HTTPError):
            with HTTMock(self.mock_api_error_404):
                self._command_line_operation_check(inspect.stack()[0][3],
                                                   ['--username', 'tester', '-url', url, 'show-labs',
                                                    '-lab', 'CloudLab1640'], SystemExit, 0,
                                                   "404 Client Error")

        with self.assertRaises(exceptions.HTTPError):
            with HTTMock(self.mock_api_error_404):
                outfile = "testfile_error.txt"
                self._command_line_operation_check(inspect.stack()[0][3],
                                                   ['--username', 'tester', '-f', outfile, '-url', url, 'show-labs',
                                                    '-lab', 'CloudLab1640'], SystemExit, 0,
                                                   "404 Client Error", None, outfile)
                os.remove(outfile)

    def test_http_errors_for_admin_patch_item(self):
        with self.assertRaises(exceptions.HTTPError):
            with HTTMock(self.mock_api_error_401):
                self._command_line_operation_check(inspect.stack()[0][3],
                                                   ['--username', 'admin', '-url', url, 'admin-patch-item',
                                                   'labs/5979c6b5e0a14a0001e20e9c', 'status=initializing'], SystemExit, 0,
                                                   "401 Client Error")

        with self.assertRaises(exceptions.HTTPError):
            with HTTMock(self.mock_api_error_500):
                self._command_line_operation_check(inspect.stack()[0][3],
                                                   ['--username', 'admin', '-url', url, 'admin-patch-item',
                                                   'labs/5979c6b5e0a14a0001e20e9c', 'status=initializing'], SystemExit, 0,
                                                   "500 Server Error")

        with self.assertRaises(exceptions.HTTPError):
            with HTTMock(self.mock_api_error_500):
                outfile = "testfile_error_500.txt"
                self._command_line_operation_check(inspect.stack()[0][3],
                                                   ['--username', 'admin', '-f', outfile, '-url', url, 'admin-patch-item',
                                                   'labs/5979c6b5e0a14a0001e20e9c', 'status=initializing'], SystemExit, 0,
                                                   "500 Server Error", None, outfile)
                os.remove(outfile)

    def test_error_Missing_Schema_error_for_admin_patch_item(self):
        with self.assertRaises(exceptions.MissingSchema):
            with HTTMock(self.mock_api_admin_patch_item_OK_csv_one_parameter):
                outfile = "testfile_error_admin_patch_item.txt"
                self._command_line_operation_check(inspect.stack()[0][3],
                                                   ['--username', 'admin', '-f', outfile, '-url','' , 'admin-patch-item',
                                                    'labs/5979c6b5e0a14a0001e20e9c', 'status=initializing'], SystemExit, 0,
                                                   "ERROR: 'Invalid URL.*/labs/5979c6", None, outfile)
                os.remove(outfile)

    def test_error_Missing_Schema_error_for_create_test_snapshots(self):
        with self.assertRaises(exceptions.InvalidSchema):
            with HTTMock(self.mock_api_admin_patch_item_OK_csv_one_parameter):
                self._command_line_operation_check(inspect.stack()[0][3],
                                                   ['--username', 'admin', '-url','' , 'create-test-snapshots', '-lab', 'mylab'], SystemExit, 0,
                                                   "### ERROR: 'No connection adapters were found for", None)

    def test_error_Missing_Schema_error_for_admin_show_schema(self):
        with self.assertRaises(exceptions.MissingSchema):
            with HTTMock(self.mock_api_admin_patch_item_OK_csv_one_parameter):
                outfile = "testfile_error_show_schema.txt"
                self._command_line_operation_check(inspect.stack()[0][3],
                                                   ['--username', 'admin', '-f', outfile, '-url', '', 'show-schema'], SystemExit, 0,
                                                   "ERROR: 'Invalid URL.*schema.*pretty", None, outfile)
                os.remove(outfile)

    def test_error_Missing_Schema_error_for_admin_admin_add_lab(self):
        with self.assertRaises(exceptions.InvalidSchema):
            with HTTMock(self.mock_api_admin_patch_item_OK_csv_one_parameter):
                outfile = "testfile_error_release_lab.txt"
                self._command_line_operation_check(inspect.stack()[0][3],
                                                   ['--username', 'admin', '-f', outfile, '-url', '', 'admin-add-lab',
                                                    '-lab', 'mylab'], SystemExit, 0,
                                                   "ERROR:.*connection adapters were found.*labs.*where.*Exit code: '1'", None, outfile)
                os.remove(outfile)

    def test_error_Missing_Schema_error_for_admin_admin_remove_labs(self):
        with self.assertRaises(exceptions.InvalidSchema):
            with HTTMock(self.mock_api_admin_patch_item_OK_csv_one_parameter):
                self.orig_stdin = sys.stdin
                sys.stdin = StringIO('Y')
                outfile = "testfile_error_remove_lab.txt"
                self._command_line_operation_check(inspect.stack()[0][3],
                                                   ['--username', 'admin', '-f', outfile, '-url', '', 'admin-remove-labs',
                                                    '-lab', 'mylab'], SystemExit, 0,
                                                   "ERROR:.*connection adapters were found.*labs.*where.*Exit code: '1'", None, outfile)
                os.remove(outfile)

    def test_error_Missing_Schema_error_for_release_lab(self):
        with self.assertRaises(exceptions.InvalidSchema):
            with HTTMock(self.mock_api_admin_patch_item_OK_csv_one_parameter):
                outfile = "testfile_error_release_lab.txt"
                self._command_line_operation_check(inspect.stack()[0][3],
                                                   ['--username', 'admin', '-f', outfile, '-url', '', 'release-lab',
                                                    '-lab', 'mylab'], SystemExit, 0,
                                                   "ERROR:.*connection adapters were found.*labs.*where.*Exit code: '1'", None, outfile)
                os.remove(outfile)

    def test_error_Missing_Schema_error_for_admin_migrate_snapshots(self):
        with HTTMock(self.mock_api_admin_patch_item_OK_csv_one_parameter):
            outfile = "testfile_error_admin_migrate_snapshots.txt"
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-f', outfile, '-url', '', 'admin-migrate-snapshots',
                                                '-labs', 'mylab'], SystemExit, 0,
                                               "ERROR:.*connection adapters were found.*labs.*where.*Exit code: '1'", None, outfile)
            os.remove(outfile)

    def test_lab_request_timeout_during_reservation(self):
        url = 'http://fakelss/rest/api/v2'
        with HTTMock(self.mock_api_request_lab_NOK_timeout_triggers):
            self._command_line_operation_check(inspect.stack()[0][3],
                                                    ["--username", "tester", "-url", url, "request-lab", "-m", "test",
                                                     "-q", "\"{\"build.id\":\"netact/product/99.17.03.0.303\"}\"", "--wait", "2", "--revert-time", "400"],
                                                     SystemExit, 0, "LAB: .*  ### ERROR in 'request-lab' operation, timeout '2' secs expired: '.*' Exit code: '1'")

    def test_lab_request_timeout_snapshot_not_working(self):
        ''' test_lab_request_timeout_snapshot_not_working: reverting snapshot ends with timeout '''
        url = 'http://fakelss/rest/api/v2'
        with HTTMock(self.mock_api_request_lab_NOK_timeout_triggers):
            self._command_line_operation_check(inspect.stack()[0][3],
                                                    ["--username", "tester", "-url", url, "request-lab", "-m", "test",
                                                     "-q", "\"{\"build.id\":\"netact/product/99.17.03.0.303\"}\"", "--wait", "4", "-rt", "4"],
                                                     SystemExit, 0, "LAB: .*  ### ERROR in 'request-lab' operation, timeout '4' secs expired: '.*' Exit code: '1'")

    def test_lab_request_timeout_zero_lab_reserved(self):
        url = 'http://fakelss/rest/api/v2'
        with HTTMock(self.mock_request_for_free_lab):
            self._command_line_operation_check(inspect.stack()[0][3],
                                                    ["--username", "tester", '-l', 'DEBUG', "-url", url, "request-lab", "-m", "test",
                                                     "-q", "\"{\"build.id\":\"netact/product/99.17.03.0.303\"}\"", "--wait", "0", '--revert-time', "14"],
                                                     SystemExit, 0, 
                                                    "LAB: vOSP0020  Exit code: '0'")

    def test_request_lab_wait_for_free_success(self):
        ''' test_request_lab_wait_for_free_success: lab matching the request is reserved at first, but then released. Thus, lab requests succeeds. '''
        self.exec_test_request_lab_wait_for_free()

    def test_request_lab_wait_for_free_timeout_during_reservation(self):
        ''' test_request_lab_wait_for_free_timeout_during_reservation: lab matching the request is reserved lab request fails due to timeout. '''
        self.exec_test_request_lab_wait_for_free(timeout_for_reservation=2, 
            expected_message = "LAB: <none>  ### ERROR in 'request-lab' operation, timeout '2' secs expired",
            exit_code = 1)

    def test_request_lab_wait_for_free_timeout_during_revert(self):
        ''' test_request_lab_wait_for_free_timeout_during_revert: lab matching the request is reserved lab request fails due to timeout. '''
        self.exec_test_request_lab_wait_for_free(timeout_for_revert = 3, 
            expected_message = "LAB: vOSP0020  ### ERROR in 'request-lab' operation, timeout '3' secs expired: '.*revert.*' Exit code: '1'",
            exit_code = 1)

    def test_request_lab_wait_for_free_fails_with_wait_zero(self):
        ''' test_request_lab_wait_for_free_fails_with_wait_zero: lab matching the request is reserved at first, but then released. Lab request fails. '''
        self.exec_test_request_lab_wait_for_free(timeout_for_reservation=0, exit_code = 1, 
            expected_message = "LAB: <none>  ### ERROR in 'request-lab' operation, timeout '0' secs expired: 'no_lab_available' Exit code: '1'")

    def exec_test_request_lab_wait_for_free(self, 
                                timeout_for_reservation=9, timeout_for_revert = None, 
                                exit_code = 0,
                                expected_message = "LAB: vOSP0020  Exit code: '0'"):
        url = 'http://fakelss/rest/api/v2'
        cmd= ["--username", "tester", '-l', 'DEBUG', "-url", url, "request-lab", "-m", "reserved_lab",
             "-q", "\"{\"build.id\":\"netact/product/99.17.03.0.303\"}\"", "--wait", str(timeout_for_reservation)]
        if timeout_for_revert is not None:
            cmd += ["-rt" , str(timeout_for_revert)]
        log.debug('CMD: %s' % (cmd))
        with HTTMock(self.mock_request_lab_wait_for_free_success):
            self._command_line_operation_check(inspect.stack()[0][3],
                                                cmd,
                                                 SystemExit, 0, 
                                                expected_message)

    def test_parse_command_line_admin_migrate_snapshots_OK_lab_does_not_exist(self):
        with HTTMock(self.mock_api_admin_migrate_snapshots_OK):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, '-dca-url', url, 'admin-migrate-snapshots',
                                                '-lab', 'sprintlab283'], SystemExit, 0,
                                               "NetAct16_5_P8_vSphere_Updated_NE_S/W_updated_vSpehereLicenseInstalled ")

    def test_parse_command_line_admin_migrate_snapshots_OK_lab_does_not_exist_with_admin_server_access_params(self):
        with HTTMock(self.mock_api_admin_migrate_snapshots_OK_with_admin_server_access_params):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, '-dca-url', url, 'admin-migrate-snapshots',
                                                '-lab', 'sprintlab283', '-user', 'mytestuser'], SystemExit, 0,
                                               "NetAct16_5_P8_vSphere_Updated_NE_S/W_updated_vSpehereLicenseInstalled ")

    def test_parse_command_line_admin_migrate_snapshots_OK_lab_exists_and_snapshots_exists(self):
        with HTTMock(self.mock_api_admin_migrate_snapshots_OK_lab_exists_and_snapshots_exist):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, '-dca-url', url, 'admin-migrate-snapshots',
                                                '-lab', 'CLAB283'], SystemExit, 0,
                                               "NetAct16_5_P8_vSphere_Updated_NE_S/W_updated_vSpehereLicenseInstalled ")

    def test_parse_command_line_admin_migrate_snapshots_OK_additional_snapshots_exist(self):
        with HTTMock(self.mock_api_admin_migrate_snapshots_OK_additional_snapshots_exist):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, '-dca-url', url, 'admin-migrate-snapshots',
                                                '-lab', 'sprintlab283'], SystemExit, 0,
                                               "SprintLab283-1483597803_addit.*REMOVED")

    def test_parse_command_line_admin_migrate_snapshots_OK_additional_snapshots_exist_with_null_snap_id(self):
        with HTTMock(self.mock_api_admin_migrate_snapshots_OK_additional_snapshots_exist_with_null_snap_id):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, '-dca-url', url, 'admin-migrate-snapshots',
                                                '-lab', 'sprintlab283'], SystemExit, 0,
                                               "SprintLab283-1483597803_addit.*REMOVED.*NetAct_17.2_P8.*REMOVED")

    def test_parse_command_line_admin_migrate_snapshots_NOK_additional_snapshots_remove_failure_404(self):
        with HTTMock(self.mock_api_admin_migrate_snapshots_NOK_additional_snapshots_remove_failure_404):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, '-dca-url', url, 'admin-migrate-snapshots',
                                                '-lab', 'sprintlab283'], SystemExit, 0,
                                               "ERROR.*Unable to delete snapshot: snapshot_id:.*97803_additional' err_msg: '404 Client Error: ")

    def test_parse_command_line_admin_migrate_snapshots_NOK_additional_snapshots_remove_failure_422(self):
        with HTTMock(self.mock_api_admin_migrate_snapshots_NOK_additional_snapshots_remove_failure_422):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, '-dca-url', url, 'admin-migrate-snapshots',
                                                '-lab', 'sprintlab283'], SystemExit, 0,
                                               "ERROR: '422 Client Error:")

    def test_parse_command_line_admin_migrate_snapshots_NOK_lab_exists_but_name_syntax_not_valid_in_dca(self):
        with HTTMock(self.mock_api_admin_migrate_snapshots_NOK_lab_exists_but_name_syntax_not_valid_in_dca):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, '-dca-url', url, 'admin-migrate-snapshots',
                                                '-lab', 'vsprintlab283'], SystemExit, 0,
                                               "ERROR: Lab name syntax not supported in DCA for 'vsprintlab'.")

    def test_parse_command_line_admin_migrate_snapshots_NOK_not_admin_user(self):
        self._command_line_operation_check(inspect.stack()[0][3],
                                           ['--username', 'testuser', '-url', url, '-dca-url', url, 'admin-migrate-snapshots',
                                            '-lab', 'vsprintlab283'], SystemExit, 0,
                                           "ERROR: User 'testuser' is not allowed to do the operation!")

    def test_parse_command_line_admin_remove_labs_OK_one_lab(self):
        with HTTMock(self.mock_api_admin_remove_labs_OK_one_lab):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-remove-labs',
                                                '-labs', 'vSprint7801', '-f'], SystemExit, 0,
                                               ".*vSprint7801.*REMOVED", "Exit code: '1'")

    def test_parse_command_line_admin_remove_labs_OK_one_lab_no_states(self):
        with HTTMock(self.mock_api_admin_remove_labs_OK_one_lab_no_states):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-remove-labs',
                                                '-labs', 'vSprint7801', '-f'], SystemExit, 0,
                                               ".*vSprint7801.*REMOVED", "Exit code: '1'")

    def test_parse_command_line_admin_remove_labs_OK_several_labs_all_OK(self):
        with HTTMock(self.mock_api_admin_remove_labs_OK_several_labs_all_OK):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-remove-labs',
                                                '-labs', 'vSprint9163,CloudLab7677', '-f'], SystemExit, 0,
                                               "vSprint9163.*REMOVED.*CloudLab7677.*REMOVED.*Exit code: '0'")

    def test_parse_command_line_admin_remove_labs_NOK_one_lab_one_NOK(self):
        with HTTMock(self.mock_api_admin_remove_labs_NOK_one_lab_one_NOK):
            self.orig_stdin = sys.stdin
            sys.stdin = StringIO('Y')
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-remove-labs',
                                               '-labs', 'SprintLab6080'], SystemExit, 0,
                                               "remove lab.*from Lab State Service.*admin-remove-lab.*SprintLab6080.*### ERROR: '500 Server Error: None for url.*Exit code: '1'")
            sys.stdin = self.orig_stdin

    def test_parse_command_line_admin_remove_labs_NOK_several_labs_one_NOK(self):
        with HTTMock(self.mock_api_admin_remove_labs_NOK_several_labs_one_NOK):
            self.orig_stdin = sys.stdin
            sys.stdin = StringIO('Y')
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-remove-labs',
                                               '-labs', 'SprintLab6080,CloudLab9879,CloudLab8610,CloudLab5336'], SystemExit, 0,
                                               "CloudLab9879.*REMOVED.*CloudLab8610.*ERROR.*Lab is currently reserved by 'testuser'.*CloudLab5336.*REMOVED.*Exit code: '1'")
            sys.stdin = self.orig_stdin

    def test_parse_command_line_admin_remove_labs_NOK_several_labs_all_NOK(self):
        with HTTMock(self.mock_api_admin_remove_labs_NOK_several_labs_all_NOK):
            self.orig_stdin = sys.stdin
            sys.stdin = StringIO('Y')
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-remove-labs',
                                                '-labs', 'CloudLab8610,vSprint1429,vSprint8526'], SystemExit, 0,
                                               "CloudLab8610.*ERROR.*Lab is currently reserved by 'testuser.*vSprint1429.*ERROR.*Lab is currently reserved by 'testuser'!.*vSprint8526.*ERROR.*Lab is currently reserved by 'testuser'!.*Exit code: '1'")
            sys.stdin = self.orig_stdin

    def test_parse_command_line_admin_remove_labs_NOK_confirmation_no(self):
        with HTTMock(self.mock_api_admin_remove_labs_NOK_several_labs_all_NOK):
            self.orig_stdin = sys.stdin
            sys.stdin = StringIO('n')
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-remove-labs',
                                                '-labs', 'CloudLab8610,vSprint1429,vSprint8526'], SystemExit, 0,
                                               "Are You sure you want to remove.*from Lab State.*Operation cancelled! Exit code: '1'" )
            sys.stdin = self.orig_stdin


    def test_parse_command_line_admin_remove_labs_NOK_lab_does_not_exist(self):
        with HTTMock(self.mock_api_admin_remove_labs_NOK_lab_does_not_exist):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-remove-labs',
                                                '-labs', 'sprintlab2', '-f'], SystemExit, 0,
                                               "sprintlab2.*ERROR.*Lab does not exist in Lab State Service.*Exit code: '1'")

    def test_parse_command_line_admin_remove_labs_NOK_user_not_allowed_to_remove(self):
        with HTTMock(self.mock_api_admin_remove_labs_NOK_user_not_allowed_to_remove):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-url', url, 'admin-remove-labs',
                                                '-labs', 'sprintlab283', '-f'], SystemExit, 0,
                                               "ERROR.*User 'tester' is not allowed to do the operation.*Exit code: '1'")

    def test_admin_remove_labs_no_force(self):
        self.exec_test_admin_remove_labs()
            
    def test_admin_remove_labs_force(self):
        self.exec_test_admin_remove_labs(force_flag = True)
            
    def exec_test_admin_remove_labs(self,
        confirm_deletion_flag = True, user = 'admin', force_flag = False, 
        expected_retval = 0,
        delete_should_be_called = True
    ):
        lab_id = 'L000007'
        lab_etag = 'v000007V1'

        with \
            mock.patch('client.admin._confirmation_for_deletion', return_value = confirm_deletion_flag) as confirm_deletion,\
            mock.patch('client.rest_client.post_resource', return_value = {'_status':'OK'}) as post_resource,\
            mock.patch('client.rest_client.delete_item') as delete_item,\
            mock.patch('client.rest_client.get_item') as get_item,\
            mock.patch('client.rest_client.get_labs') as get_labs:
            ###confirm_deletion.return_value = confirm_deletion_flag
            get_labs.return_value = [
            {'_items':[
                {
                    '_id' : lab_id, '_etag':lab_etag,
                    'states':[
                        {'snapshot_id':'S1', '_id': 'L0007-A', '_etag':'v000007AV1.1',},
                        {'snapshot_id':'S2', '_id': 'L0007-B', '_etag':'v000007BV1',},
                    ],
                }
            ]}]

            retval = client.admin.admin_remove_labs(['lab007'], force_flag, service_url='http://itsafake/lss', username=user)
            log.info('RETVAL: %s', retval)

            log.info('Calls to client.admin._confirmation_for_deletion: %s' % (confirm_deletion.mock_calls))
            log.info('Calls to client.rest_client.get_labs: %s' % (get_labs.mock_calls))
            log.info('Calls to client.rest_client.post_resource: %s' % (post_resource.mock_calls))
            log.info('Calls to client.rest_client.delete_item: %s' % (delete_item.mock_calls))
            if delete_should_be_called:
                delete_item.assert_called_once_with('labs', lab_id, None, lab_etag, 'http://itsafake/lss', force_flag=force_flag)
            self.assertEqual(retval, expected_retval)

    def test_parse_command_line_admin_add_lab_OK_name_given(self):
        with HTTMock(self.mock_api_admin_add_lab_OK_name_given):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-add-lab',
                                                '-lab', 'sprintlab283'], SystemExit, 0,
                                               "Lab 'sprintlab283'.*'labs/597b1453e0a14a0001e20ed2'.*added into.*Exit code: '0'")

    def test_parse_command_line_admin_add_lab_OK_name_type_given(self):
        with HTTMock(self.mock_api_admin_add_lab_OK_name_type_given):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-add-lab',
                                                '-lab', 'cloudlab283', '-type', 'cloud'], SystemExit, 0,
                                               "Lab 'cloudlab283'.*'labs/597b1453e0a14a0001e20ed2'.*added into.*Exit code: '0'")

    def test_parse_command_line_admin_add_lab_OK_name_type_status_given(self):
        with HTTMock(self.mock_api_admin_add_lab_OK_name_type_status_given):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-add-lab',
                                                '-lab', 'vsp0283', '-type', 'vsprint', '-status', 'initializing'], SystemExit, 0,
                                               "Lab 'vsp0283'.*'labs/597b1453e0a14a0001e20ed2'.*added into.*Exit code: '0'")

    def test_parse_command_line_admin_add_lab_NOK_lab_already_exists(self):
        with HTTMock(self.mock_api_admin_add_lab_NOK_lab_already_exists):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-add-lab',
                                                '-lab', 'sprintlab283'], SystemExit, 0,
                                               "### ERROR: Lab 'sprintlab283'.*_id: 'labs/597b1453e0a14a0001e20ed2'.*already exists in Lab State Service.*Exit code: '1'")

    def test_parse_command_line_admin_add_lab_NOK_invalid_lab_type(self):
        with self.assertRaises(SystemExit):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-add-lab',
                                                '-lab', 'sprintlab283', '-type', 'invalid'], SystemExit, 2,
                                               "-type/--lab-type: invalid choice: 'invalid'.*choose from ")

    def test_parse_command_line_admin_add_lab_NOK_invalid_lab_status(self):
        with self.assertRaises(SystemExit):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-add-lab',
                                                '-lab', 'sprintlab283', '-status', 'invalid initializing'], SystemExit, 2,
                                               "-status/--lab-status: invalid choice: 'invalid initializing'.*choose from")

    def test_parse_command_line_admin_add_lab_NOK_username_not_valid(self):
        with HTTMock(self.mock_api_admin_add_lab_NOK_username_not_valid):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-url', url, 'admin-add-lab',
                                                '-lab', 'sprintlab283'], SystemExit, 0,
                                               "User 'tester' is not allowed to do the operation!Exit code: '1'")

    def test_parse_command_line_create_test_snapshots_OK_one_snapshot(self):
        with HTTMock(self.mock_api_create_snapshots_OK_one_snapshot):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'create-test-snapshots',
                                                '-lab', 'sprintlab283', '-c', '1'], SystemExit, 0,
                                               "netact/product/99.17.03.*OK.*Exit code: '0'")

    def test_parse_command_line_create_test_snapshots_OK_several_snapshots(self):
        with HTTMock(self.mock_api_create_snapshots_OK_several_snapshots):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'create-test-snapshots',
                                                '-lab', 'sprintlab283'], SystemExit, 0,
                                               "netact/product/99.17.03.*OK.*Exit code: '0'")

    def test_parse_command_line_create_test_snapshots_NOK_wrong_username(self):
        with HTTMock(self.mock_api_create_snapshots_NOK_wrong_username):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'root', '-url', url, 'create-test-snapshots',
                                                '-lab', 'sprintlab283'], SystemExit, 0,
                                               "Exit code: '1'")

    def test_parse_command_line_create_test_snapshots_NOK_lab_does_not_exist(self):
        with HTTMock(self.mock_api_create_snapshots_NOK_lab_does_not_exist):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'create-test-snapshots',
                                                '-lab', 'sprintlab283'], SystemExit, 0,
                                               "Lab 'sprintlab283' does not exist!.*Exit code: '1'")

    def test_parse_command_line_create_test_snapshots_NOK_some_snapshots_successful(self):
        with HTTMock(self.mock_api_create_snapshots_NOK_some_snapshots_successful):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'create-test-snapshots',
                                                '-lab', 'sprintlab283'], SystemExit, 0,
                                               "for 'sprintlab283' status: .*ERROR.*ERR.*'lab': 'required field'.*Exit code: '1'")

    def test_parse_command_line_create_test_snapshots_NOK_all_snapshots_failed(self):
        with HTTMock(self.mock_api_create_snapshots_NOK_all_snapshots_failed):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'create-test-snapshots',
                                                '-lab', 'sprintlab283'], SystemExit, 0,
                                               "Exit code: '1'")

    def test_parse_command_line_admin_patch_item_OK_csv_one_parameter(self):
        with HTTMock(self.mock_api_admin_patch_item_OK_csv_one_parameter):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-patch-item',
                                                'labs/5979c6b5e0a14a0001e20e9c', 'status=initializing'], SystemExit, 0,
                                               "'admin-patch-item'.*labs/5979c6b5e0a14a0001e20e9c.*status=initializing.*OK.*Exit code: '0'")

    def test_parse_command_line_admin_patch_item_OK_csv_several_parameters(self):
        with HTTMock(self.mock_api_admin_patch_item_OK_csv_several_parameters):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-patch-item',
                                                'states/5979c6b5e0a14a0001e20e9c', 'status=initializing,lab_name=vCloudLab984'], SystemExit, 0,
                                               "states/5979c6b5e0a14a0001e20e9c.*status=initializing,lab_name=vCloudLab984.*Exit code: '0'")

    def test_parse_command_line_admin_patch_item_OK_json_one_parameter(self):
        with HTTMock(self.mock_api_admin_patch_item_OK_json_one_parameter):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-patch-item',
                                                'labs/5979c6b5e0a14a0001e20e9c', '{"snapshot_status": "available"}'], SystemExit, 0,
                                               "Exit code: '0'")

    def test_parse_command_line_admin_patch_item_OK_json_several_parameters(self):
        with HTTMock(self.mock_api_admin_patch_item_OK_json_several_parameters):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-patch-item',
                                                'labs/5979c6b5e0a14a0001e20e9c', '{"status": "ready", "lab_name": "vCloudLab984"}'], SystemExit, 0,
                                               "Exit code: '0'")

    def test_parse_command_line_admin_patch_item_NOK_wrong_username(self):
        with HTTMock(self.mock_api_admin_patch_item_NOK_wrong_username):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'not_admin', '-url', url, 'admin-patch-item',
                                                'labs/5979c6b5e0a14a0001e20e9c', '"status=initializing"'], SystemExit, 0,
                                               "User 'not_admin' is not allowed to do the operation! Exit code: '1'")

    def test_parse_command_line_admin_patch_item_NOK_item_does_not_exist(self):
        with HTTMock(self.mock_api_admin_patch_item_NOK_item_does_not_exist):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-patch-item',
                                                'labs/5979c6b5e0a14a0001e20e9c', '"status=initializing"'], SystemExit, 0,
                                               "### ERROR: item not found 'labs/5979c6b5e0a14a0001e20e9c' Exit code: '1'")

    def test_parse_command_line_admin_patch_item_NOK_csv_parameter_error(self):
        with HTTMock(self.mock_api_admin_patch_item_NOK_csv_parameter_error):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-patch-item',
                                                'labs/5979c6b5e0a14a0001e20e9c', 'invalid_parameter=initializing'], SystemExit, 0,
                                               "labs/5979c6b5e0a14a0001e20e9c.*invalid_parameter=initializing.*status.*ERR.*'invalid_parameter': 'unknown field'.*Exit code: '1'")

    def test_parse_command_line_admin_patch_item_NOK_json_parameter_error(self):
        with HTTMock(self.mock_api_admin_patch_item_NOK_json_parameter_error):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-patch-item',
                                                'labs/5979c6b5e0a14a0001e20e9c', '{"snapshot_status": "available"'], SystemExit, 0,
                                               "Exit code: '1'")

    def test_parse_command_line_admin_data_backup_OK(self):
        with HTTMock(self.mock_api_admin_data_backup_OK):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-data-backup',
                                                '-lab', 'sprintlab283'], SystemExit, 0,
                                               "data back-up.*Exit code: '0'")

    def test_parse_command_line_admin_data_restore_OK(self):
        self._command_line_operation_check(inspect.stack()[0][3],
                                           ['--username', 'admin', '-url', url, 'admin-data-restore',
                                            '-lab', 'sprintlab283'], SystemExit, 0,
                                           "restore.*Exit code: '0'")

    def test_parse_command_line_admin_reserve_labs_OK_one_lab(self):
        with HTTMock(self.mock_api_admin_reserve_labs_OK_one_lab):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-reserve-labs',
                                                '-labs', 'CloudLab5960'], SystemExit, 0,
                                               "admin-reserve-lab.*CloudLab5960.*RESERVED.*Exit code: '0'")

    def test_parse_command_line_admin_reserve_labs_OK_several_labs(self):
        with HTTMock(self.mock_api_admin_reserve_labs_OK_several_labs):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-reserve-labs',
                                                '-labs', 'CloudLab5960,sprintlab1234,vsp0034'], SystemExit, 0,
                                               "admin-reserve-lab.*CloudLab5960.*RESERVED.*sprintlab1234.*RESERVED.*vsp0034.*RESERVED.*Exit code: '0'")

    def test_parse_command_line_admin_reserve_labs_OK_one_lab_with_force(self):
        with HTTMock(self.mock_api_admin_reserve_labs_OK_one_lab_with_force):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-reserve-labs',
                                                '-labs', 'CloudLab5960', '-f'], SystemExit, 0,
                                               "admin-reserve-lab.*CloudLab5960.*RESERVED.*Exit code: '0'")

    def test_parse_command_line_admin_reserve_labs_OK_several_labs_with_force(self):
        with HTTMock(self.mock_api_admin_reserve_labs_OK_several_labs_with_force):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-reserve-labs',
                                                '-labs', 'CloudLab5960,vsp0044,sprintlab0098', '-f'], SystemExit, 0,
                                               "admin-reserve-lab.*CloudLab5960.*RESERVED.*vsp0044.*RESERVED.*sprintlab0098.*RESERVED.*Exit code: '0'")

    def test_parse_command_line_admin_reserve_labs_OK_one_lab_reserved_by_admin_with_force(self):
        with HTTMock(self.mock_api_admin_reserve_labs_OK_one_lab_reserved_by_admin_with_force):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-reserve-labs',
                                                '-labs', 'CloudLab4960', '-f'], SystemExit, 0,
                                               "admin-reserve-lab.*CloudLab4960.*RESERVED.*Exit code: '0'")

    def test_parse_command_line_admin_reserve_labs_OK_one_lab_reserved_by_other_user_with_force(self):
        with HTTMock(self.mock_api_admin_reserve_labs_OK_one_lab_reserved_by_other_user_with_force):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-reserve-labs',
                                                '-labs', 'CloudLab3960', '-f'], SystemExit, 0,
                                               "admin-reserve-lab.*CloudLab3960.*RESERVED.*Exit code: '0'")

    def test_parse_command_line_admin_reserve_labs_OK_all_labs_reserved_by_other_user_with_force(self):
        with HTTMock(self.mock_api_admin_reserve_labs_OK_all_labs_reserved_by_other_user_with_force):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-reserve-labs',
                                                '-labs', 'CloudLab5960,vsp0044,sprintlab0098', '-f'], SystemExit, 0,
                                               "admin-reserve-lab.*vsp0044.*RESERVED.*sprintlab0098.*RESERV.*Exit code: '0'")

    def test_parse_command_line_admin_reserve_labs_NOK_one_lab(self):
        with HTTMock(self.mock_api_admin_reserve_labs_NOK_one_lab):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-reserve-labs',
                                                '-labs', 'CloudLab5960'], SystemExit, 0,
                                               "admin-reserve-lab.*ERROR: 'CloudLab5960' is currently reserved by another user:.*Exit code: '1'")

    def test_parse_command_line_admin_reserve_labs_NOK_several_labs_one_NOK(self):
        with HTTMock(self.mock_api_admin_reserve_labs_NOK_several_labs_one_NOK):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-reserve-labs',
                                                '-labs', 'CloudLab5960,vsp0044,sprintlab0098'], SystemExit, 0,
                                               "admin-reserve-lab.*ERROR: 'vsp0044' is currently reserved.*sprintlab0098.*RESERV.*Exit code: '1'")

    def test_parse_command_line_admin_reserve_labs_NOK_several_labs_all_NOK(self):
        with HTTMock(self.mock_api_admin_reserve_labs_NOK_several_labs_all_NOK):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-reserve-labs',
                                                '-labs', 'CloudLab5960,vsp0044,sprintlab0098'], SystemExit, 0,
                                               "admin-reserve-lab.*ERROR: 'CloudLab5960' is currently reserved.*ERROR: 'vsp0044' does not exist.*ERROR: 'sprintlab0098' does not exist!.*Exit code: '1'")

    def test_parse_command_line_admin_reserve_labs_NOK_several_labs_one_NOK_with_force(self):
        with HTTMock(self.mock_api_admin_reserve_labs_NOK_several_labs_one_NOK_with_force):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-reserve-labs',
                                                '-labs', 'CloudLab5960,vsp0044,sprintlab0098', '-f'], SystemExit, 0,
                                               "admin-reserve-lab.*CloudLab5960.*RESERVED.*vsp0044.*ERROR: '422 Client Error: None for url.*sprintlab0098.*RESERV.*Exit code: '1'")

    def test_parse_command_line_admin_reserve_labs_NOK_several_labs_all_NOK_with_force(self):
        with HTTMock(self.mock_api_admin_reserve_labs_NOK_several_labs_all_NOK_with_force):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-reserve-labs',
                                                '-labs', 'CloudLab5960,vsp0044,sprintlab0098'], SystemExit, 0,
                                               "admin-reserve-lab.*CloudLab5960.*ERROR: Removing 'reservations/None' failed!.*vsp0044.*ERROR: 'vsp0044' is currently reserved.*sprintlab0098.*### ERROR: Precondition failure in removing 'reservations/None'.*Exit code: '1'")

    def test_parse_command_line_admin_reserve_labs_NOK_lab_does_not_exist(self):
        with HTTMock(self.mock_api_admin_reserve_labs_NOK_lab_does_not_exist):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-reserve-labs',
                                                '-labs', 'CloudLab5960'], SystemExit, 0,
                                               "admin-reserve-lab.*ERROR: 'CloudLab5960' does not exist.*Exit code: '1'")

    def test_parse_command_line_admin_reserve_labs_NOK_user_not_allowed_to_reserve(self):
        with HTTMock(self.mock_api_admin_reserve_labs_NOK_user_not_allowed_to_reserve):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'not_admin_user', '-url', url, 'admin-reserve-labs',
                                                '-labs', 'CloudLab5960'], SystemExit, 0,
                                               "ERROR: User 'not_admin_user' is not allowed to do the operation! Exit code: '1'")

    def test_parse_command_line_admin_reserve_labs_NOK_lab_already_reserved(self):
        with HTTMock(self.mock_api_admin_reserve_labs_NOK_lab_already_reserved):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-reserve-labs',
                                                '-labs', 'CloudLab5960'], SystemExit, 0,
                                               "admin-reserve-lab.*### ERROR: 'CloudLab5960' is currently reserved by another user: 'Pertti Keinonen'.*Exit code: '1'")

    def test_parse_command_line_admin_reserve_labs_NOK_exception(self):
        with HTTMock(self.mock_api_admin_reserve_labs_NOK_exception):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-reserve-labs',
                                                '-labs', 'CloudLab5960'], SystemExit, 0,
                                               "admin-reserve-lab.*### ERROR: '_links'.*Exit code: '1'")

    def test_format_string(self):
        test_str = "test string"
        col = "OK"

        regexp = "30m{}.*0m".format(test_str)
        #        self.assertEqual(col, regexp)
        formatted_str = client._format_string(test_str, col)
        self.assertRegexpMatches(formatted_str, test_str)
        self.assertRegexpMatches(formatted_str, regexp)

        regexp = "1m.*{}.*0m".format(test_str)
        formatted_str = client._format_string(test_str, col, True)
        self.assertIsNotNone(formatted_str)
        self.assertRegexpMatches(formatted_str, regexp)

        regexp = "4m.*{}.*0m".format(test_str)
        formatted_str = client._format_string(test_str, col, True, True)
        self.assertIsNotNone(formatted_str)
        self.assertRegexpMatches(formatted_str, regexp)

    def test_resolve_status_from_response(self):
        response = {u'_status': u'ERR', u'_error': {u'message': u'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.', u'code': 404}}
        status, msg = client.resolve_status_from_response(response)
        self.assertFalse(status)
        self.assertRegexpMatches(msg, "Code:.*URL manually please.*")

    def test_resolve_schema_text(self):
        text = """
    "labs": {
        "status": {
            "default": "queued_for_initialization",
            "type": "string",
            "allowed": [
                "reverting_state",
                "preserving_state",
                "state_operation_failed",
                "queued_for_initialization",
                "queued_for_revert",
                "initializing",
                "ready"
            ]
        },
        "_id": {
            "type": "objectid"
        }
    },
    "states": {
        "lab": {
            "required": true,
            "type": "objectid",
            "data_relation": {
                "field": "_id",
                "resource": "labs",
                "embeddable": true
            }
        },
 """ 
        schema_item = "labs"
        new_schema = client.resolve_schema_text(text, schema_item)
        self.assertRegexpMatches(new_schema, "queued_for_initialization")

    def test_parse_command_line_admin_remove_snapshots_OK_one_snapshot(self):
        with HTTMock(self.mock_api_admin_remove_snapshots_OK_one_snapshot):
            self.orig_stdin = sys.stdin
            sys.stdin = StringIO('Y')
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-remove-snapshots',
                                                '-lab', 'vSprint7489', '-snaps', '113456'], SystemExit, 0,
                                               "remove snapshots.*Lab State Service and DC Storage.*'admin-remove-snapshots' for 'vSprint7489' status.*113456.*REMOVED.*Exit code: '0'")
            sys.stdin = self.orig_stdin

    def test_parse_command_line_admin_remove_snapshots_OK_several_snapshots(self):
        with HTTMock(self.mock_api_admin_remove_snapshots_OK_several_snapshots):
            self.orig_stdin = sys.stdin
            sys.stdin = StringIO('Y')
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-remove-snapshots',
                                                '-lab', 'vSprint7489', '-snaps', '113456,3456,66777'], SystemExit, 0,
                                               "'admin-remove-snapshots' for 'vSprint7489' status.*113456.*REMOVED.*Exit code: '0'")
            sys.stdin = self.orig_stdin

    def test_parse_command_line_admin_remove_snapshots_OK_one_snapshot_with_force(self):
        with HTTMock(self.mock_api_admin_remove_snapshots_OK_one_snapshot_with_force):
            self.orig_stdin = sys.stdin
            sys.stdin = StringIO('n')
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-remove-snapshots',
                                                 '-lab', 'vsp7489', '-snaps', '113456', '-f'], SystemExit, 0,
                                               "'admin-remove-snapshots' for 'vsp7489' status.*113456.*REMOVED.*Exit code: '0'")
            sys.stdin = self.orig_stdin

    def test_parse_command_line_admin_remove_snapshots_OK_several_snapshots_with_force(self):
        with HTTMock(self.mock_api_admin_remove_snapshots_OK_several_snapshots_with_force):
            self.orig_stdin = sys.stdin
            sys.stdin = StringIO('n')
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-remove-snapshots',
                                                '-lab', 'CloudLab5960', '-snaps', '113456,3456,66777', '-f'], SystemExit, 0,
                                               "'admin-remove-snapshots' for 'CloudLab5960' status:.*66777.*REMOVED.*Exit code: '0'")
            sys.stdin = self.orig_stdin

    def test_parse_command_line_admin_remove_snapshots_NOK_empty_snapshot_id(self):
        with HTTMock(self.mock_api_admin_remove_snapshots_OK_one_snapshot):
            self.orig_stdin = sys.stdin
            sys.stdin = StringIO('Y')
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-remove-snapshots',
                                                '-lab', 'CloudLab5960', '-snaps', ''], SystemExit, 0,
                                               "admin-remove-snapshots.*<empty_id>.*### ERROR: Snapshot does not exist in lab!.*Exit code: '1'")
            sys.stdin = self.orig_stdin

    def test_parse_command_line_admin_remove_snapshots_NOK_several_snapshots_one_NOK(self):
        with HTTMock(self.mock_api_admin_remove_snapshots_NOK_several_snapshots_one_NOK):
            self.orig_stdin = sys.stdin
            sys.stdin = StringIO('Y')
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-remove-snapshots',
                                                '-lab', 'CloudLab5960', '-snaps', '113456,3456,56'], SystemExit, 0,
                                               "'admin-remove-snapshots' for 'CloudLab5960' status.*113456.*REMOVED.*3456.*REMOVED.*56.*ERROR.*Snapshot does not exist in lab.*Exit code: '1'")
            sys.stdin = self.orig_stdin

    def test_parse_command_line_admin_remove_snapshots_NOK_several_snapshots_all_NOK(self):
        with HTTMock(self.mock_api_admin_remove_snapshots_NOK_several_snapshots_all_NOK):
            self.orig_stdin = sys.stdin
            sys.stdin = StringIO('Y')
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-remove-snapshots',
                                                '-lab', 'CloudLab5960', '-snaps', '113456,3456,56'], SystemExit, 0,
                                               "'admin-remove-snapshots' for 'CloudLab5960' status.*113456.*ERROR.*3456.*ERROR.*56.*ERROR.*Snapshot does not exist in lab.*Exit code: '1'")
            sys.stdin = self.orig_stdin

    def test_parse_command_line_admin_remove_snapshots_NOK_several_snapshots_one_NOK_with_force(self):
        with HTTMock(self.mock_api_admin_remove_snapshots_NOK_several_snapshots_one_NOK_with_force):
            self.orig_stdin = sys.stdin
            sys.stdin = StringIO('n')
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-remove-snapshots',
                                                '-lab', 'CloudLab5960', '-snaps', '113456,3456,66777', '-f'], SystemExit, 0,
                                               "'admin-remove-snapshots' for 'CloudLab5960' status.*113456.*REMOVED.*3456.*ERROR.*66777.*REMOVED.*Exit code: '1'")
            sys.stdin = self.orig_stdin

    def test_parse_command_line_admin_remove_snapshots_NOK_several_snapshots_all_NOK_with_force(self):
        with HTTMock(self.mock_api_admin_remove_snapshots_NOK_several_snapshots_all_NOK_with_force):
            self.orig_stdin = sys.stdin
            sys.stdin = StringIO('Y')
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-remove-snapshots',
                                                 '-lab', 'CloudLab5960', '-snaps', '113456,3456,56', '-f'], SystemExit, 0,
                                               "'admin-remove-snapshots' for 'CloudLab5960' status.*113456.*ERROR.*3456.*ERROR.*56.*ERROR.*Snapshot does not exist in lab.*Exit code: '1'")
            sys.stdin = self.orig_stdin

    def test_parse_command_line_admin_remove_snapshots_NOK_lab_does_not_exist(self):
        with HTTMock(self.mock_api_admin_remove_snapshots_NOK_lab_does_not_exist):
            self.orig_stdin = sys.stdin
            sys.stdin = StringIO('Y')
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-remove-snapshots',
                                                '-lab', 'CloudLab5960', '-snaps', '567'], SystemExit, 0,
                                               "ERROR: Lab does not exist in Lab State Service!  Exit code: '1'")
            sys.stdin = self.orig_stdin

    def test_parse_command_line_admin_remove_snapshots_NOK_user_not_allowed_to_remove(self):
        with HTTMock(self.mock_api_admin_remove_snapshots_NOK_user_not_allowed_to_remove):
            self.orig_stdin = sys.stdin
            sys.stdin = StringIO('n')
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'not admin user', '-url', url, 'admin-remove-snapshots',
                                                '-lab', 'CloudLab5960', '-snaps', '345'], SystemExit, 0,
                                               "ERROR: User 'not admin user' is not allowed to do the operation!.*Exit code: '1'")
            sys.stdin = self.orig_stdin

    def test_parse_command_line_admin_remove_snapshots_NOK_lab_already_reserved(self):
        with HTTMock(self.mock_api_admin_remove_snapshots_NOK_lab_already_reserved):
            self.orig_stdin = sys.stdin
            sys.stdin = StringIO('Y')
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-remove-snapshots',
                                                '-lab', 'CloudLab5960', '-snaps', '345'], SystemExit, 0,
                                               "ERROR: Lab is currently reserved by 'Pertti Keino.*Exit code: '1'")
            sys.stdin = self.orig_stdin

    def test_parse_command_line_admin_remove_snapshots_NOK_operation_cancelled_in_question(self):
        with HTTMock(self.mock_api_admin_remove_snapshots_NOK_operation_cancelled_in_question):
            self.orig_stdin = sys.stdin
            sys.stdin = StringIO('n')
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'admin-remove-snapshots',
                                                '-lab', 'CloudLab5960', '-snaps', ''], SystemExit, 0,
                                               "Operation cancelled! Exit code: '1'")
            sys.stdin = self.orig_stdin

    def test_parse_command_line_show_admin_server_access_data_ok_no_data_all_labs(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_no_data_all_labs):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'show-admin-server-access-data'], SystemExit, 0,
                                               "ERROR: Labs do not exist in Lab State.*Exit code: '1'")

    def test_parse_command_line_show_admin_server_access_data_ok_no_data_all_labs_ASCII(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_no_data_all_labs):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, '-o', 'ASCII', 'show-admin-server-access-data'], SystemExit, 0,
                                               "ERROR: Labs do not exist in Lab State.*Exit code: '1'")

    def test_parse_command_line_show_admin_server_access_data_ok_no_data_all_labs_CSV(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_no_data_all_labs):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, '-o', 'CSV', 'show-admin-server-access-data'], SystemExit, 0,
                                               "ERROR: Labs do not exist in Lab State.*Exit code: '1'")

    def test_parse_command_line_show_admin_server_access_data_ok_no_data_all_labs_JSON(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_no_data_all_labs):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, '-o', 'JSON', 'show-admin-server-access-data'], SystemExit, 0,
                                               "\"status\": \"Failed\".*ERROR: Labs do not exist in Lab State")

    def test_parse_command_line_show_admin_server_access_data_nok_no_data_one_lab(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_nok_no_data_one_lab):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'show-admin-server-access-data',
                                                '-lab', 'CloudLab6128'], SystemExit, 0,
                                               "ERROR: Lab 'CloudLab6128' does not exist.*Exit code: '1'")

    def test_parse_command_line_show_admin_server_access_data_nok_no_data_one_lab_ASCII(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_nok_no_data_one_lab):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, '-o', 'ASCII', 'show-admin-server-access-data',
                                                '-lab', 'CloudLab6128'], SystemExit, 0,
                                               "ERROR: Lab 'CloudLab6128' does not exist.*Exit code: '1'")

    def test_parse_command_line_show_admin_server_access_data_nok_no_data_one_lab_CSV(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_nok_no_data_one_lab):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, '-o', 'CSV', 'show-admin-server-access-data',
                                                '-lab', 'CloudLab6128'], SystemExit, 0,
                                               "ERROR: Lab 'CloudLab6128' does not exist.*Exit code: '1'")

    def test_parse_command_line_show_admin_server_access_data_nok_no_data_one_lab_JSON(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_nok_no_data_one_lab):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, '-o', 'JSON', 'show-admin-server-access-data',
                                                '-lab', 'CloudLab6128'], SystemExit, 0,
                                               "\"status\": \"Failed\".*ERROR: Lab 'CloudLab6128' does not exist")

    def test_parse_command_line_show_admin_server_access_data_nok_no_data_one_lab_with_snap(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_nok_no_data_one_lab_with_snap):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'show-admin-server-access-data',
                                                '-lab', 'CloudLab6128', '-snap', 'netact/product/99.17.03.0.123'], SystemExit, 0,
                                               "ERROR: Lab 'CloudLab6128' does not exist.*Exit code: '1'")

    def test_parse_command_line_show_admin_server_access_data_nok_no_data_one_lab_with_snap_ASCII(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_nok_no_data_one_lab_with_snap):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, '-o', 'ASCII', 'show-admin-server-access-data',
                                                '-lab', 'CloudLab6128', '-snap', 'netact/product/99.17.03.0.123'], SystemExit, 0,
                                               "ERROR: Lab 'CloudLab6128' does not exist.*Exit code: '1'")

    def test_parse_command_line_show_admin_server_access_data_nok_no_data_one_lab_with_snap_CSV(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_nok_no_data_one_lab_with_snap):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, '-o', 'CSV', 'show-admin-server-access-data',
                                                '-lab', 'CloudLab6128', '-snap', 'netact/product/99.17.03.0.123'], SystemExit, 0,
                                               "ERROR: Lab 'CloudLab6128' does not exist.*Exit code: '1'")

    def test_parse_command_line_show_admin_server_access_data_nok_no_data_one_lab_with_snap_JSON(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_nok_no_data_one_lab_with_snap):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, '-o', 'JSON', 'show-admin-server-access-data',
                                                '-lab', 'CloudLab6128', '-snap', 'netact/product/99.17.03.0.123'], SystemExit, 0,
                                               "\"status\": \"Failed\".*ERROR: Lab 'CloudLab6128' does not exist")

    def test_parse_command_line_show_admin_server_access_data_ok_only_lab_data_all_labs(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_only_lab_data_all_labs):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'show-admin-server-access-data',
                                                ], SystemExit, 0,
                                               "sprintlab245.*\[\].*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_only_lab_data_all_labs_ASCII(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_only_lab_data_all_labs):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'ASCII', '-url', url, 'show-admin-server-access-data',
                                                ], SystemExit, 0,
                                               "sprintlab245.*\[\].*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_only_lab_data_all_labs_CSV(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_only_lab_data_all_labs):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'CSV', '-url', url, 'show-admin-server-access-data',
                                                ], SystemExit, 0,
                                               "labName,buildId,host,password.*sprintlab245,,,,,,.*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_only_lab_data_all_labs_JSON(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_only_lab_data_all_labs):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'JSON', '-url', url, 'show-admin-server-access-data',
                                                ], SystemExit, 0,
                                               "{\"_items\": \[{\"lab_name\": \"sprintlab245\", \"admin_server_access\": \[{}\]}\]}")

    def test_parse_command_line_show_admin_server_access_data_ok_only_lab_data_one_lab(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_only_lab_data_one_lab):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'show-admin-server-access-data',
                                                '-lab', 'sprintlab245'], SystemExit, 0,
                                               "sprintlab245:.*\[\].*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_only_lab_data_one_lab_ASCII(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_only_lab_data_one_lab):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'ASCII', '-url', url, 'show-admin-server-access-data',
                                                '-lab', 'sprintlab245'], SystemExit, 0,
                                               "sprintlab245:.*\[\].*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_only_lab_data_one_lab_CSV(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_only_lab_data_one_lab):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'CSV', '-url', url, 'show-admin-server-access-data',
                                                '-lab', 'sprintlab245'], SystemExit, 0,
                                               "labName,buildId,host,password.*sprintlab245,,,,,,.*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_only_lab_data_one_lab_JSON(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_only_lab_data_one_lab):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'JSON', '-url', url, 'show-admin-server-access-data',
                                                '-lab', 'sprintlab245'], SystemExit, 0,
                                               "{\"lab_name\": \"sprintlab245\", \"admin_server_access\": \[{}\]}")

    def test_parse_command_line_show_admin_server_access_data_nok_only_lab_data_one_lab_with_snap(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_nok_only_lab_data_one_lab_with_snap):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'show-admin-server-access-data',
                                                '-lab', 'sprintlab245', '-snap', 'netact/product/99.17.03.0.123'], SystemExit, 0,
                                               "sprintlab245:.*### ERROR: Snapshot with build id 'netact/product/99.17.03.0.123' does not exist in lab.*Exit code: '1'")

    def test_parse_command_line_show_admin_server_access_data_nok_only_lab_data_one_lab_with_snap_ASCII(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_nok_only_lab_data_one_lab_with_snap):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'ASCII', '-url', url, 'show-admin-server-access-data',
                                                '-lab', 'sprintlab245', '-snap', 'netact/product/99.17.03.0.123'], SystemExit, 0,
                                               "sprintlab245:.*### ERROR: Snapshot with build id 'netact/product/99.17.03.0.123' does not exist in lab.*Exit code: '1'")

    def test_parse_command_line_show_admin_server_access_data_nok_only_lab_data_one_lab_with_snap_CSV(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_nok_only_lab_data_one_lab_with_snap):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'CSV', '-url', url, 'show-admin-server-access-data',
                                                '-lab', 'sprintlab245', '-snap', 'netact/product/99.17.03.0.123'], SystemExit, 0,
                                               "### ERROR: Snapshot with build id 'netact/product/99.17.03.0.123' does not exist in lab.*Exit code: '1'")

    def test_parse_command_line_show_admin_server_access_data_nok_only_lab_data_one_lab_with_snap_JSON(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_nok_only_lab_data_one_lab_with_snap):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'JSON', '-url', url, 'show-admin-server-access-data',
                                                '-lab', 'sprintlab245', '-snap', 'netact/product/99.17.03.0.123'], SystemExit, 0,
                                               "{\"status\": \"Failed\", \"error_text\": \" ### ERROR: Snapshot with build id 'netact/product/99.17.03.0.123' does not exist in lab!\"}")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_snaps_empty_all_labs(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_snaps_empty):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'show-admin-server-access-data',
                                                ], SystemExit, 0,
                                               "sprintlab245:.*\[\].*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_snaps_empty_all_labs_ASCII(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_snaps_empty):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'ASCII', '-url', url, 'show-admin-server-access-data',
                                                ], SystemExit, 0,
                                               "sprintlab245:.*\[\].*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_snaps_empty_all_labs_CSV(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_snaps_empty):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'CSV', '-url', url, 'show-admin-server-access-data',
                                                ], SystemExit, 0,
                                               "labName,buildId,host.*sprintlab245,,,,.*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_snaps_empty_all_labs_JSON(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_snaps_empty):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'JSON', '-url', url, 'show-admin-server-access-data',
                                                ], SystemExit, 0,
                                               "{\"_items\": \[{\"lab_name\": \"sprintlab245\", \"admin_server_access\": \[{}\]}\]}")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_snaps_empty_one_lab(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_snaps_empty):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245'], SystemExit, 0,
                                               "sprintlab245:.*\[\].*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_snaps_empty_one_lab_ASCII(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_snaps_empty):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'ASCII', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245'], SystemExit, 0,
                                               "sprintlab245:.*\[\].*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_snaps_empty_one_lab_CSV(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_snaps_empty):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'CSV', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245'], SystemExit, 0,
                                               "labName,buildId,host.*sprintlab245,,,,.*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_snaps_empty_one_lab_JSON(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_snaps_empty):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'JSON', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245'], SystemExit, 0,
                                               "{\"lab_name\": \"sprintlab245\", \"admin_server_access\": \[{}\]}")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_snaps_empty_one_lab_with_snaps(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_snaps_empty):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245', '-snap', 'cm_n17-5/system/3426'], SystemExit, 0,
                                               "### ERROR: Snapshot with build id 'cm_n17-5/system/3426' does not exist.*Exit code: '1'")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_snaps_empty_one_lab_with_snaps_ASCII(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_snaps_empty):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'ASCII', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245', '-snap', 'cm_n17-5/system/3426'], SystemExit, 0,
                                               "### ERROR: Snapshot with build id 'cm_n17-5/system/3426' does not exist.*Exit code: '1'")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_snaps_empty_one_lab_with_snaps_CSV(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_snaps_empty):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'CSV', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245', '-snap', 'cm_n17-5/system/3426'], SystemExit, 0,
                                               "### ERROR: Snapshot with build id 'cm_n17-5/system/3426' does not exist.*Exit code: '1'")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_snaps_empty_one_lab_with_snaps_JSON(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_snaps_empty):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'JSON', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245', '-snap', 'cm_n17-5/system/3426'], SystemExit, 0,
                                               "{\"status\": \"Failed\", \"error_text\": \" ### ERROR: Snapshot with build id 'cm_n17-5/system/3426' does not exist in lab!\"}")

    ##################################################
    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_one_snaps_all_labs(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_one_snaps):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'show-admin-server-access-data',
                                                ], SystemExit, 0,
                                               "sprintlab245:.*\[buildId: 'cm_n17-2/system/6762', host: 'SprintLab314vm1.netact.nsn-rdnet.net', passw.*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_one_snaps_all_labs_ASCII(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_one_snaps):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'ASCII', '-url', url, 'show-admin-server-access-data',
                                                ], SystemExit, 0,
                                               "sprintlab245:.*\[buildId: 'cm_n17-2/system/6762', host: 'SprintLab314vm1.netact.nsn-rdnet.net', passw.*Exit code: '0'")


    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_one_snaps_all_labs_CSV(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_one_snaps):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'CSV', '-url', url, 'show-admin-server-access-data',
                                                ], SystemExit, 0,
                                               "labName,buildId,host,password,port,protocol,username.*sprintlab245,cm_n17-2/system/6762,SprintLab314vm1.netact.nsn-rdnet.net,nasroot,22,ssh,root.*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_one_snaps_all_labs_JSON(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_one_snaps):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'JSON', '-url', url, 'show-admin-server-access-data',
                                                ], SystemExit, 0,
                                               "{\"_items\": \[{\"lab_name\": \"sprintlab245\", \"admin_server_access\": \[{\"username\": \"root\", \"host\": \"SprintLab314")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_one_snaps_one_lab(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_one_snaps):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245'], SystemExit, 0,
                                               "sprintlab245:.*\[buildId: 'cm_n17-2/system/6762', host: 'SprintLab314vm1.netact.nsn-rdnet.net', passw.*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_one_snaps_one_lab_ASCII(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_one_snaps):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'ASCII', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245'], SystemExit, 0,
                                               "sprintlab245:.*\[buildId: 'cm_n17-2/system/6762', host: 'SprintLab314vm1.netact.nsn-rdnet.net', passw.*Exit code: '0'")


    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_one_snaps_one_lab_CSV(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_one_snaps):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'CSV', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245'], SystemExit, 0,
                                               "labName,buildId,host,password,port,protocol,username.*sprintlab245,cm_n17-2/system/6762,SprintLab314vm1.netact.nsn-rdnet.net,nasroot,22,ssh,root.*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_one_snaps_one_lab_JSON(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_one_snaps):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'JSON', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245'], SystemExit, 0,
                                               "{\"lab_name\": \"sprintlab245\", \"admin_server_access\": \[{\"username\": \"root\", \"host\": \"SprintLab314")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_one_snaps_one_lab_with_snaps(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_one_snaps):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245', '-snap', 'cm_n17-2/system/6762'], SystemExit, 0,
                                               "sprintlab245:.*\[buildId: 'cm_n17-2/system/6762', host: 'SprintLab314vm1.netact.nsn-rdnet.net', passw.*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_one_snaps_one_lab_with_snaps_ASCII(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_one_snaps):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'ASCII', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245', '-snap', 'cm_n17-2/system/6762'], SystemExit, 0,
                                               "sprintlab245:.*\[buildId: 'cm_n17-2/system/6762', host: 'SprintLab314vm1.netact.nsn-rdnet.net', passw.*Exit code: '0'")


    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_one_snaps_one_lab_with_snaps_CSV(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_one_snaps):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'CSV', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245', '-snap', 'cm_n17-2/system/6762'], SystemExit, 0,
                                               "labName,buildId,host,password,port,protocol,username.*sprintlab245,cm_n17-2/system/6762,SprintLab314vm1.netact.nsn-rdnet.net,nasroot,22,ssh,root.*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_one_snaps_one_lab_with_snaps_JSON(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_one_snaps):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'JSON', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245', '-snap', 'cm_n17-2/system/6762'], SystemExit, 0,
                                               "{\"lab_name\": \"sprintlab245\", \"admin_server_access\": {\"username\": \"root\", \"host\": \"SprintLab314")

    ##################################################
    # Several snapshots in lab
    ##################################################

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_several_snaps_all_labs(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_several_snaps):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'show-admin-server-access-data',
                                                ], SystemExit, 0,
                                               "sprintlab245:.*022', host: 'vSprint2260vm1.netact.nsn-rdnet.net'.*buildId: 'netact/product/99.17.03.0.145', .*\[buildId: 'cm_n17-2/system/6762', host: 'SprintLab314vm1.netact.nsn-rdnet.net', passw.*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_several_snaps_all_labs_ASCII(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_several_snaps):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'ASCII', '-url', url, 'show-admin-server-access-data',
                                                ], SystemExit, 0,
                                               "sprintlab245:.*022', host: 'vSprint2260vm1.netact.nsn-rdnet.net'.*buildId: 'netact/product/99.17.03.0.145', .*\[buildId: 'cm_n17-2/system/6762', host: 'SprintLab314vm1.netact.nsn-rdnet.net', passw.*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_several_snaps_all_labs_CSV(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_several_snaps):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'CSV', '-url', url, 'show-admin-server-access-data',
                                                ], SystemExit, 0,
                                               "labName,buildId,host,password,port,protocol,username.*.003,vSprint2260vm1.netact.nsn-r.*sprintlab245,netact/product/99.17.03.0.145,vSprint2260.*sprintlab245,cm_n17-2/system/6762,SprintLab314vm1.netact.nsn-rdnet.net,nasroot,22,ssh,root.*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_several_snaps_all_labs_JSON(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_several_snaps):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'JSON', '-url', url, 'show-admin-server-access-data',
                                                ], SystemExit, 0,
                                               "{\"_items\": \[{\"lab_name\": \"sprintlab245\", \"admin_server_access\": \[{\"username\": \"root\", \"host\": \"vSprint2260vm1.netact.nsn-rdnet.net\", \"protocol\": \"ssh\", \"buildId\": \"netact/product/99.17.03.0.003\", \"password\": \"nasroot\", \"port\": 22},{\"username\": \"root\", \"host\": \"vSprint2260vm1.netact.nsn-rdnet.net\", \"protocol\": \"ssh\", \"buildId\": \"netact/product/99.17.03.0.022\", \"password\": \"nasroot\", \"port\": 22},{\"username\": \"root\", \"host\": \"vSprint2260vm1.netact.nsn-rdnet.net\", \"protocol\": \"ssh\", \"buildId\": \"netact/product/99.17.03.0.145\", \"password\": \"nasroot\", \"port\": 22},{\"username\": \"root\", \"host\": \"SprintLab314vm1.netact.nsn-rdnet.net\", \"protocol\": \"ssh\", \"buildId\": \"cm_n17-2/system/6762\", \"password\": \"nasroot\", \"port\": 22}\]}\]}")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_several_snaps_one_lab(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_several_snaps):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245'], SystemExit, 0,
                                              "sprintlab245:.*022', host: 'vSprint2260vm1.netact.nsn-rdnet.net'.*buildId: 'netact/product/99.17.03.0.145', .*\[buildId: 'cm_n17-2/system/6762', host: 'SprintLab314vm1.netact.nsn-rdnet.net', passw.*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_several_snaps_one_lab_ASCII(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_several_snaps):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'ASCII', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245'], SystemExit, 0,
                                              "sprintlab245:.*022', host: 'vSprint2260vm1.netact.nsn-rdnet.net'.*buildId: 'netact/product/99.17.03.0.145', .*\[buildId: 'cm_n17-2/system/6762', host: 'SprintLab314vm1.netact.nsn-rdnet.net', passw.*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_several_snaps_one_lab_CSV(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_several_snaps):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'CSV', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245'], SystemExit, 0,
                                               "labName,buildId,host,password,port,protocol,username.*.003,vSprint2260vm1.netact.nsn-r.*sprintlab245,netact/product/99.17.03.0.145,vSprint2260.*sprintlab245,cm_n17-2/system/6762,SprintLab314vm1.netact.nsn-rdnet.net,nasroot,22,ssh,root.*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_several_snaps_one_lab_JSON(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_several_snaps):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'JSON', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245'], SystemExit, 0,
                                               "{\"lab_name\": \"sprintlab245\", \"admin_server_access\": \[{\"username\": \"root\", \"host\": \"vSprint2260vm1.netact.nsn-rdnet.net\", \"protocol\": \"ssh\", \"buildId\": \"netact/product/99.17.03.0.003\", \"password\": \"nasroot\", \"port\": 22},{\"username\": \"root\", \"host\": \"vSprint2260vm1.netact.nsn-rdnet.net\", \"protocol\": \"ssh\", \"buildId\": \"netact/product/99.17.03.0.022\", \"password\": \"nasroot\", \"port\": 22},{\"username\": \"root\", \"host\": \"vSprint2260vm1.netact.nsn-rdnet.net\", \"protocol\": \"ssh\", \"buildId\": \"netact/product/99.17.03.0.145\", \"password\": \"nasroot\", \"port\": 22},{\"username\": \"root\", \"host\": \"SprintLab314vm1.netact.nsn-rdnet.net\", \"protocol\": \"ssh\", \"buildId\": \"cm_n17-2/system/6762\", \"password\": \"nasroot\", \"port\": 22}\]}")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_several_snaps_one_lab_with_snaps(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_several_snaps):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245', '-snap', 'cm_n17-2/system/6762'], SystemExit, 0,
                                               "sprintlab245:.*\[buildId: 'cm_n17-2/system/6762', host: 'SprintLab314vm1.netact.nsn-rdnet.net', passw.*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_several_snaps_one_lab_with_snaps_ASCII(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_several_snaps):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'ASCII', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245', '-snap', 'cm_n17-2/system/6762'], SystemExit, 0,
                                               "sprintlab245:.*\[buildId: 'cm_n17-2/system/6762', host: 'SprintLab314vm1.netact.nsn-rdnet.net', passw.*Exit code: '0'")


    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_several_snaps_one_lab_with_snaps_CSV(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_several_snaps):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'CSV', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245', '-snap', 'cm_n17-2/system/6762'], SystemExit, 0,
                                               "labName,buildId,host,password,port,protocol,username.*sprintlab245,cm_n17-2/system/6762,SprintLab314vm1.netact.nsn-rdnet.net,nasroot,22,ssh,root.*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_one_lab_data_several_snaps_one_lab_with_snaps_JSON(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_one_lab_data_several_snaps):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'JSON', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245', '-snap', 'cm_n17-2/system/6762'], SystemExit, 0,
                                               "{\"lab_name\": \"sprintlab245\", \"admin_server_access\": {\"username\": \"root\", \"host\": \"SprintLab314")

    ##################################################
    # Mass lab data
    ##################################################

    def test_parse_command_line_show_admin_server_access_data_ok_mass_labs_data_all_labs(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_mass_labs_data):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'show-admin-server-access-data',
                                                ], SystemExit, 0,
                                               "SprintLab314:.*\[\].*CloudLab416:.*\[buildId: 'netact/product/99.17.03.0.166'.*SprintLab2354:.*\[buildId: 'netact/product/99.17.03.0.303', host: 'SprintLab2.*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_mass_labs_data_all_labs_ASCII(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_mass_labs_data):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'ASCII', '-url', url, 'show-admin-server-access-data',
                                                ], SystemExit, 0,
                                               "SprintLab314:.*\[\].*CloudLab416:.*\[buildId: 'netact/product/99.17.03.0.166'.*SprintLab2354:.*\[buildId: 'netact/product/99.17.03.0.303', host: 'SprintLab2.*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_mass_labs_data_all_labs_CSV(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_mass_labs_data):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'CSV', '-url', url, 'show-admin-server-access-data',
                                                ], SystemExit, 0,
                                               "labName,buildId,host,password,port,protocol,username.*SprintLab576,cm_n17-5/system/3426,SprintLab576vm1.netact.nsn-rdnet.net,nasroot,22,ssh,root.*SprintLab314,,,,,,.*CloudLab416,netact/p.*SprintLab2354,netact/product/99.17.03.0.645,SprintLab2354vm1.netact.nsn-rdnet.net,nasroot,22,ssh,root.*vSprint2368,netact/product/99.17.03.0.112,vSprint2368vm1.netact.nsn-rdnet.net,nasroot,22,ssh,root.*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_mass_labs_data_all_labs_JSON(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_mass_labs_data):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'JSON', '-url', url, 'show-admin-server-access-data',
                                                ], SystemExit, 0,
                                               "{\"_items\": \[{\"lab_name\": \"SprintLab576\", \"admin_server_access\": \[{\"username\": \"root\", \"host\": \"SprintLab576vm1.netact.nsn-rdnet.net\", \"protocol\": \"ssh\", \"buildId\": \"cm_n17-5/system/3426\", \"password\": \"nasroot\", \"port\": 22}\]},{\"lab_name\": \"SprintLab314\", \"admin_server_access\": \[{}\]},{\"lab_name\": \"CloudLab416\", \"admin_server_access\": \[{\"username\": \"root\", \"host\": \"CloudLab416vm1.netact.nsn-rdnet.net\", \"protocol\": \"ssh\", \"buildId\": \"netact/product/99.17.03.0.166\", \"password\": \"nasroot\", \"port\": 22}\]},{\"lab_name\": \"CloudLab9021\", \"admin_server_access\": \[{\"username\": \"root\", \"host\": \"CloudLab9021vm1.netact.nsn-rdnet.net\", \"protocol\": \"ssh\", \"buildId\": \"netact/product/99.17.03.0.123\", \"password\": \"nasroot\", \"port\": 22}\]},{\"lab_name\": \"vSprint2260\", \"admin_server_access\": \[{\"username\":")

    def test_parse_command_line_show_admin_server_access_data_ok_mass_labs_data_one_lab(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_mass_labs_data):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'vSprint5403'], SystemExit, 0,
                                              "vSprint5403:.*\[buildId: 'cm_n17-5/system/3426', host: 'SprintLab576.*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_mass_labs_data_one_lab_ASCII(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_mass_labs_data):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'ASCII', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'vSprint5403'], SystemExit, 0,
                                              "vSprint5403:.*\[buildId: 'cm_n17-5/system/3426', host: 'SprintLab576.*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_mass_labs_data_one_lab_CSV(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_mass_labs_data):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'CSV', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245'], SystemExit, 0,
                                               "labName,buildId,host,password,port,protocol,username.*sprintlab245,cm_n17-5/system/3426,SprintLab576vm1.netact.nsn-rdnet.net,nasroot,22,ssh,root")

    def test_parse_command_line_show_admin_server_access_data_ok_mass_labs_data_one_lab_JSON(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_mass_labs_data):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'JSON', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245'], SystemExit, 0,
                                               "{\"lab_name\": \"sprintlab245\", \"admin_server_access\": \[{\"username\": \"root\", \"host\": \"SprintLab576vm1.netact.nsn-rdnet.net\", \"protocol\": \"ssh\", \"buildId\": \"cm_n17-5/system/3426\", \"password\": \"nasroot\", \"port\": 22}\]}")

    def test_parse_command_line_show_admin_server_access_data_ok_mass_labs_data_one_lab_with_snaps(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_mass_labs_data):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245', '-snap', 'cm_n17-5/system/3426'], SystemExit, 0,
                                               "sprintlab245:.*\[buildId: 'cm_n17-5/system/3426', host: 'SprintLab576vm1.netact.nsn-rdnet.net', passw.*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_mass_labs_data_one_lab_with_snaps_ASCII(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_mass_labs_data):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'ASCII', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245', '-snap', 'cm_n17-5/system/3426'], SystemExit, 0,
                                               "sprintlab245:.*\[buildId: 'cm_n17-5/system/3426', host: 'SprintLab576vm1.netact.nsn-rdnet.net', passw.*Exit code: '0'")

    def test_parse_command_line_show_admin_server_access_data_ok_mass_labs_data_one_lab_with_snaps_CSV(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_mass_labs_data):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'CSV', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245', '-snap', 'cm_n17-5/system/3426'], SystemExit, 0,
                                               "labName,buildId,host,password,port,protocol,username.*sprintlab245,cm_n17-5/system/3426,SprintLab576vm1.netact.nsn-rdnet.net,nasroot,22,ssh,root.*Exit code: '0'")


    def test_parse_command_line_show_admin_server_access_data_ok_mass_labs_data_one_lab_with_snaps_JSON(self):
        with HTTMock(self.mock_api_show_admin_server_access_data_ok_mass_labs_data):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-o', 'JSON', '-url', url, 'show-admin-server-access-data',
                                                '-l', 'sprintlab245', '-snap', 'cm_n17-5/system/3426'], SystemExit, 0,
                                               "{\"lab_name\": \"sprintlab245\", \"admin_server_access\": {\"username\": \"root\", \"host\": \"SprintLab576vm1.netact.nsn-rdnet.net\", \"protocol\": \"ssh\", \"buildId\": \"cm_n17-5/system/3426\", \"password\": \"nasroot\", \"port\": 22}}")

    @mock.patch('client.rest_client.get_item')
    def test_get_existing_config_value(self, get_item):
        get_item.return_value = {"name": "SOME_EXISTING_VAR", "value": "XXXXXXXXXXXX", "_id": "5b7e7cd3ab3d3f00019baa57", "_etag": "4af75a0dc3a7b61fe5825d1b87e05a0d791c7e04"}
        argv = ['--username', 'admin', '-url', url,
                 'config', 'get', 'SOME_EXISTING_VAR']
        log.info('CMD: %s' % ("\t".join(argv)))
        parsed_args = client.parse_command_line(argv)
        log.info('parsed_args: %s' % (parsed_args))
        retval = client.execute_command_line(parsed_args)
        log.info('retval: %s' % (retval))
        self.assertEqual(retval, "XXXXXXXXXXXX")

    @mock.patch('client.rest_client.get_item')
    def test_get_not_existing_config_value(self, get_item):
        get_item.side_effect = exceptions.HTTPError()
        argv = ['--username', 'admin', '-url', url,
                 'config', 'get', 'SOME_VAR']
        log.info('CMD: %s' % ("\t".join(argv)))
        retval = client.execute_command_line(client.parse_command_line(argv))
        log.info('retval: %s' % (retval))
        self.assertEqual(retval, None)

    @mock.patch('client.rest_client.delete_item')
    @mock.patch('client.rest_client.get_item')
    def test_remove_existing_config_value(self, get_item, delete_item):
        get_item.return_value = {"name": "SOME_EXISTING_VAR", "value": "XXXXXXXXXXXX", "_id": "5b7e7cd3ab3d3f00019baa57", "_etag": "4af75a0dc3a7b61fe5825d1b87e05a0d791c7e04"}
        argv = ['--username', 'admin', '-url', url,
                 'config', 'del', 'SOME_EXISTING_VAR']
        log.info('CMD: %s' % ("\t".join(argv)))
        retval = client.execute_command_line(client.parse_command_line(argv))
        log.info('retval: %s' % (retval))
        log.info('Calls to client.rest_client.delete_item: %s' % (delete_item.mock_calls))
        delete_item.assert_any_call('config', 'SOME_EXISTING_VAR', None, '4af75a0dc3a7b61fe5825d1b87e05a0d791c7e04', url)
        self.assertTrue(retval)

    @mock.patch('client.rest_client.delete_item')
    @mock.patch('client.rest_client.get_item')
    def test_remove_not_existing_config_value(self, get_item, delete_item):
        get_item.side_effect = exceptions.HTTPError()
        argv = ['--username', 'admin', '-url', url,
                 'config', 'del', 'SOME_VAR']
        log.info('CMD: %s' % ("\t".join(argv)))
        retval = client.execute_command_line(client.parse_command_line(argv))
        log.info('Calls to client.rest_client.get_item: %s' % (get_item.mock_calls))
        log.info('Calls to client.rest_client.delete_item: %s' % (delete_item.mock_calls))
        log.info('retval: %s' % (retval))
        self.assertFalse(retval)

    @mock.patch('client.rest_client.post_resource')
    @mock.patch('client.rest_client.patch_item')
    @mock.patch('client.rest_client.get_item')
    def test_add_new_config_value(self, get_item, patch_item, post_resource):
        get_item.side_effect = exceptions.HTTPError()
        argv = ['--username', 'admin', '-url', url,
                 'config', 'set', 'SOME_VAR', 'a value']
        log.info('CMD: %s' % ("\t".join(argv)))
        retval = client.execute_command_line(client.parse_command_line(argv))
        log.info('Calls to client.rest_client.get_item: %s' % (get_item.mock_calls))
        log.info('Calls to client.rest_client.patch_item: %s' % (patch_item.mock_calls))
        log.info('Calls to client.rest_client.post_resource: %s' % (post_resource.mock_calls))
        post_resource.assert_any_call('config', {'name': 'SOME_VAR', 'value': 'a value'}, url)
        self.assertEqual(patch_item.call_count, 0, 'rest.patch_item should not be called')

    @mock.patch('client.rest_client.post_resource')
    @mock.patch('client.rest_client.patch_item')
    @mock.patch('client.rest_client.get_item')
    def test_patch_existing_config_value(self, get_item, patch_item, post_resource):
        get_item.return_value = {"name": "SOME_VAR", "value": "old value", "_id": "5b7e7cd3ab3d3f00019baa57", "_etag": "4af75a0dc3a7b61fe5825d1b87e05a0d791c7e04"}
        argv = ['--username', 'admin', '-url', url,
                 'config', 'set', 'SOME_VAR', 'NEW VALUE']
        log.info('CMD: %s' % ("\t".join(argv)))
        retval = client.execute_command_line(client.parse_command_line(argv))
        log.info('Calls to client.rest_client.get_item: %s' % (get_item.mock_calls))
        log.info('Calls to client.rest_client.patch_item: %s' % (patch_item.mock_calls))
        log.info('Calls to client.rest_client.post_resource: %s' % (post_resource.mock_calls))
        patch_item.assert_any_call('config', 'SOME_VAR', {'value': 'NEW VALUE'}, '4af75a0dc3a7b61fe5825d1b87e05a0d791c7e04', url)
        self.assertEqual(post_resource.call_count, 0, 'rest.post_resource should not be called')


##############################################################################################################
# show snapshots
##############################################################################################################




    def test_show_snapshot_OK_when_one_snapshot_is_unavailable(self):
        with HTTMock(self.mock_api_mock_show_snapshot_OK_one_snapshot_unavailable_data):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin','-url', url,
                                                'show-snapshots'],SystemExit, 0,"netact/product/99.17.03.0.424.*UNAVAILABLE.*cm_n17-2/system/6762.*AVAILABLE" )



    def test_show_snapshot_OK_when_one_snapshot_is_unavailable_and_labs_shown(self):
        with HTTMock(self.mock_api_mock_show_snapshot_OK_one_snapshot_unavailable_data):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin','-url', url,
                                                'show-snapshots', '-labs'],SystemExit, 0,".*vSprint9711.*reserved")


    def test_show_snapshot_NOK_when_snapshot_should_be_unavailalbe_but_it_is_available(self):
        with HTTMock(self.mock_api_mock_show_snapshot_OK_one_snapshot_unavailable_data):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin','-url', url,
                                                'show-snapshots', '-labs'],SystemExit, 0,stdout_not_match_data="netact/product/99.17.03.*cm_n17-5/system/3426.* AVAILABLE.*cm_n17-2/system/6762")

    def test_show_snapshot_OK_when_it_uses_snapshot_parameter(self):
        with HTTMock(self.mock_api_mock_show_snapshot_OK_one_snapshot_unavailable_data):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin','-url', url,
                                                'show-snapshots',"-snap","netact/product/99.17.03.0.112"],SystemExit, 0,"netact/product/99.17.03.0.112 .*AVAILABLE")

    def test_show_snapshot_OK_when_it_uses_snapshot_parameter_with_labs_on(self):
        with HTTMock(self.mock_api_mock_show_snapshot_OK_one_snapshot_unavailable_data):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'admin', '-url', url,
                                                'show-snapshots',"-labs", "-snap",
                                                "netact/product/99.17.03.0.112" ], SystemExit, 0,
                                               "netact/product/99.17.03.0.112 .*AVAILABLE.*vSprint972               free")



    def test_show_snapshots_with_html_ouput(self):
        with HTTMock(self.mock_api_mock_show_snapshot_OK_one_snapshot_unavailable_data):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-url', url, '-o', 'HTML', 'show-snapshots'
                                                ], SystemExit, 0,
                                               '.*ol width="200px" /><col width="200px" /><tr style="background: none" valign="top"><td>vSprint972</td><td>free</td><td>vsprint</td></tr></table></td></tr><tr valign="top"><td>netact/product/99.17.03.0.003</td><td>UNAVAILABLE</td><td><table class="fixed"style="text-align:left;background: none;"><col width="200px" /><col width="200px" /><col width="200px" /><tr style="background: none" valign="top"><td>vSprint9711</td><td>reserved</td><td>vsprint</td></tr></table></td></tr><tr valign="top"><td>netact/product/99.17.03.0.145</td><td>UNAVAILABLE</td><td><table class="fixed"style="text-align:left;background: none;"><col width="200px" /><col width="200px" /><col width="200px" /><tr style="background: none" valign="top"><td>vSprint9711</td><td>reserved</td><td>vsprint</td></tr></table></td></tr><tr valign="top"><td>netact/product/99.17.03.0.004</td><td>UNAVAILABLE</td><td><table class="fixed"style="text-align:left;background: none;"><col width="200px" /><col width="200px" /><col width="200px" /><tr style="background: none" valign="top"><td>vSprint6935</td><td>reserved</td><td>vsprint</td></tr></table></td></tr><tr valign="top"><td>netact/product/99.17.03.0.166</td><td>AVAILABLE</td><td><table class="fixed"style="text-align:left;background: none;"><col width="200px" /><col width="200px" /><col width="200px" /><tr style="background: none" valign="top"><td>CloudLab3672</td><td>free</td><td>None</td></tr></table></td></tr><tr valign="top"><td>cm_n17-2/system/6762</td><td>AVAILABLE</td><td><table class="fixed"style="text-align:left;background: none;"><col width="200px" /><col width="200px" /><col width="200px" /><tr style="background: none" valign="top"><td>SprintLab6936</td><td>free</td><td>other</td></tr></table></td></tr><tr valign="top"><td>netact/product/99.17.03.0.645</td><td>UNAVAILABLE</td><td><table class="fixed"style="text-align:left;background: none;"><col width="200px" /><col width="200px" /><col width="200px" .*')


    def test_lab_reservation_set_duration(self):
        self._exec_lab_reservation_change('300', 'duration', '300')

    def test_lab_reservation_set_duration_adding(self):
        self._exec_lab_reservation_change('+300', 'duration', '+300')
        self._exec_lab_reservation_change('+300min', 'duration', '+18000')

    def test_lab_reservation_set_duration_reduction(self):
        self._exec_lab_reservation_change('-300', 'duration', '-300')

    def test_lab_reservation_set_expiration_no_dst(self):
        _2018_12_15_1000 = 1544860800
        log.info('_2018_12_15_1000: %u -> %s', _2018_12_15_1000, time.ctime(_2018_12_15_1000))
        self._exec_lab_reservation_set_expiration(_2018_12_15_1000)

    def test_lab_reservation_set_expiration_dst(self):
        _2018_07_01_1300 = 1530439200
        log.info('_2018_07_01_1300: %u -> %s', _2018_07_01_1300, time.ctime(_2018_07_01_1300))
        self._exec_lab_reservation_set_expiration(_2018_07_01_1300)

    def _exec_lab_reservation_set_expiration(self, tstamp_epoch):
        t_str = time.strftime('%Y-%m-%dT%H:00', time.localtime(tstamp_epoch))
        t_str_expected = time.strftime('%a, %d %b %Y %H:00:00 GMT', time.gmtime(tstamp_epoch))
        log.info('local: %s utc: %s', t_str, t_str_expected)
        self._exec_lab_reservation_change(t_str, 'expireAt', t_str_expected)

    def test_lab_reservation_set_expiration_invalid_input(self):
        with self.assertRaises(AssertionError):
            self._exec_lab_reservation_change('JUNK', None, None)

    @mock.patch('client.rest_client.patch_item')
    @mock.patch('client.rest_client.get_item')
    def _exec_lab_reservation_change(self, duration_input, duration_attribute, duration_expected, get_item, patch_item):
        service_url='http://lss-fake:1234'
        lab_name = 'lab001'
        username = 'foo'
        reservation = '1234567890'
        reservation_etag = 'v2'
        get_item.return_value = dict(
            # lab item
            reservation = reservation,
            # reservation item
            lab_name = 'lab001',
            username = 'foo',
            _etag = reservation_etag,
        )
        log.debug('CALL: client.lab_request.change_lab_reservation(service_url=%s, username = %s, duration=%s)',
            service_url, username,
            duration_input)
        client.lab_request.change_lab_reservation(service_url=service_url, username = username, duration=duration_input)

        log.info('Calls to client.rest_client.patch_item: %s', patch_item.mock_calls)
        patch_item.assert_called_with('reservations', reservation, 
                {duration_attribute: duration_expected}, 
                reservation_etag, service_url, raise_error=mock.ANY)


    def test_show_snapshots_with_html_ouput_when_not_labs_are_in_pool(self):
        with HTTMock(self.mock_api_labs_NOK_lab_not_found):
            self._command_line_operation_check(inspect.stack()[0][3],
                                               ['--username', 'tester', '-url', url, '-o', 'HTML', 'show-snapshots'
                                                ], SystemExit, 0,
                                               'Labs</th> </tr></table> </div> </body> </html>')

    def test_count_to_seconds_no_unit(self):
        self._exec_test_count_to_seconds('1234', 1234)

    def test_count_to_seconds_float(self):
        self._exec_test_count_to_seconds('7.5m', 450)

    def test_count_to_seconds_int(self):
        self._exec_test_count_to_seconds(14916, 14916)

    def test_count_to_seconds_None(self):
        self._exec_test_count_to_seconds(None, None)

    def test_count_to_seconds_seconds(self):
        self._exec_test_count_to_seconds('4s', 4)
        self._exec_test_count_to_seconds('4sec', 4)
        self._exec_test_count_to_seconds('4seconds', 4)
        self._exec_test_count_to_seconds('4second', 4)
        self._exec_test_count_to_seconds('4 second', 4)

    def test_count_to_seconds_minutes(self):
        self._exec_test_count_to_seconds('7m', 420)
        self._exec_test_count_to_seconds('7  min', 420)
        self._exec_test_count_to_seconds('7 minute', 420)
        self._exec_test_count_to_seconds('7 minutes', 420)

    def test_count_to_seconds_hours(self):
        self._exec_test_count_to_seconds('5h', 18000)
        self._exec_test_count_to_seconds('5   hours', 18000)
        self._exec_test_count_to_seconds('5hours', 18000)
        self._exec_test_count_to_seconds('5hour', 18000)

    def test_count_to_seconds_signed(self):
        self._exec_test_count_to_seconds('-5hour', -18000)
        self._exec_test_count_to_seconds('-5 min', -300)
        self._exec_test_count_to_seconds('+5 min', 300)
        self._exec_test_count_to_seconds('+5', 5)
        self._exec_test_count_to_seconds('-3000s', -3000)
        self._exec_test_count_to_seconds('-3000', -3000)

    def _exec_test_count_to_seconds(self, in_string, seconds_expected):
        seconds = client.utils.count_seconds(in_string)
        self.assertEqual(seconds_expected, seconds, 
            'client.utils.count_seconds(%s) should return %s - output was %s' % (in_string, seconds_expected, seconds)
        )
        

##############################################################################################################
# Support functions
##############################################################################################################



def _list_tests():
    show_tests, filter_str = _parse_args()
    if show_tests:
        tests = _test_methods(ClientTests)
        service_tests = _show_test_methods(tests, filter_str)
        _check_coverage(service_tests, filter_str)
        sys.exit(0)


def _parse_args():
    filter_str = ""
    show_tests = 0
    argv_len = len(sys.argv)
    if argv_len >= 2:
        if sys.argv[1] in ("-lt", "--list_tests"):
            show_tests = 1
            if argv_len >= 3:
                filter_str = sys.argv[2]
    return (show_tests, filter_str)


def _show_test_methods(tests, filter_str):
    service_tests = {}
    data = "\n"
    binary = "python client_test.py ClientTests."
    test_cnt = 0
    pattern = re.compile(filter_str)
    for test in tests:
        if filter_str == "" or pattern.search(test):
            data += " {}{}\n".format(binary, test)
            test_cnt += 1
        m = re.search('command_line_(\S+)_(ok|OK|NOK|ok|nok)(_|)', test)
        if m:
            test_name = m.group(1).replace('_', '-')
            if test_name not in service_tests:
                service_tests[test_name] = {}
            service_tests[test_name][test] = 0
#            print "    YYY: {}  -> {}".format(test_name, test)
    data += "\n Test count : '{}'\n".format(test_cnt)
    print data
    return service_tests


def _test_methods(cls):
    tests = []
    for name, y in cls.__dict__.items():
        if type(y) == FunctionType and name.startswith("test"):
            tests.append(name)
    return sorted(tests)


def _check_coverage(service_tests, filter_str):
    data = ""
    data_line_ok = ""
    data_line_nok = ""
    cmd = 'python client.py -h | egrep "^\s+{.*}" | tail -1'
    output = subprocess.check_output(cmd, shell=True)
    services = output.strip().replace('{', '').replace('}', '').split(",")
    for service in services:
        line_format = "\t%-30.30s    %-10.10s     %s\n"
        test_count = 0
        pattern = re.compile(filter_str.replace('_', '-'))
        if service in service_tests:
            test_count = len(service_tests[service])
            status = "OK"
            if filter_str == "" or pattern.search(service):
                data_line_ok += line_format % (service, status, test_count)
        else:
            status = "NOK"
            if filter_str == "" or pattern.search(service):
                data_line_nok += line_format % (service, status, test_count)

    data += data_line_nok
    data += "\n\n"
    data += data_line_ok
    print "{}".format(data)


if __name__ == '__main__':
    _list_tests()
    unittest.main()
