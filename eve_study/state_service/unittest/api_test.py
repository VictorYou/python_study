import api
import unittest
from mock import patch, ANY as mock_ANY
import json
from datetime import datetime, timedelta
import time
from wsgiref.handlers import format_date_time
import os
import logging
logging.basicConfig(level=logging.DEBUG)

# http://eve.readthedocs.io/en/latest/config.html
# http://werkzeug.pocoo.org/docs/0.11/test/#werkzeug.test.Client
app = api.app.test_client()

os.environ["STATE_SERVICE_TESTING_ENABLED"] = "yes"

class LabTests(unittest.TestCase):

    def setUp(self):
        self.start_time = time.time()

    def tearDown(self):
        # WARNING! deletes all data in mongodb
        app.delete('/labs')
        t = time.time() - self.start_time
        print " %.3f: %s" % (t, self.id())

    def _createLab(self, lab_name, expected_status=201):
        test_data = {"lab_name": lab_name}
        data = json.dumps(test_data)
        headers = {'Content-Type': "application/json"}
        # http://flask.pocoo.org/docs/0.12/api/#response-objects
        response = app.post('/labs', data=data, headers=headers)
        status = response.status_code
        self.assertEqual(status, expected_status)
        response_data = json.loads(response.data)
        if '_id' in response_data:
            lab_uid = response_data['_id']
        else:
            lab_uid = "<none>"
        return status, lab_uid, response_data

    def _createLabs(self, lab_names):
        rets = []
        for lab_name in lab_names:
            ret = self._createLab(lab_name)
            rets.append(ret)
        return rets

    def _checkLabsData(self, test_labs):
        ret = []
        ret = _get_lab("")
        txt = "---> Result of _getLab()"
        _print_ret(txt, ret)
        labs = self._getLabsFromResult(ret)
        self.assertEqual(labs, test_labs)

    def _getLabsFromResult(self, ret):
        labs = []
        for lab in ret[2]["_items"]:
            labs.append(lab["lab_name"])
        return labs

    def _mass_creation_labs(self, nbr):
        ret = []
        rets = []
        test_labs = []
        for x in range(0, nbr):
            test_labs.append("myTestLab30%0dMass%d" % (x, nbr))
        rets = self._createLabs(test_labs)
        txt = "---> Result of _createLabs()"
        _print_rets(txt, rets)
        ret = []
        ret = _get_lab("")
        txt = "---> Result of _getLab() page1"
        _print_ret(txt, ret)
        ret = _get_lab("?page=2")
        txt = "---> Result of _getLab() page2"
        txt = "---> Result of _getLab()"
        _print_ret(txt, ret)

    def test_lab_creation(self):
        expected_initial_status = "queued_for_initialization"
        test_data = {"lab_name": "testlab123"}
        data = json.dumps(test_data)
        headers = {'Content-Type': "application/json"}
        # http://flask.pocoo.org/docs/0.12/api/#response-objects
        response = app.post('/labs', data=data, headers=headers)
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        lab_uid = response_data['_id']
        get_response = app.get('/labs/' + lab_uid)
        self.assertEqual(get_response.status_code, 200)
        get_response_data = json.loads(get_response.data)
        self.assertEqual(get_response_data["lab_name"], test_data["lab_name"])
        self.assertEqual(get_response_data["status"], expected_initial_status)

    def test_lab_creation_with_single(self):
        lab_name = "mynewlab223"
        retC = self._createLab(lab_name)
        retG = _get_lab(retC[1])
        _print_ret("----> _createLab():", retC)
        _print_ret("----> _getLab()   :", retG)
        self.assertEqual(retG[2]["_id"], retC[2]["_id"])
        self.assertEqual(retG[2]["lab_name"], lab_name)

    def test_lab_mass_creation_with_2_same_labs(self):
        test_labs = ["mynewlabSAME223Mass", "mynewlabSAME223Mass"]
        ret = self._createLab(test_labs[0])
        txt = "---> Result of SAMELAB_1 _createLabs()"
        _print_ret(txt, ret)
        ret = self._createLab(test_labs[0], 422)
        txt = "---> Result of SAMELAB_2 _createLabs()"
        _print_ret(txt, ret)

    def test_lab_mass_creation_with_2_labs(self):
        ret = []
        rets = []
        test_labs = ["mynewlab223Mass", "myTestLab921Mass"]
        rets = self._createLabs(test_labs)
        txt = "---> Result of _createLabs()"
        _print_rets(txt, rets)
        self._checkLabsData(test_labs)

    def test_lab_mass_creation_with_11_labs(self):
        self._mass_creation_labs(11)

    def test_lab_mass_creation_with_222_labs(self):
        self._mass_creation_labs(222)

    def test_lab_removal_with_force(self):
        labid = _post_lab("testlab1", extra_fields={'status': "preserving_state"})
        _, _, labdata = _get_lab(labid)
        lab_etag = labdata['_etag']
        headers = {"If-Match": lab_etag}
        response = app.delete('labs/{}?force'.format(labid), headers=headers)
        self.assertEqual(response.status_code, 204)
        status_code, _, _ = _get_lab(labid)
        self.assertEqual(status_code, 404)

    def test_lab_removal_fails_if_lab_is_not_in_final_state(self):
        labid = _post_lab("testlab2", extra_fields={'status': "preserving_state"})
        _, _, labdata = _get_lab(labid)
        lab_etag = labdata['_etag']
        headers = {"If-Match": lab_etag}
        response = app.delete('labs/{}'.format(labid), headers=headers)
        self.assertEqual(response.status_code, 422)
        status_code, _, _ = _get_lab(labid)
        self.assertEqual(status_code, 200)

    def test_lab_removal_removes_states_and_reservation(self):
        labid = _post_lab("ttt")
        state_data = dict(lab=labid,
                          build=dict(id="foobar"),
                          snapshot_status="available",
                          snapshot_id="foobar"
                          )
        reservation_data = dict(lab=labid,
                                username="tester"
                                )
        state_id = _post_resource('states', data=state_data)
        reservation_id = _post_resource('reservations', reservation_data)
        response = _delete_lab(labid)
        self.assertEqual(response.status_code, 204)
        lab_status_code, _, _ = _get_lab(labid)
        self.assertEqual(lab_status_code, 404)
        state_status_code, _, _ = _get_state(state_id)
        self.assertEqual(state_status_code, 404)
        reservation_status_code, _, _ = _get_reservation(reservation_id)
        self.assertEqual(state_status_code, 404)

    def test_bug_lab_batch_removal_trailing_slash_test(self):
        labid = _post_lab("ttt")
        _, _, labdata = _get_lab(labid)
        lab_etag = labdata['_etag']
        headers = {"If-Match": lab_etag}
        response = app.delete('labs/', headers=headers)
        self.assertEqual(response.status_code, 204)
        status_code, _, _ = _get_lab(labid)
        self.assertEqual(status_code, 404)


