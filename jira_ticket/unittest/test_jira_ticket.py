import unittest
import sys
sys.path.append("..")
sys.path.append("../../common")

from jira_ticket import JiraTicket

class TestJiraTicket(unittest.TestCase):
  jira_ticket = JiraTicket()
  
  def test_init(self):
    expected_result = ['asangwan', 'caiyzhan', 'carhe', 'dalbu']
    expected_result.sort()
    self.assertEqual(self.jira_ticket._reporters_chengdu, expected_result)

  def test_get(self):
    expected_result = [
      {'key': 'OSSSUP-88094', 'Summary': 'CLAB856 scratch install failed with N19 P8 build', 'assignee': 'w2yu', 'reporter': 'wendywan', 'from': 'Chengdu', 'creation_date': '1588242180'}, 
      {'key': 'OSSSUP-88092', 'Summary': 'Unplanned SW upgrade,lab upgrades are failing on CLAB1378', 'assignee': 'w2yu', 'reporter': 'sbhargav', 'from': 'Others', 'creation_date': '1588213200'}
    ]
    expected_result = sorted(list, key=lambda k: k['key'])
    self.assertEqual(self.jira_ticket.get(), expected_result)


if __name__ == '__main__':
  unittest.main()
