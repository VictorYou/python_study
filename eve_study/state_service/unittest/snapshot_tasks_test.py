import snapshot_tasks
import unittest
from httmock import urlmatch, HTTMock
from mock import patch
import json
from celery import exceptions
import os
import logging
from test_utils import test_data
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

try:
    del os.environ['HTTP_PROXY']
    del os.environ['http_proxy']
except:
    pass


class TaskTest(unittest.TestCase):

    @urlmatch(netloc=r'web')
    def mock_api(self, url, request):
        log.debug("MOCK {} {}, BODY: {}, HEADERS: {}".format(request.method, request.url, request.body, request.headers))
        if "states/not_queued_state" in request.url:
            return json.dumps({"snapshot_status" : "reverting"})
        elif "states/not_whitelisted_state" in request.url:
            return json.dumps({"snapshot_status": "queued"})
        elif "states/queued_state" in request.url:
            return json.dumps({"snapshot_status": "queued", "snapshot_id": "12334"})
        elif "states/available_state" in request.url:
            return json.dumps({"snapshot_status": "available", "snapshot_id": "12334"})
        elif "states" in request.url:
            return json.dumps({"snapshot_status": "queued", "_etag" : "123456"})
        elif "labs/free_lab" in request.url:
            return json.dumps({"lab_name": "free_lab", "_etag": "66666"})
        elif "labs/reserved_lab" in request.url:
            return json.dumps({"lab_name": "reserved_lab", "_etag": "66666", "reservation": "1212323"})
        else:
            return json.dumps({"_etag": "999999"})

    @patch('snapshot_tasks._change_lab_status')
    @patch('snapshot_tasks._take_snapshot')
    def test_take_snapshot_and_state_is_not_queued(self, mock_take_snapshot, mock_change_lab_status):
        my_lab = "reserved_lab"
        with HTTMock(self.mock_api):
            with self.assertRaises(exceptions.TaskError):
                snapshot_tasks.take_snapshot(my_lab, "not_queued_state", "etag", lab_whitelisted=True)
        mock_change_lab_status.assert_called_with(my_lab, "state_operation_failed")
        mock_take_snapshot.assert_not_called()

    @patch('snapshot_tasks._change_lab_status')
    @patch('snapshot_tasks._take_snapshot')
    def test_take_snapshot_and_lab_is_not_whitelisted(self, mock_take_snapshot, mock_change_lab_status):
        my_lab = "reserved_lab"
        with HTTMock(self.mock_api):
            with self.assertRaises(exceptions.TaskError):
                snapshot_tasks.take_snapshot(my_lab, "not_whitelisted_state", "etag", lab_whitelisted=False)
        mock_change_lab_status.assert_called_with(my_lab, "state_operation_failed")
        mock_take_snapshot.assert_not_called()

    @patch('snapshot_tasks._take_storage_snapshot')
    @patch('snapshot_tasks._get_snapshot_status')
    @patch('snapshot_tasks._change_lab_status')
    def test_take_snapshot(self, mock_change_lab_status, mock_snapshot_status, mock_take_snapshot):
        mock_snapshot_status.side_effect = ["queued", "creating"]
        mock_take_snapshot.return_value = ("some_snapshot_id", "some_event_id")
        with HTTMock(self.mock_api):
            self.assertTrue(snapshot_tasks.take_snapshot("reserved_lab", "some_state", "etag", lab_whitelisted=True))
        mock_change_lab_status.assert_called_with("reserved_lab", "ready")
        mock_take_snapshot.assert_called_with("reserved_lab")

    @patch('snapshot_tasks._take_storage_snapshot')
    @patch('snapshot_tasks._get_snapshot_status')
    @patch('snapshot_tasks._change_lab_status')
    def test_take_snapshot_and_lab_is_not_reserved(self, mock_change_lab_status, mock_snapshot_status, mock_take_snapshot):
        mock_snapshot_status.side_effect = ["queued", "creating"]
        mock_take_snapshot.return_value = ("some_snapshot_id", "some_event_id")
        with HTTMock(self.mock_api):
            with self.assertRaises(exceptions.TaskError):
                self.assertTrue(snapshot_tasks.take_snapshot("free_lab", "some_state", "etag"))
        mock_change_lab_status.assert_called_with("free_lab", "state_operation_failed")
        mock_take_snapshot.assert_not_called()

    @patch('snapshot_tasks._take_storage_snapshot')
    @patch('snapshot_tasks._get_snapshot_status')
    @patch('snapshot_tasks._change_lab_status')
    @patch('snapshot_tasks._change_state')
    def test_take_snapshot_fails(self,
                                 mock_change_state,
                                 mock_change_lab_status,
                                 mock_snapshot_status,
                                 mock_take_snapshot
                                 ):
        my_lab = "reserved_lab"
        mock_snapshot_status.side_effect = ["queued", "creating"]
        mock_take_snapshot.side_effect = [RuntimeError]
        mock_change_state.return_value = "etag"
        with HTTMock(self.mock_api):
            with self.assertRaises(RuntimeError):
                snapshot_tasks.take_snapshot(my_lab, "some_state", "etag", lab_whitelisted=True)
        mock_take_snapshot.assert_called_with(my_lab)
        mock_change_lab_status.assert_called_with(my_lab, "state_operation_failed")
        mock_change_state.assert_called_with("some_state", "etag", "failed")

    @patch('snapshot_tasks._change_lab_status')
    @patch('snapshot_tasks._revert_storage_snapshot')
    def test_revert_snapshot(self, mock_revert_storage_snapshot, mock_change_lab_status):
        my_lab = "reserved_lab"
        lab = dict(lab_name = 'reserved_lab', reservation = "1234567890")
        mock_change_lab_status.return_value = "etag"
        with HTTMock(self.mock_api):
            snapshot_tasks.revert_to_snapshot(my_lab, lab, "available_state", lab_whitelisted=True)
        mock_revert_storage_snapshot.assert_called_with(my_lab, "12334", False)
        mock_change_lab_status.assert_called_with(my_lab, "ready")

    @patch('snapshot_tasks._change_lab_status')
    @patch('snapshot_tasks._revert_storage_snapshot')
    def test_revert_snapshot_and_lab_is_not_reserved(self, mock_revert_storage_snapshot, mock_change_lab_status):
        my_lab = "free_lab"
        lab = dict(lab_name = 'lab')
        mock_change_lab_status.return_value = "etag"
        with HTTMock(self.mock_api):
            with self.assertRaises(exceptions.InvalidTaskError):
                snapshot_tasks.revert_to_snapshot(my_lab, lab, "available_state", lab_whitelisted=True)
        mock_revert_storage_snapshot.assert_not_called()
        mock_change_lab_status.assert_called_with(my_lab, "state_operation_failed")

    @patch('snapshot_tasks._change_lab_status')
    @patch('snapshot_tasks._revert_storage_snapshot')
    def test_revert_snapshot_fails(self, mock_revert_storage_snapshot, mock_change_lab_status):
        my_lab = "reserved_lab"
        lab = dict(lab_name = 'reserved_lab', reservation = "1234567890")
        mock_change_lab_status.return_value = "etag"
        mock_revert_storage_snapshot.side_effect = [RuntimeError]
        with HTTMock(self.mock_api):
            with self.assertRaises(RuntimeError):
                snapshot_tasks.revert_to_snapshot(my_lab, lab, "available_state", lab_whitelisted=True)
        mock_revert_storage_snapshot.assert_called_with(my_lab, "12334", False)
        mock_change_lab_status.assert_called_with(my_lab, 'state_operation_failed')
        mock_revert_storage_snapshot.assert_called_with(my_lab, "12334", False)

    @patch('snapshot_tasks._change_lab_status')
    @patch('snapshot_tasks._revert_storage_snapshot')
    def test_revert_snapshot_and_state_is_not_queued(self, mock_revert, mock_change_lab_status):
        my_lab = "reserved_lab"
        lab = dict(lab_name = 'reserved_lab', reservation = "123456789")
        with HTTMock(self.mock_api):
            with self.assertRaises(exceptions.TaskError):
                snapshot_tasks.revert_to_snapshot(my_lab, lab, "not_queued_state", lab_whitelisted=True)
        mock_change_lab_status.assert_called_with(my_lab, "state_operation_failed")
        mock_revert.assert_not_called()

    @patch('snapshot_tasks._change_lab_status')
    @patch('snapshot_tasks._revert_storage_snapshot')
    def test_revert_snapshot_and_lab_is_not_whitelisted(self, mock_revert, mock_change_lab_status):
        lab = dict(lab_name = 'reserved_lab', reservation = "1234567890")
        with HTTMock(self.mock_api):
            with self.assertRaises(exceptions.TaskError):
                snapshot_tasks.revert_to_snapshot("reserved_lab", lab, "not_whitelisted_state")
        mock_change_lab_status.assert_called_with("reserved_lab", "state_operation_failed")
        mock_revert.assert_not_called()

    def test_change_state_queued_to_creating(self):
        with patch('snapshot_tasks._get_snapshot_status', return_value="queued") as m, patch('snapshot_tasks._patch_snapshot_status', return_value="new_etag"):
            self.assertEqual("new_etag", snapshot_tasks._change_state("state", "etag", "creating"))
            m.assert_called_once_with("state")

    def test_change_state_creating_to_available(self):
        with patch('snapshot_tasks._get_snapshot_status', return_value="creating") as m, patch('snapshot_tasks._patch_snapshot_status', return_value="new_etag"):
            self.assertEqual("new_etag", snapshot_tasks._change_state("state", "etag", "available", snapshot_id="joopajoo"))
            m.assert_called_once_with("state")

    def test_change_state_creating_to_failed(self):
        with patch('snapshot_tasks._get_snapshot_status', return_value="creating") as m, patch('snapshot_tasks._patch_snapshot_status', return_value="new_etag"):
            self.assertEqual("new_etag", snapshot_tasks._change_state("state", "etag", "failed"))
            m.assert_called_once_with("state")

    def test_change_state_queued_to_failed(self):
        with patch('snapshot_tasks._get_snapshot_status', return_value="queued") as m, patch('snapshot_tasks._patch_snapshot_status', return_value="new_etag"):
            with self.assertRaises(exceptions.TaskError):
                snapshot_tasks._change_state("new_etag", "etag", "failed")
                m.assert_called_once_with("state")

    def test_change_lab_status_queued_for_revert_to_reverting(self):
        with patch('snapshot_tasks._get_lab_status', return_value=("queued_for_revert", "etag")) as m, patch('snapshot_tasks._patch_lab', return_value="new_etag"):
            self.assertEqual("new_etag", snapshot_tasks._change_lab_status("lab", "reverting_state"))
            m.assert_called_once_with("lab")

    def test_change_lab_status_failed_to_reverting(self):
        with patch('snapshot_tasks._get_lab_status', return_value=("state_operation_failed", "etag")) as m, patch('snapshot_tasks._patch_lab', return_value="new_etag"):
            self.assertEqual("new_etag", snapshot_tasks._change_lab_status("lab", "reverting_state"))
            m.assert_called_once_with("lab")

    def test_change_lab_status_ready_to_preserving(self):
        with patch('snapshot_tasks._get_lab_status', return_value=("ready", "etag")) as m, patch('snapshot_tasks._patch_lab', return_value="new_etag"):
            self.assertEqual("new_etag", snapshot_tasks._change_lab_status("lab", "preserving_state"))
            m.assert_called_once_with("lab")

    def test_change_lab_status_failed_to_preserving(self):
        with patch('snapshot_tasks._get_lab_status', return_value=("state_operation_failed", "etag")) as m, patch('snapshot_tasks._patch_lab', return_value="new_etag"):
            self.assertEqual("new_etag", snapshot_tasks._change_lab_status("lab", "preserving_state"))
            m.assert_called_once_with("lab")

    def test_change_lab_status_preserving_state_to_ready(self):
        with patch('snapshot_tasks._get_lab_status', return_value=("ready", "etag")) as m, patch('snapshot_tasks._patch_lab', return_value="new_etag"):
            self.assertEqual("new_etag", snapshot_tasks._change_lab_status("lab", "preserving_state"))
            m.assert_called_once_with("lab")

    def test_change_lab_status_failed_to_preserving_state(self):
        with patch('snapshot_tasks._get_lab_status', return_value=("state_operation_failed", "etag")) as m, patch('snapshot_tasks._patch_lab', return_value="new_etag"):
            self.assertEqual("new_etag", snapshot_tasks._change_lab_status("lab", "preserving_state"))
            m.assert_called_once_with("lab")

    def test_change_lab_status_preserving_state_to_initializing(self):
        with patch('snapshot_tasks._get_lab_status', return_value=("preserving_state", "etag")) as m, patch('snapshot_tasks._patch_lab', return_value="new_etag"):
            with self.assertRaises(exceptions.TaskError):
                snapshot_tasks._change_lab_status("lab", "initializing")
                m.assert_called_once_with("lab")

if __name__ == '__main__':
    unittest.main()
