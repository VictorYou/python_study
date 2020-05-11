import unittest
import os
import sys

sys.path.append("..")
sys.path.append("../../common")

from promotion_history import RisVersionPromotionHistory, RisComponentPromotionHistory
from riscomponent_list import RisVersionCommitter, RisVersionDependencyVersion
from exceptions import MissingStatus, CommitDateTooOld
from unittest.mock import MagicMock

class TestRisVersionPromotionHistory(unittest.TestCase):
  history = RisVersionPromotionHistory('MED_N20/3GPPNBI/20.0.0.390', 'component_upgrade_validated_with,release_upgrade_validated_with,scratch_install_validated_with:ready_for_product', '2019-04-18T04:24:57')

  def test_init(self):
    self.assertEqual(self.history._ris_id, 'MED_N20/3GPPNBI/20.0.0.390')
    self.assertEqual(self.history._ris_status_file, 'MED_N20-3GPPNBI-20.0.0.390-status.xml')
    self.assertEqual(self.history._status_keys_list, [['component_upgrade_validated_with', 'release_upgrade_validated_with', 'scratch_install_validated_with'], ['ready_for_product']])

  def test_get_status_list(self):
    expected_result = [
      {'component_upgrade_validated_with': '2020-04-18T04:24:57+03:00'},
      {'ready_for_product': '2020-04-23T06:03:22+03:00'},
      {'release_upgrade_validated_with': '2020-04-22T10:14:34+03:00'},
      {'scratch_install_validated_with': '2020-04-23T10:29:23+03:00'},
    ]
    expected_result = sorted(expected_result, key=lambda d: list(d.keys()))
    orig = self.history.download_files
    self.history.download_files = MagicMock(return_value=True)
    self.assertEqual(self.history.get_status_list(), expected_result)
    self.history.download_files = orig

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
      {'ready_for_product': 9},
      {'release_upgrade_validated_with': 12},
      {'scratch_install_validated_with': 13},
    ]
    status_list_timestamp3 = [
      {'component_upgrade_validated_with': 10},
      {'release_upgrade_validated_with': 12},
      {'scratch_install_validated_with': 13},
    ]
    orig = self.history.get_status_list_timestamp
    self.history.get_status_list_timestamp = MagicMock(return_value=status_list_timestamp1)
    self.assertEqual(self.history.get_promotion_date_timestamp(), 11)
    self.history.get_status_list_timestamp = MagicMock(return_value=status_list_timestamp2)
    self.assertEqual(self.history.get_promotion_date_timestamp(), 10)
    self.history.get_status_list_timestamp = MagicMock(return_value=status_list_timestamp3)
    self.assertRaises(MissingStatus, self.history.get_promotion_date_timestamp)
    self.history.get_status_list_timestamp = orig

  def test_get_commit_date(self):
    os.system("cp ris_RisVersionPromotionHistory.xml ris.xml")
    self.assertEqual(self.history.get_commit_date(), '2020-04-17T08:07:20+03:00')
    os.system('rm -rf ris.xml')

  def test_get_commit_date_timestamp(self):
    orig = self.history.get_commit_date
    self.history.get_commit_date = MagicMock(return_value='2020-04-18T08:07:20+03:00')
    self.assertEqual(self.history.get_commit_date_timestamp(), 1587186440)
    self.history.get_commit_date = MagicMock(return_value='2018-04-18T08:07:20+03:00')
    self.assertRaises(CommitDateTooOld, self.history.get_commit_date_timestamp)
    self.history.get_commit_date = orig

  def test_get_promotion_history(self):
    orig_get_status_list = self.history.get_status_list
    self.history.get_status_list = MagicMock(return_value=True)
    self.history.get_commit_date_timestamp = MagicMock(return_value=13)
    self.history.get_promotion_date_timestamp = MagicMock(return_value=20)
    expected_result = {'ris_id': 'MED_N20/3GPPNBI/20.0.0.390', 'ris_component': '3GPPNBI', 'promotion_date': 20, 'promotion_time': 7 / 3600, 'commit_date': 13}
    self.assertEqual(self.history.get(), expected_result)
    self.history.get_status_list = orig_get_status_list
    

class TestRisComponentPromotionHistory(unittest.TestCase):
  history = RisComponentPromotionHistory('MED_N20/3GPPNBI')

  def test_init(self):
    self.assertEqual(self.history._ris_group_component, 'MED_N20/3GPPNBI')
    self.assertEqual(self.history._chronological, 'chronological.xml')

  def test_get_versions(self):
    orig = self.history.download_file
    self.history.download_file = MagicMock(return_value=True)
    expected_list = ['20.0.0.401']
    expected_list.sort()
    self.assertEqual(self.history.get_versions('2020-04-24T18:30:39'), expected_list)
    self.history.download_file = orig


class TestRisVersionCommitter(unittest.TestCase):
  committer = RisVersionCommitter('MED_N20/3GPPNBI/20.0.0.390')
  def test_get(self):
    os.system('cp ris_RisVersionCommitter.xml ris.xml')
    self.committer.download_files = MagicMock(return_value=True)
    self.assertEqual(self.committer.get(), 'stone.1.shi@nokia-sbell.com')
    os.system('rm -rf ris.xml')

class TestRisVersionDependencyVersion(unittest.TestCase):
  dependency_version = RisVersionDependencyVersion('MED_N20/3GPPNBI/20.0.0.390')
  def test_get(self):
    os.system('cp ris_RisVersionDependencyVersion.xml ris.xml')
    self.dependency_version.download_files = MagicMock(return_value=True)
    expected = ['adaptations-2/ADAP_2G_10/19.0.0.10', 'adaptations-2/ADAP_2GASBSC_11/19.1.0.13']
    expected.sort()
    self.assertEqual(self.dependency_version.get(), expected)
    os.system('rm -rf ris.xml')


if __name__ == '__main__':
    unittest.main()