class StateTests(unittest.TestCase):

    def setUp(self):
        self.start_time = time.time()

    def tearDown(self):
        # WARNING! deletes data in mongodb
        app.delete('/labs')
        app.delete('/reservations')
        app.delete('/states')
        t = time.time() - self.start_time
        print " %.3f: %s" % (t,self.id())

    @patch('api.snapshot_tasks.take_snapshot.delay')
    def test_state_creation_creates_cross_reference_to_lab_object_and_triggers_snapshot(self, mock_tasks):
        expected_initial_status = "queued"
        lab_uid = _post_lab("testlab")
        test_data = {"lab": lab_uid,
                     "build": {"id": "netact/product/123"}
                     }
        data = json.dumps(test_data)
        headers = {'Content-Type': "application/json"}
        # http://flask.pocoo.org/docs/0.12/api/#response-objects
        response = app.post('/states', data=data, headers=headers)
        mock_tasks.assert_called()
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        state_uid = response_data['_id']
        retS = _get_state(state_uid)
        self.assertEqual(retS[2]["snapshot_status"], expected_initial_status)
        retL = _get_lab(lab_uid)
        self.assertIn(state_uid, retL[2]["states"])

    @patch('api.snapshot_tasks.take_snapshot.delay')
    def test_state_import_case_does_not_trigger_snapshot(self, mock_tasks):

        lab_uid = _post_lab("testlab")
        test_data = {"lab": lab_uid,
                     "build": {"id": "netact/product/123"},
                     "snapshot_id": "dummy-id-12345",
                     "snapshot_status": "available",
                     "admin_server_access.username": "testuser",
                     "admin_server_access.password": "mysweetpw",
                     "admin_server_access.port": "22",
                     "admin_server_access.host": "myhost"
                     }
        data = json.dumps(test_data)
        headers = {'Content-Type': "application/json"}
        # http://flask.pocoo.org/docs/0.12/api/#response-objects
        response = app.post('/states', data=data, headers=headers)
        mock_tasks.assert_not_called()
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        state_uid = response_data['_id']
        retS = _get_state(state_uid)
        self.assertEqual(retS[2]["snapshot_status"], "available")
        self.assertEqual(retS[2]["admin_server_access"]["username"], "testuser")
        self.assertEqual(retS[2]["admin_server_access"]["password"], "mysweetpw")
        self.assertEqual(retS[2]["admin_server_access"]["port"], 22)
        retL = _get_lab(lab_uid)
        self.assertIn(state_uid, retL[2]["states"])

    @patch('api.snapshot_tasks.take_snapshot.delay')
    @patch('api.snapshot_tasks.revert_to_snapshot.delay')
    def test_state_revert_endpoint_triggers_revert(self, mock_revert_to_snapshot, mock_take_snapshot):
        lab_uid = _post_lab("testlab")
        test_data = {"lab": lab_uid,
                     "build": {"id": "netact/product/123"}
                     }
        data = json.dumps(test_data)
        headers = {'Content-Type': "application/json"}
        # http://flask.pocoo.org/docs/0.12/api/#response-objects
        response = app.post('/states', data=data, headers=headers)
        mock_take_snapshot.assert_called()
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        state_id = response_data['_id']
        state_etag = response_data['_etag']
        retL = _get_lab(lab_uid)
        self.assertIn(state_id, retL[2]["states"])
        response = app.patch("states/{}/revert".format(state_id))
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response_data, {'_status': "OK"})
        mock_revert_to_snapshot.assert_called_with(state_id=state_id, lab_id=lab_uid, lab_info=mock_ANY, testing_enabled=False, lab_whitelisted=False)

    @patch('api.snapshot_tasks.take_snapshot.delay')
    @patch('api.snapshot_tasks.revert_to_snapshot.delay')
    def test_state_revert_endpoint_not_found_state(self, mock_revert, mock_take_snapshot):
        lab_uid = _post_lab("testlab")
        test_data = {"lab": lab_uid,
                     "build": {"id": "netact/product/123"}
                     }
        data = json.dumps(test_data)
        headers = {'Content-Type': "application/json"}
        # http://flask.pocoo.org/docs/0.12/api/#response-objects
        response = app.post('/states', data=data, headers=headers)
        mock_take_snapshot.assert_called()
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        state_id = response_data['_id']
        state_etag = response_data['_etag']
        retL = _get_lab(lab_uid)
        self.assertIn(state_id, retL[2]["states"])
        response = app.patch("states/12354/revert".format(state_id))
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_data['_status'], "ERR")
        mock_revert.assert_not_called()


    @patch('api.snapshot_tasks.take_snapshot.delay')
    @patch('api.snapshot_tasks.revert_to_snapshot.delay')
    def test_state_revert_endpoint_other_failure(self, mock_revert, mock_take_snapshot):
        lab_uid = _post_lab("testlab")
        test_data = {"lab": lab_uid,
                     "build": {"id": "netact/product/123"}
                     }
        data = json.dumps(test_data)
        headers = {'Content-Type': "application/json"}
        # http://flask.pocoo.org/docs/0.12/api/#response-objects
        response = app.post('/states', data=data, headers=headers)
        mock_take_snapshot.assert_called()
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        state_id = response_data['_id']
        state_etag = response_data['_etag']
        retL = _get_lab(lab_uid)
        self.assertIn(state_id, retL[2]["states"])
        mock_revert.side_effect = [Exception("Fake exception")]
        response = app.patch("states/{}/revert".format(state_id))
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response_data['_status'], "ERR")
        mock_revert.assert_called()

    @patch('api.snapshot_tasks.take_snapshot.delay')
    def test_failed_state_creation_does_not_trigger_snapshotting(self, mock_tasks):
        test_data = {"lab": None,
                     "build": {"id": "netact/product/123"}}
        data = json.dumps(test_data)
        headers = {'Content-Type': "application/json"}
        # http://flask.pocoo.org/docs/0.12/api/#response-objects
        response = app.post('/states', data=data, headers=headers)
        self.assertGreaterEqual(response.status_code, 400)
        mock_tasks.assert_not_called()
        test_data = [{"lab": None,
                     "build": {"id": "netact/product/123"}
                      }]
        data = json.dumps(test_data)
        headers = {'Content-Type': "application/json"}
        # http://flask.pocoo.org/docs/0.12/api/#response-objects
        response = app.post('/states', data=data, headers=headers)
        self.assertGreaterEqual(response.status_code, 400)
        mock_tasks.assert_not_called()

    @patch('api.snapshot_tasks.take_snapshot.delay')
    def test_state_bulk_creation_creates_cross_references_to_lab_objects_and_triggers_snapshot_tasks(self, mock_tasks):
        lab1_uid = _post_lab("testlab1")
        lab2_uid = _post_lab("testlab2")
        test_data = [{"lab": lab1_uid,
                     "build": {"id": "netact/product/123"}
                      },
                     {"lab": lab1_uid,
                     "build": {"id": "netact/product/1234"}
                      },
                     {"lab": lab2_uid,
                      "build": {"id": "netact/product/123"}
                      }
                     ]
        data = json.dumps(test_data)
        headers = {'Content-Type': "application/json"}
        # http://flask.pocoo.org/docs/0.12/api/#response-objects
        response = app.post('/states', data=data, headers=headers)
        self.assertEqual(mock_tasks.call_count, 3)
        self.assertEqual(response.status_code, 201)
        lab1 = _get_lab(lab1_uid)
        lab2 = _get_lab(lab2_uid)
        self.assertEqual(len(lab1[2]["states"]), 2)
        self.assertEqual(len(lab2[2]["states"]), 1)

    @patch('api.snapshot_tasks.take_snapshot.delay')
    def test_state_bulk_import_does_not_trigger_snapshot_tasks(self, mock_tasks):
        lab1_uid = _post_lab("testlab1")
        lab2_uid = _post_lab("testlab2")
        test_data = [{"lab": lab1_uid,
                      "build": {"id": "netact/product/123"},
                      "snapshot_id": "32144354",
                      "snapshot_status": "available"
                      },
                     {"lab": lab1_uid,
                      "build": {"id": "netact/product/1234"},
                      "snapshot_id": "32144354",
                      "snapshot_status": "available"
                      },
                     {"lab": lab2_uid,
                      "build": {"id": "netact/product/123"},
                      "snapshot_id": "32144354",
                      "snapshot_status": "available"
                      }
                     ]
        data = json.dumps(test_data)
        headers = {'Content-Type': "application/json"}
        # http://flask.pocoo.org/docs/0.12/api/#response-objects
        response = app.post('/states', data=data, headers=headers)
        mock_tasks.assert_not_called()
        self.assertEqual(response.status_code, 201)
        lab1 = _get_lab(lab1_uid)
        lab2 = _get_lab(lab2_uid)
        self.assertEqual(len(lab1[2]["states"]), 2)
        self.assertEqual(len(lab2[2]["states"]), 1)

    @patch('api.snapshot_tasks.take_snapshot.delay')
    def test_state_removal_removes_cross_reference_from_lab_object(self, mock_tasks):
        expected_initial_status = "queued"
        lab_uid = _post_lab("testlab")
        test_data = {"lab": lab_uid,
                     "build": {"id": "netact/product/123"}
                     }
        data = json.dumps(test_data)
        headers = {'Content-Type': "application/json"}
        # http://flask.pocoo.org/docs/0.12/api/#response-objects
        response = app.post('/states', data=data, headers=headers)
        response = app.post('/states', data=data, headers=headers)
        response = app.post('/states', data=data, headers=headers)
        response = app.post('/states', data=data, headers=headers)
        response = app.post('/states', data=data, headers=headers)
        response = app.post('/states', data=data, headers=headers)
        mock_tasks.assert_called()
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        state_uid = response_data['_id']
        state_etag = response_data['_etag']
        retS = _get_state(state_uid)
        self.assertEqual(retS[2]["snapshot_status"], expected_initial_status)
        retL = _get_lab(lab_uid)
        self.assertIn(state_uid, retL[2]["states"])
        headers.update({"If-Match": state_etag})
        r = app.delete('states/{}'.format(state_uid), headers=headers)
        retL = _get_lab(lab_uid)
        self.assertNotIn(state_uid, retL[2]["states"])


