import unittest
import labrequest_tasks
import logging
import requests
import time
import datetime
import os
import json
from mock import patch, Mock
import threading
from test_utils import test_data

# NOTE! prerequisite is test server
STATE_REST_API_URL = "http://localhost:8000"
labrequest_tasks.STATE_REST_API_URL = "http://localhost:8000"

logging.basicConfig(level=logging.DEBUG)

try:
    del os.environ['HTTP_PROXY']
    del os.environ['http_proxy']
except:
    pass


class LabrequestTasksTests(unittest.TestCase):

    def tearDown(self):
        pass

    def setUp(self):
        self._drop_collections()

    def _drop_collections(self):
        requests.delete("{}/{}".format(STATE_REST_API_URL, 'labrequests'))
        requests.delete("{}/{}".format(STATE_REST_API_URL, 'labs'))
        requests.delete("{}/{}".format(STATE_REST_API_URL, 'states'))
        requests.delete("{}/{}".format(STATE_REST_API_URL, 'reservations'))

    def test_get_sorted_labrequests(self):
        usernames = ["eka", "toka", "kolmas"]
        for username in usernames:
            url = "{}/{}".format(STATE_REST_API_URL, 'labrequests')
            data = {'username': username,
                    'state_search_query': '{"build.id": "netact"}'}
            response = requests.post(url, data=data)
            response.raise_for_status()
            time.sleep(1)
        labrequests = labrequest_tasks._get_open_labrequests()
        for i, labrequest in enumerate(labrequests):
            self.assertEqual(labrequest['username'], usernames[i])

    def test_patch(self):
        url = "{}/{}".format(STATE_REST_API_URL, 'labrequests')
        data = {'username': "test",
                'state_search_query': '{"build.id": "netact"}'}
        response = requests.post(url, json=data)
        response.raise_for_status()
        labrequest_id = response.json()['_id']
        labrequest_data = test_data.get_item('labrequests', labrequest_id)
        etag = labrequest_data['_etag']
        data = {'username': "test-2"}
        labrequest_tasks._patch_item('labrequests', labrequest_id, data, etag)
        labrequest_updated_data = test_data.get_item('labrequests', labrequest_id)
        self.assertEqual(labrequest_updated_data['username'], "test-2")

    @patch('labrequest_tasks.LabrequestProcessor')
    def test_process_labrequests_process_all_even_if_failures(self, mockLabrequestProcessor):
        mockLabrequestProcessor.side_effect = [Exception, Mock(), Exception, RuntimeError]
        test_data.post_labrequest("mikko", "{{\"build.id\": \"{0}\"}}".format("dsa"))
        test_data.post_labrequest("mikko", "{{\"build.id\": \"{0}\"}}".format("dsa"))
        test_data.post_labrequest("mikko", "{{\"build.id\": \"{0}\"}}".format("dsa"))
        test_data.post_labrequest("mikko", "{{\"build.id\": \"{0}\"}}".format("dsa"))
        labrequest_tasks.process_labrequests()
        self.assertEqual(mockLabrequestProcessor.call_count, 4)

    def test_process_labrequests(self):
        expected_lab = ("testlab", "sprint", "netact-3", False)
        testlabs = [("testlab-1", "sprint", "netact-5", False),
                    ("testlab2", "sprint", "netact-2", False),
                    ("testlab-2", "sprint", "netact-2", False),
                    expected_lab,
                    ("2", "sprint", "netact-2", False),
                    ("lab-2", "sprint", "netact-2", False),
                    ("testlab-3", "cloud", "netact-1", False)]
        test_data.test_setup(testlabs, lab_status="ready")
        labs = test_data.get_resources('labs')['_items']
        expected_lab_ids = [lab['_id'] for lab in labs if lab['lab_name'] == expected_lab[0]]
        self.assertEqual(len(expected_lab_ids), 1)
        expected_lab_id = expected_lab_ids.pop()
        labrequest_response = test_data.post_labrequest("mikko", "{{\"build.id\": \"{0}\"}}".format(expected_lab[2]))
        labrequest_id = labrequest_response['_id']
        labrequest_data = test_data.get_resources('labrequests')['_items'][0]
        self.assertIsNone(labrequest_data.get('lab'))
        self.assertEqual(labrequest_data['username'], "mikko")
        self.assertEqual(labrequest_data['status'], "pending")
        labrequest_tasks.process_labrequests()
        labrequest_processed_data = test_data.get_item('labrequests', labrequest_id)
        self.assertEqual(labrequest_processed_data['lab'], expected_lab_id)
        self.assertEqual(labrequest_processed_data['username'], "mikko")
        my_lab = test_data.get_item('labs', expected_lab_id)
        my_reservation = test_data.get_item('reservations', my_lab['reservation'])
        self.assertEqual(my_reservation['username'], "mikko")
        self.assertEqual(my_reservation['username'], "mikko")
        self.assertEqual(labrequest_processed_data['status'], "ready")

    def test_process_labrequests_lifecycle_bug(self):
        expected_lab = ("testlab", "sprint", "netact-3", False)
        testlabs = [("testlab-1", "sprint", "netact-5", False),
                    ("testlab2", "sprint", "netact-2", False),
                    ("testlab-2", "sprint", "netact-2", False),
                    expected_lab,
                    ("2", "sprint", "netact-2", False),
                    ("lab-2", "sprint", "netact-2", False),
                    ("testlab-3", "cloud", "netact-1", False)]
        test_data.test_setup(testlabs, lab_status="ready")
        labs = test_data.get_resources('labs')['_items']
        expected_lab_ids = [lab['_id'] for lab in labs if lab['lab_name'] == expected_lab[0]]
        self.assertEqual(len(expected_lab_ids), 1)
        expected_lab_id = expected_lab_ids.pop()
        labrequest_response = test_data.post_labrequest("mikko", "{{\"build.id\": \"{0}\"}}".format(expected_lab[2]))
        labrequest_id = labrequest_response['_id']
        labrequest_data = test_data.get_resources('labrequests')['_items'][0]
        self.assertIsNone(labrequest_data.get('lab'))
        self.assertEqual(labrequest_data['username'], "mikko")
        self.assertEqual(labrequest_data['status'], "pending")
        labrequest_tasks.process_labrequests()
        labrequest_processed_data = test_data.get_item('labrequests', labrequest_id)
        self.assertEqual(labrequest_processed_data['lab'], expected_lab_id)
        self.assertEqual(labrequest_processed_data['username'], "mikko")
        my_lab = test_data.get_item('labs', expected_lab_id)
        my_reservation = test_data.get_item('reservations', my_lab['reservation'])
        self.assertEqual(my_reservation['username'], "mikko")
        self.assertEqual(my_reservation['username'], "mikko")
        self.assertEqual(labrequest_processed_data['status'], "ready")
        self.assertEqual(my_lab.get('status'), "queued_for_revert")
        _mock_snapshot_revert_task(my_lab['_id'])
        response = test_data.delete_item('reservations', my_reservation['_id'], force=True)
        self.assertEqual(response.status_code, 204)
        labrequest_response = test_data.post_labrequest("mikko", "{{\"build.id\": \"{0}\"}}".format(expected_lab[2]))
        labrequest_id = labrequest_response['_id']
        labrequest_data = test_data.get_item('labrequests', labrequest_id)
        self.assertIsNone(labrequest_data.get('lab'))
        self.assertEqual(labrequest_data['username'], "mikko")
        self.assertEqual(labrequest_data['status'], "pending")
        labrequest_tasks.process_labrequests()
        labrequest_processed_data = test_data.get_item('labrequests', labrequest_id)
        self.assertEqual(labrequest_processed_data['lab'], expected_lab_id)
        self.assertEqual(labrequest_processed_data['username'], "mikko")
        my_lab = test_data.get_item('labs', expected_lab_id)
        my_reservation = test_data.get_item('reservations', my_lab['reservation'])
        self.assertEqual(my_reservation['username'], "mikko")
        self.assertEqual(my_reservation['username'], "mikko")
        self.assertEqual(labrequest_processed_data['status'], "ready")

    def test_process_labrequest_successful_reservation(self):
        reservation = self._exec_test_process_labrequest_successful_reservation()
        logging.info('Reservation: %s', reservation)
        tag = reservation.get('tag')
        self.assertIsNone(tag, 'Tag for reservation was %s, but was expected to be None' % (tag))

    def test_process_labrequest_successful_reservation_with_tag(self):
        expected_tag = 'Guten Tag!'
        reservation = self._exec_test_process_labrequest_successful_reservation(tag = expected_tag)
        tag = reservation.get('tag')
        self.assertEqual(expected_tag , tag, 'Tag for reservation was %s, but %s was expected' % (tag, expected_tag))

    def test_process_labrequest_successful_reservation_repeated_reservation_with_same_tag(self):
        expected_tag = 'Guten Tag!'
        reservation, reservation2 =\
            self._exec_test_process_labrequest_successful_reservation_repeated_reservation_with_tag(expected_tag, expected_tag)
        self.assertEqual(reservation, reservation2, 'same reservation expected for same tag')

    def test_process_labrequest_successful_reservation_repeated_reservation_with_another_tag(self):
        a_tag = 'Guten Tag!'
        yet_another_tag = 'Guten Abend!'
        reservation, reservation2 =\
            self._exec_test_process_labrequest_successful_reservation_repeated_reservation_with_tag(a_tag, yet_another_tag)
        self.assertIsNone(reservation2, 'Reservation with another tag should not succeed')

    def _exec_test_process_labrequest_successful_reservation_repeated_reservation_with_tag(self, tag1, tag2):
        reservation = self._exec_test_process_labrequest_successful_reservation(tag = tag1)
        tag = reservation.get('tag')
        self.assertEqual(tag1, tag, 'Tag for reservation was %s, but %s was expected' % (tag, tag1))

        query = json.dumps({'build.id': 'netact-3'})
        try:
            reservation2 = self._do_reserve_lab("mikko", query, expected_state='ready', tag = tag2)
        except:
            reservation2 = None
        logging.info('Reservation #1: %s', reservation)
        logging.info('Reservation #2: %s', reservation2)
        return reservation, reservation2

    def _exec_test_process_labrequest_successful_reservation(self, **more_labrequest_settings):
        expected_lab = ("testlab", "sprint", "netact-3", False)
        testlabs = [("testlab-1", "sprint", "netact-5", False),
                    ("testlab2", "sprint", "netact-2", False),
                    ("testlab-2", "sprint", "netact-2", False),
                    expected_lab,
                    ("2", "sprint", "netact-2", False),
                    ("lab-2", "sprint", "netact-2", False),
                    ("testlab-3", "cloud", "netact-1", False)]
        test_data.test_setup(testlabs, lab_status="ready")

        query = json.dumps({'build.id': expected_lab[2]})
        reservation = self._do_reserve_lab("mikko", query, expected_state='ready', **more_labrequest_settings)
        return reservation

    def test_process_labrequest_no_lab_available_all_reserved(self):
        testlabs = [("testlab-1", "sprint", "netact-5", True),
                    ("lab-2", "sprint", "netact-2", True),
                    ("testlab-3", "cloud", "netact-1", True)]
        test_data.test_setup(testlabs)
        labrequest_response = test_data.post_labrequest("mikko", "{{\"build.id\": \"{0}\"}}".format("netact-1"))
        labrequest_id = labrequest_response['_id']
        labrequest_data = test_data.get_item('labrequests', labrequest_id)
        self.assertIsNone(labrequest_data.get('lab'))
        self.assertEqual(labrequest_data['username'], "mikko")
        self.assertEqual(labrequest_data['status'], "pending")
        labrequest_tasks.LabrequestProcessor(labrequest_data).process_labrequest()
        labrequest_processed_data = test_data.get_item('labrequests', labrequest_id)
        self.assertIsNone(labrequest_data.get('lab'))
        self.assertEqual(labrequest_processed_data['username'], "mikko")
        self.assertEqual(labrequest_processed_data['status'], "no_lab_available")

    def test_process_labrequest_no_lab_available_no_final_state(self):
        testlabs = [("testlab-1", "sprint", "netact-5", False),
                    ("lab-2", "sprint", "netact-2", False),
                    ("testlab-3", "cloud", "netact-1", False)]
        test_data.test_setup(testlabs, lab_status="reverting_state")
        labrequest_response = test_data.post_labrequest("mikko", "{{\"build.id\": \"{0}\"}}".format("netact-1"))
        labrequest_id = labrequest_response['_id']
        labrequest_data = test_data.get_item('labrequests', labrequest_id)
        self.assertIsNone(labrequest_data.get('lab'))
        self.assertEqual(labrequest_data['username'], "mikko")
        self.assertEqual(labrequest_data['status'], "pending")
        labrequest_tasks.LabrequestProcessor(labrequest_data).process_labrequest()
        labrequest_processed_data = test_data.get_item('labrequests', labrequest_id)
        self.assertIsNone(labrequest_data.get('lab'))
        self.assertEqual(labrequest_processed_data['username'], "mikko")
        self.assertEqual(labrequest_processed_data['status'], "no_lab_available")

    def test_process_labrequest_no_matching_state(self):
        testlabs = [("testlab-1", "sprint", "netact-5", True),
                    ("lab-2", "sprint", "netact-2", True),
                    ("testlab-3", "cloud", "netact-1", True)]
        test_data.test_setup(testlabs)
        labrequest_response = test_data.post_labrequest("mikko", "{{\"build.id\": \"{0}\"}}".format("this_shall_not_match"))
        labrequest_id = labrequest_response['_id']
        labrequest_data = test_data.get_item('labrequests', labrequest_id)
        self.assertIsNone(labrequest_data.get('lab'))
        self.assertEqual(labrequest_data['username'], "mikko")
        self.assertEqual(labrequest_data['status'], "pending")
        labrequest_tasks.LabrequestProcessor(labrequest_data).process_labrequest()
        labrequest_processed_data = test_data.get_item('labrequests', labrequest_id)
        self.assertIsNone(labrequest_data.get('lab'))
        self.assertEqual(labrequest_processed_data['username'], "mikko")
        self.assertEqual(labrequest_processed_data['status'], "no_matching_state")

    def test_process_labrequest_no_matching_lab(self):
        testlabs = [("testlab-1", "sprint", "netact-5", True),
                    ("lab-2", "sprint", "netact-2", True),
                    ("testlab-3", "cloud", "netact-1", True)]
        test_data.test_setup(testlabs)
        labrequest_response = test_data.post_labrequest("mikko",
                                               "{{\"build.id\": \"{0}\"}}".format("netact-1"),
                                                        lab_search_query="lab_type==sprint")
        labrequest_id = labrequest_response['_id']
        labrequest_data = test_data.get_item('labrequests', labrequest_id)
        self.assertIsNone(labrequest_data.get('lab'))
        self.assertEqual(labrequest_data['username'], "mikko")
        self.assertEqual(labrequest_data['status'], "pending")
        labrequest_tasks.LabrequestProcessor(labrequest_data).process_labrequest()
        labrequest_processed_data = test_data.get_item('labrequests', labrequest_id)
        self.assertIsNone(labrequest_data.get('lab'))
        self.assertEqual(labrequest_processed_data['username'], "mikko")
        self.assertEqual(labrequest_processed_data['status'], "no_matching_state")

    def test_process_labrequest_set_duration_to_date(self):
        duration = 3600 * 2

        expireAt = datetime.datetime.strftime(
            (datetime.datetime.utcnow() + datetime.timedelta(days=1)),
            '%a, %d %b %Y %H:%M:%S GMT')
        expireAt_org_expected = datetime.datetime.strftime(
            (datetime.datetime.utcnow() + datetime.timedelta(seconds=duration)),
            '%a, %d %b %Y %H:%M:%S GMT')

        # 1st step: reserve lab and get reservation
        reservation = self._test_process_labrequest_extend_duration_setup(duration)
        expireAt_org = reservation.get('expireAt')
        duration_org = reservation.get('duration')
        # time wrongly set at reservation?
        self.assertEqual(expireAt_org, expireAt_org_expected)
        self.assertEqual(int(duration_org), duration)

        # 2nd step set expireAt
        reservation_updated, expireAt_updated, duration_updated =\
            self._do_set_expire_at(reservation, expireAt)
        # time wrongly set?
        self.assertEqual(expireAt_updated, expireAt)
        ##self.assertEqual(int(duration_updated), 86400)

        # 3rd step set expireAt again to old time
        reservation_updated2, expireAt_updated2, duration_updated2 =\
            self._do_set_expire_at(reservation_updated, expireAt_org)

        logging.info('reservation(org): expireAt=%s duration=%s', expireAt_org, duration_org)
        logging.info('expireAt=%s', expireAt)
        logging.info('reservation_updated: expireAt=%s duration=%s', expireAt_updated, duration_updated)
        logging.info('reservation_updated2: expireAt=%s duration=%s', expireAt_updated2, duration_updated2)
        self.assertEqual(expireAt_org, expireAt_updated2, 'expireAt should be re-stored to org. value')
        ##self.assertEqual(duration_org, duration_updated2, 
        ##    'duration should be re-stored to org. value: %s != %s' % (duration_org, duration_updated2))

    def test_process_labrequest_extend_duration(self):
        duration = 757
        duration2 = 999
        self._exec_test_process_labrequest_extend_duration(duration, duration2)

    def test_process_labrequest_extend_duration_by_adding_and_subtracting(self):
        duration = 639
        duration_diff = 100
        self._exec_test_process_labrequest_extend_duration(duration, duration_diff, add_and_subtract = True)

    def _exec_test_process_labrequest_extend_duration(self, duration, duration2=None, add_and_subtract = False):
        ''' execute testcases for duration value change 
            param: duration             first duration to be set during reservation
            param: duration2            second first duration to be set, or value to be added and then subtracted
            param: add_and_subtract     if True, duration added and then subtracted
        '''
        # 1st step: reserve lab and get reservation
        reservation = self._test_process_labrequest_extend_duration_setup(duration)

        # 2nd step: extend the duration
        reservation_updated = self._do_set_duration(reservation, duration2, add_and_subtract)

        # 3rd step: set duration back and check expiration date is same as before
        if add_and_subtract:
            reservation_updated_2 = self._do_set_duration(reservation_updated, -duration2, add_and_subtract)
        else:
            reservation_updated_2 = self._do_set_duration(reservation_updated, duration, add_and_subtract)

        self.assertEqual(reservation.get('expireAt'), reservation_updated_2.get('expireAt'))

    def _test_process_labrequest_extend_duration_setup(self, duration):
        ''' setup some labs and reserve one of them '''
        test_data.test_setup([
            ("testlab-1", "sprint", "netact-5", False),
            ("testlab-2", "sprint", "netact-5", False),
            ("testlab-3", "sprint", "netact-7", False),
        ])
        return self._do_reserve_lab('X', '{"build.id": "netact-7"}', message='test_process_labrequest_extend_duration',
                    expected_state='ready',
                    duration=str(duration))

    def _do_reserve_lab(self, user, query, message=None, expected_state='ready', expected_lab_is_None=False, expected_lab=None, **kwargs):
        # 1st step: reserve lab
        lab_id = self._do_lab_request(user, query, message, 
            expected_state='ready',
            **kwargs)
        logging.info('reserved lab_id=%s', lab_id)
        
        # 2nd step: get reservation
        reservations = test_data.get_resources('reservations')['_items']                             
        self.assertEqual(len(reservations), 1)
        reservation = reservations[0]
        self.assertEqual(lab_id, reservation.get('lab'), 'lab w/ id %s expected to be reserved' % reservation.get('lab'))
        return reservation

    def _do_set_expire_at(self, reservation, expireAt):
        response = test_data.patch_item('reservations', reservation['_id'],
                                        {'expireAt': expireAt})
        logging.info('response: %s', response)
        reservation_updated = test_data.get_item('reservations', reservation['_id'])
        self.assertNotEqual(reservation, reservation_updated)
        return reservation_updated, reservation_updated.get('expireAt'), reservation_updated.get('duration')

    def _do_set_duration(self, reservation, duration, add_and_subtract):
        duration_string = ('+' if add_and_subtract and duration >= 0 else '') + str(duration)
        duration0 = int(reservation.get('duration'))
        response = test_data.patch_item('reservations', reservation['_id'], {'duration': duration_string})
        logging.info('response: %s', response)
        reservation_updated = test_data.get_item('reservations', reservation['_id'])
        self.assertNotEqual(reservation, reservation_updated)
        logging.debug('reservation:\n\t%s\nreservation_updated:\n\t%s', reservation, reservation_updated)
        if add_and_subtract:
            expected_duration = duration + duration0
            self.assertEqual(float(expected_duration), float(reservation_updated.get('duration')), 'expected duration %u but is %s' % (expected_duration, reservation_updated.get('duration')))
        else:
            self.assertEqual(float(duration), float(reservation_updated.get('duration')), 'duration was set to %u but is %s' % (duration, reservation_updated.get('duration')))
        return reservation_updated

    def _do_lab_request(self, user, query, message, expected_state='ready', expected_lab_is_None=False, expected_lab=None, **kwargs):
        ''' create & execute labrequest and checks results'''
        response = test_data.post_labrequest(user, query, **kwargs)

        labrequest = test_data.get_item('labrequests', response['_id'])
        # state of fresh request is 'pending'
        self.assertEqual(labrequest.get('username'), user)
        self.assertEqual(labrequest.get('status'), 'pending')
        self.assertIsNone(labrequest.get('lab'))

        labrequest_tasks.LabrequestProcessor(labrequest).process_labrequest()
        labrequest = test_data.get_item('labrequests', response['_id'])
        logging.info('labrequest: %s', labrequest)
        self.assertEqual(labrequest.get('username'), user)
        self.assertEqual(labrequest.get('status'), expected_state)
        if expected_lab_is_None:
            self.assertIsNone(labrequest.get('lab'))
        else:
            self.assertIsNotNone(labrequest.get('lab'))
        return labrequest.get('lab')

    def test_process_labrequests_concurrency_problem(self):
        # It's possible that labrequest processing and keepalive are both updating labrequest at the same time.
        # Both are now supporting retry in case of etag mismatch that seems to help and should tackle all meaningful scenarios.
        # i.e. where keepalive is called by one client once per second etc.
        #
        # There's still some problem that causes labrequest processing to add a lab even when the request itself seems to be successful.
        # To reproduce, increase the number of keepalive_threads.
        expected_lab = ("testlab", "sprint", "netact-3", False)
        testlabs = [("testlab-1", "sprint", "netact-5", False),
                    ("testlab2", "sprint", "netact-2", False),
                    ("testlab-2", "sprint", "netact-2", False),
                    expected_lab,
                    ("2", "sprint", "netact-2", False),
                    ("lab-2", "sprint", "netact-2", False),
                    ("testlab-3", "cloud", "netact-1", False)]
        test_data.test_setup(testlabs, lab_status="ready")
        labs = test_data.get_resources('labs')['_items']
        expected_lab_ids = [lab['_id'] for lab in labs if lab['lab_name'] == expected_lab[0]]
        self.assertEqual(len(expected_lab_ids), 1)
        expected_lab_id = expected_lab_ids.pop()
        labrequest_response = test_data.post_labrequest("mikko", "{{\"build.id\": \"{0}\"}}".format(expected_lab[2]))
        labrequest_id = labrequest_response['_id']
        labrequest_data = test_data.get_resources('labrequests')['_items'][0]
        self.assertIsNone(labrequest_data.get('lab'))
        self.assertEqual(labrequest_data['username'], "mikko")
        self.assertEqual(labrequest_data['status'], "pending")

        def _process():
            labrequest_tasks.process_labrequests()

        def _keepalive():
            requests.patch("{}/{}/{}/keepalive".format(STATE_REST_API_URL, 'labrequests', labrequest_id))

        process = threading.Thread(target=_process)
        keepalive_threads = []
        for i in xrange(1, 10):
            keepalive_threads.append(threading.Thread(target=_keepalive))
        process.start()
        for thread in keepalive_threads:
            thread.start()
        process.join()
        for thread in keepalive_threads:
            thread.join()
        labrequest_processed_data = test_data.get_item('labrequests', labrequest_id)
        self.assertEqual(labrequest_processed_data['lab'], expected_lab_id)
        self.assertEqual(labrequest_processed_data['username'], "mikko")
        my_lab = test_data.get_item('labs', expected_lab_id)
        my_reservation = test_data.get_item('reservations', my_lab['reservation'])
        self.assertEqual(my_reservation['username'], "mikko")
        self.assertEqual(my_reservation['username'], "mikko")
        self.assertEqual(labrequest_processed_data['status'], "ready")

    def test_process_labrequest_match_only_available_snapshots(self):
        expected_lab = ("testlab", "sprint", "netact-3", False)
        testlabs = [("testlab-1", "sprint", "netact-5", False),
                    ("testlab2", "sprint", "netact-2", False),
                    ("testlab-2", "sprint", "netact-2", False),
                    expected_lab,
                    ("2", "sprint", "netact-2", False),
                    ("lab-2", "sprint", "netact-2", False),
                    ("testlab-3", "cloud", "netact-1", False)]
        test_data.test_setup(testlabs, snapshots_status="failed")
        labs = test_data.get_resources('labs')['_items']
        expected_lab_ids = [lab['_id'] for lab in labs if lab['lab_name'] == expected_lab[0]]
        self.assertEqual(len(expected_lab_ids), 1)
        labrequest_response = test_data.post_labrequest("mikko", "{{\"build.id\": \"{0}\"}}".format(expected_lab[2]))
        labrequest_id = labrequest_response['_id']
        labrequest_data = test_data.get_item('labrequests', labrequest_id)
        self.assertIsNone(labrequest_data.get('lab'))
        self.assertEqual(labrequest_data['username'], "mikko")
        self.assertEqual(labrequest_data['status'], "pending")
        labrequest_tasks.LabrequestProcessor(labrequest_data).process_labrequest()
        labrequest_processed_data = test_data.get_item('labrequests', labrequest_id)
        self.assertEqual(labrequest_processed_data.get('status'), "no_lab_available")
        self.assertIsNone(labrequest_processed_data.get('lab'))

    def test_process_labrequest_lab_state_shall_not_be_ready_before_snapshot_task_picks_it_up(self):
        expected_lab = ("testlab", "sprint", "netact-3", False)
        testlabs = [("testlab-1", "sprint", "netact-5", False),
                    ("testlab2", "sprint", "netact-2", False),
                    ("testlab-2", "sprint", "netact-2", False),
                    expected_lab,
                    ("2", "sprint", "netact-2", False),
                    ("lab-2", "sprint", "netact-2", False),
                    ("testlab-3", "cloud", "netact-1", False)]
        test_data.test_setup(testlabs, lab_status="ready")
        labs = test_data.get_resources('labs')['_items']
        expected_lab_ids = [lab['_id'] for lab in labs if lab['lab_name'] == expected_lab[0]]
        self.assertEqual(len(expected_lab_ids), 1)
        expected_lab_id = expected_lab_ids.pop()
        labrequest_response = test_data.post_labrequest("mikko", "{{\"build.id\": \"{0}\"}}".format(expected_lab[2]))
        labrequest_id = labrequest_response['_id']
        labrequest_data = test_data.get_resources('labrequests')['_items'][0]
        self.assertIsNone(labrequest_data.get('lab'))
        self.assertEqual(labrequest_data['username'], "mikko")
        self.assertEqual(labrequest_data['status'], "pending")
        labrequest_tasks.process_labrequests()
        labrequest_processed_data = test_data.get_item('labrequests', labrequest_id)
        self.assertEqual(labrequest_processed_data['lab'], expected_lab_id)
        self.assertEqual(labrequest_processed_data['username'], "mikko")
        my_lab = test_data.get_item('labs', expected_lab_id)
        my_reservation = test_data.get_item('reservations', my_lab['reservation'])
        self.assertEqual(my_reservation['username'], "mikko")
        self.assertEqual(my_reservation['username'], "mikko")
        self.assertEqual(labrequest_processed_data['status'], "ready")
        self.assertEqual(my_lab['status'], "queued_for_revert")

    def test_get_resource_items(self):
        testlabs = [("testlab-1", "sprint", "netact-5", False),
                    ("testlab-2", "sprint", "netact-2", False),
                    ("testlab-3", "sprint", "netact-2", False),
                    ("testlab-4", "sprint", "netact-2", False),
                    ("testlab-5", "sprint", "netact-2", False),
                    ("testlab-6", "sprint", "netact-2", False),
                    ("testlab-7", "cloud", "netact-1", False)]
        test_data.test_setup(testlabs)
        items = labrequest_tasks._get_all_resource_items('labs', all_pages=True, max_results=1)
        self.assertEqual(len(items), len(testlabs))
        items = labrequest_tasks._get_all_resource_items('labs', all_pages=True)
        self.assertEqual(len(items), len(testlabs))
        items = labrequest_tasks._get_all_resource_items('labs', all_pages=False)
        self.assertEqual(len(items), len(testlabs))
        items = labrequest_tasks._get_all_resource_items('labs', all_pages=False, max_results=1)
        self.assertEqual(len(items), 1)
        items = labrequest_tasks._get_all_resource_items('labs')
        self.assertEqual(len(items), len(testlabs))
        items = labrequest_tasks._get_all_resource_items('labs', all_pages=True, max_results=2)
        self.assertEqual(len(items), len(testlabs))
        self.assertEqual(items[3]['lab_name'], "testlab-4")


def _mock_snapshot_revert_task(lab_id):
    test_data.patch_item('labs', lab_id, {"status": "reverting_state"})
    test_data.patch_item('labs', lab_id, {"status": "ready"})


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
