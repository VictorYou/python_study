import unittest
import sys
sys.path.append("..")
from build_promotion_history import RisPromotionHistory
from unittest.mock import MagicMock

class TestRisPromotionHistory(unittest.TestCase):
  history = RisPromotionHistory('MED_N20/3GPPNBI/20.0.0.390')
  def test_init(self):
    self.assertEqual(self.history._ris_status_file, 'MED_N20-3GPPNBI-20.0.0.390-status.xml')

  def test_get_status_list(self):
    expected_result = [
      {'component_upgrade_validated_with': '2020-04-18T04:24:57+03:00'},
      {'ready_for_product': '2020-04-23T06:03:22+03:00'},
      {'release_upgrade_validated_with': '2020-04-22T10:14:34+03:00'},
      {'scratch_install_validated_with': '2020-04-23T10:29:23+03:00'},
    ]
    expected_result = sorted(expected_result, key=lambda d: list(d.keys()))
    self.assertEqual(self.history.get_status_list(), expected_result)

  def test_get_status_list_timestamp(self):
    status_list = [
      {'component_upgrade_validated_with': '2020-04-18T04:24:57+03:00'},
      {'ready_for_product': '2020-04-23T06:03:22+03:00'},
    ]
    expected_result = [
      {'component_upgrade_validated_with': 1587173097},
      {'ready_for_product': 1587611002},
    ]
    self.history.get_status_list = MagicMock(return_value=status_list)
    expected_result = sorted(expected_result, key=lambda d: list(d.keys()))
    self.assertEqual(self.history.get_status_list_timestamp(), expected_result)

  def test_get_promotion_date_timestamp(self):
    status_list_timestamp1 = [
      {'component_upgrade_validated_with': 10},
      {'ready_for_product': 11},
      {'release_upgrade_validated_with': 12},
      {'scratch_install_validated_with': 13},
    ]
    status_list_timestamp2 = [
      {'component_upgrade_validated_with': 10},
      {'ready_for_product': 14},
      {'release_upgrade_validated_with': 12},
      {'scratch_install_validated_with': 13},
    ]
    orig = self.history.get_status_list_timestamp
    self.history.get_status_list_timestamp = MagicMock(return_value=status_list_timestamp1)
    self.assertEqual(self.history.get_promotion_date_timestamp(), 13)
    self.history.get_status_list_timestamp = MagicMock(return_value=status_list_timestamp2)
    self.assertEqual(self.history.get_promotion_date_timestamp(), 14)
    self.history.get_status_list_timestamp = orig

  def test_get_commit_date(self):
    self.assertEqual(self.history.get_commit_date(), '2020-04-17T08:07:20+03:00')

  def test_get_commit_date_timestamp(self):
    self.history.get_commit_date = MagicMock(return_value='2020-04-18T08:07:20+03:00')
    self.assertEqual(self.history.get_commit_date_timestamp(), 1587186440)

  def test_get_promotion_time(self):
    orig_get_status_list = self.history.get_status_list
    self.history.get_status_list = MagicMock(return_value=True)
    self.history.get_commit_date_timestamp = MagicMock(return_value=13)
    self.history.get_promotion_date_timestamp = MagicMock(return_value=20)
    self.assertEqual(self.history.get_promotion_time(), 7)
    self.history.get_status_list = orig_get_status_list
    

if __name__ == '__main__':
    unittest.main()