class ReservationTests(unittest.TestCase):

    def setUp(self):
        self.start_time = time.time()

    def tearDown(self):
        # WARNING! deletes data in mongodb
        app.delete('/labs')
        app.delete('/reservations')
        app.delete('/states')
        t = time.time() - self.start_time
        print " %.3f: %s" % (t,self.id())

    def test_reservation_creation_creates_cross_reference_to_lab_object(self):
        lab_uid = _post_lab("testlab_reservation")
        three_hours_from_now = datetime.now() + timedelta(hours=3)
        print "YYY: '" , three_hours_from_now , "'"
        test_data = {"lab": lab_uid,
                     "expireAt": "Tue, 02 Apr 2013 10:29:13 GMT",
                     "username": "tester"}
        data = json.dumps(test_data)
        headers = {'Content-Type': "application/json"}
        # http://flask.pocoo.org/docs/0.12/api/#response-objects
        response = app.post('/reservations', data=data, headers=headers)
        print "Reservations_rsp:",response.data
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        reservation_uid = response_data['_id']
        retL = _get_lab(lab_uid)
        self.assertIn(reservation_uid, retL[2]["reservation"])

    def test_3_reservation_creation_creates_cross_reference_to_lab_object(self):
        lab_uid1 = _post_lab("testlab_reservation_1")
        lab_uid2 = _post_lab("testlab_reservation_2")
        lab_uid3 = _post_lab("testlab_reservation_3")
        three_hours_from_now = datetime.now() + timedelta(hours=3)
        print "YYY: '" , three_hours_from_now , "'"
        test_data = [{"lab": lab_uid1,
                     "expireAt": "Tue, 02 Apr 2013 10:29:13 GMT",
                      "username": "tester"},{"lab": lab_uid2,
                     "expireAt": "Tue, 02 Apr 2013 10:29:13 GMT",
                     "username": "tester"},{"lab": lab_uid3,                                          "expireAt": "Tue, 02 Apr 2013 10:29:13 GMT",
                     "username": "tester"}]
        data = json.dumps(test_data)
        headers = {'Content-Type': "application/json"}
        # http://flask.pocoo.org/docs/0.12/api/#response-objects
        response = app.post('/reservations', data=data, headers=headers)
        print "Reservations_rsp:",response.data
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        # Check Reservation_1
        state_uid1 = response_data['_items'][0]['_id']
        retL1 = _get_lab(lab_uid1)
        self.assertIn(state_uid1, retL1[2]["reservation"])
        # Check Reservation_2
        state_uid2 = response_data['_items'][1]['_id']
        retL2 = _get_lab(lab_uid2)
        self.assertIn(state_uid2, retL2[2]["reservation"])
        # Check Reservation_3
        state_uid3 = response_data['_items'][2]['_id']
        retL3 = _get_lab(lab_uid3)
        self.assertIn(state_uid3, retL3[2]["reservation"])

    def test_reservation_removal_removes_cross_reference_from_lab_object(self):
        lab_uid = _post_lab("testlab_reservation")
        test_data = {"lab": lab_uid,
                     "username": "tester"}
        data = json.dumps(test_data)
        headers = {'Content-Type': "application/json"}
        response = app.post('/reservations', data=data, headers=headers)
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        reservation_uid = response_data['_id']
        reservation_etag = response_data['_etag']
        retL = _get_lab(lab_uid)
        self.assertIn(reservation_uid, retL[2]["reservation"])
        headers.update({"If-Match": reservation_etag})
        response = app.delete('reservations/{}'.format(reservation_uid), headers=headers)
        self.assertEqual(response.status_code, 204)
        retL = _get_lab(lab_uid)
        self.assertIsNone(retL[2].get("reservation"))

    def test_reservation_removal_is_not_possible_if_lab_is_not_in_final_state(self):
        lab_uid = _post_lab("testlab_reservation", extra_fields={"status": "preserving_state"})
        test_data = {"lab": lab_uid,
                     "username": "tester"}
        data = json.dumps(test_data)
        headers = {'Content-Type': "application/json"}
        response = app.post('/reservations', data=data, headers=headers)
        self.assertEqual(response.status_code, 201)
        reservation_data = json.loads(response.data)
        reservation_uid = reservation_data['_id']
        reservation_etag = reservation_data['_etag']
        retL = _get_lab(lab_uid)
        self.assertIn(reservation_uid, retL[2]["reservation"])
        headers.update({"If-Match": reservation_etag})
        response = app.delete('reservations/{}'.format(reservation_uid), headers=headers)
        self.assertEqual(response.status_code, 422)
        retL = _get_lab(lab_uid)
        self.assertIn(reservation_uid, retL[2]["reservation"])
        response = app.delete('reservations/{}?force'.format(reservation_uid), headers=headers)  # can be done using the force
        self.assertEqual(response.status_code, 204)
        retL = _get_lab(lab_uid)
        self.assertIsNone(retL[2]["reservation"])

    def test_bug_reservation_batch_removal_trailing_slash_error(self):
        lab_uid = _post_lab("testlab_reservation")
        test_data = {"lab": lab_uid,
                     "username": "tester"}
        data = json.dumps(test_data)
        headers = {'Content-Type': "application/json"}
        response = app.post('/reservations', data=data, headers=headers)
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        reservation_uid = response_data['_id']
        reservation_etag = response_data['_etag']
        retL = _get_lab(lab_uid)
        self.assertIn(reservation_uid, retL[2]["reservation"])
        headers.update({"If-Match": reservation_etag})
        response = app.delete('reservations/', headers=headers)
        self.assertEqual(response.status_code, 204)
        status_code, _, _ = _get_reservation(reservation_uid)
        self.assertEqual(status_code, 404)


class LabrequestTests(unittest.TestCase):

    def setUp(self):
        self.start_time = time.time()

    def tearDown(self):
        # WARNING! deletes data in mongodb
        app.delete('/labrequests')
        app.delete('/states')
        app.delete('/labs')
        t = time.time() - self.start_time
        print " %.3f: %s" % (t,self.id())

    def test_labrequest_creation(self):
        expected_initial_status = "pending"
        expected_expiry_time = _datetime_to_rfc1123(datetime.now() + timedelta(minutes=1))
        data = {'state_search_query': '{"build.id": "netact"}',
                'username': 'testuser'}
        _id = _post_resource('labrequests', data)
        result = _get_item('labrequests', _id)
        self.assertEqual(result.get('status'), expected_initial_status)
        self.assertEqual(result.get('expireAt'), expected_expiry_time)

    def test_labrequest_expiration(self):
        expected_initial_status = "pending"
        expected_expiry_time = _datetime_to_rfc1123(datetime.now() + timedelta(minutes=1))
        data = {'state_search_query': '{"build.id": "netact"}',
                'username': 'testuser'}
        _id = _post_resource('labrequests', data)
        result = _get_item('labrequests', _id)
        self.assertEqual(result.get('status'), expected_initial_status)
        self.assertEqual(result.get('expireAt'), expected_expiry_time)
        # documents with expireAt will be automatically deleted by mongodb within ~60 seconds from expiry date
        # below will take 2 minutes and only works if Eve is properly initialized -> mongodb indexes created, doesn't work with flask test app
        # time.sleep(120)
        # with self.assertRaises(RuntimeError):
        #    _get_item('labrequests', _id)

    def test_labrequest_expiry_time_is_readonly(self):
        data = {'state_search_query': '{"build.id": "netact"}',
                'username': 'testuser',
                'expireAt': "test"}
        data = json.dumps(data)
        headers = {'Content-Type': "application/json"}
        response = app.post('/{}'.format('labrequests'), data=data, headers=headers)
        self.assertNotEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['_issues'], {"expireAt": "field is read-only"})

    @patch('labrequest_tasks.process_labrequests.delay')
    def test_labrequest_keepalive(self, mock_labrequest_tasks_process_labrequests):
        # create labrequest
        labrequest_id = _post_resource('labrequests', {"username": "mikko", "state_search_query": "build.id==none"})
        labrequest_data = _get_item('labrequests', labrequest_id)
        orig_etag = labrequest_data['_etag']
        # update labrequest using keepalive endpoint
        headers = {'Content-Type': "application/json"}
        response = app.patch('/labrequests/{0}/keepalive'.format(labrequest_id), headers=headers)
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['_id'], labrequest_id)
        self.assertEqual(response_data['_status'], "OK")
        self.assertNotEqual(response_data['_etag'], orig_etag)
        labrequest_updated_data = _get_item('labrequests', labrequest_id)
        self.assertEqual(labrequest_updated_data['_etag'], response_data['_etag'])
        mock_labrequest_tasks_process_labrequests.assert_called()

    @patch('labrequest_tasks.process_labrequests.delay')
    def test_labrequest_keepalive_failure_not_existing_request(self, mock_labrequest_tasks_process_labrequests):
        # create labrequest
        labrequest_id = "fake"
        # update labrequest using keepalive endpoint
        headers = {'Content-Type': "application/json"}
        response = app.patch('/labrequests/{0}/keepalive'.format(labrequest_id), headers=headers)
        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_data['_status'], "ERR")
        mock_labrequest_tasks_process_labrequests.assert_called()


def _post_resource(resource_name, data):
    """Creates resource, returns its _id"""
    data = json.dumps(data)
    headers = {'Content-Type': "application/json"}
    response = app.post('/{}'.format(resource_name), data=data, headers=headers)
    if response.status_code == 201:
        response_data = json.loads(response.data)
        _id = response_data['_id']
    else:
        raise RuntimeError("Resource creation failed due to {}".format(response.data))
    return _id


def _patch_resource(resource_name, item_id, etag, data):
    """Updates resource"""
    data = json.dumps(data)
    headers = {'Content-Type': "application/json", "If-Match": etag}
    response = app.patch('/{}/{}'.format(resource_name, item_id), data=data, headers=headers)
    if response.status_code < 400:
        response_data = json.loads(response.data)
        _id = response_data['_id']
    else:
        raise RuntimeError("Resource creation failed due to {}".format(response.data))
    return _id


def _get_item(resource_name, _id):
    """Reads item by given its resource and _id"""
    headers = {'Content-Type': "application/json"}
    response = app.get('/{}/{}'.format(resource_name, _id), headers=headers)
    if response.status_code == 200:
        response_data = json.loads(response.data)
    else:
        raise RuntimeError("Getting item failed due to {}".format(response.data))
    return response_data


def _print_rets(txt, rets):
    print txt
    i = 0
    txt_sub = ""
    ret = 0
    for ret in rets:
        txt_sub = "Index-%d:" % i
        i += 1
    _print_ret(txt_sub, ret)


def _print_ret(txt, ret):
    tada = ""
    formi = " (status,lab_name,resu): [%-5.5d] [%s]   [%s]\n"
    tada += formi % (ret[0], ret[1], ret[2])
    print txt + tada


def _get_state(state_uid):
    get_response = app.get('/states/' + state_uid)
    status = get_response.status_code
    get_response_data = json.loads(get_response.data)
    return status, state_uid, get_response_data


def _get_lab(lab_uid):
    get_response = app.get('/labs/' + lab_uid)
    status = get_response.status_code
    get_response_data = json.loads(get_response.data)
    return status, lab_uid, get_response_data


def _get_reservation(reservation_uid):
    get_response = app.get('/reservations/' + reservation_uid)
    status = get_response.status_code
    get_response_data = json.loads(get_response.data)
    return status, reservation_uid, get_response_data


def _post_lab(name, extra_fields=None):
    """Creates a lab of given name, returns _id"""
    test_data = {"lab_name": name, "status": "ready"}
    if extra_fields:
        test_data.update(extra_fields)
    data = json.dumps(test_data)
    headers = {'Content-Type': "application/json"}
    response = app.post('/labs', data=data, headers=headers)
    response_data = json.loads(response.data)
    lab_uid = response_data['_id']
    return lab_uid


def _delete_lab(labid):
    _, _, labdata = _get_lab(labid)
    lab_etag = labdata['_etag']
    headers = {"If-Match": lab_etag}
    response = app.delete('labs/{}'.format(labid), headers=headers)
    return response


def _datetime_to_rfc1123(dt):
    stamp = time.mktime(dt.timetuple())
    return format_date_time(stamp)

if __name__ == '__main__':
    unittest.main()
