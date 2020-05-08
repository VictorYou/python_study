import unittest
import sys
sys.path.append("..")
sys.path.append("../../common")

from jira_ticket import JiraTicket

class TestJiraTicket(unittest.TestCase):
  maxDiff = None
  jira_ticket = JiraTicket()
  
  def test_init(self):
    expected_reporters_lab = ['magrocho', 'junlili']
    expected_reporters_lab.sort()
    self.assertEqual(self.jira_ticket._reporters_lab, expected_reporters_lab)
    expected_reporters_chengdu = ['asangwan', 'caiyzhan', 'carhe', 'dalbu', 'kuni', 'wendywan']
    expected_reporters_chengdu.sort()
    self.assertEqual(self.jira_ticket._reporters_chengdu, expected_reporters_chengdu)

  def test_get_tickets(self):
    expected_tickets = [
      {'Issue key': 'OSSSUP-88094', 'Summary': 'CLAB856s scratch install ', 'Assignee': 'w2yu', 'Reporter': 'wendywan', 'From': 'Chengdu', 'Created': 1585688400}, 
      {'Issue key': 'OSSSUP-88093', 'Summary': 'clab3423 install to NetAc', 'Assignee': 'w2yu', 'Reporter': 'kuni', 'From': 'Chengdu', 'Created': 1583013600}, 
      {'Issue key': 'OSSSUP-88092', 'Summary': 'lab upgrades are failing ', 'Assignee': 'w2yu', 'Reporter': 'sbhargav', 'From': 'Others', 'Created': 1580508000},
      {'Issue key': 'OSSSUP-88086', 'Summary': '[CLAB849] Application Ini', 'Assignee': 'w2yu', 'Reporter': 'tedkim', 'From': 'Others', 'Created': 1580508000},
    ]
    expected_tickets = sorted(expected_tickets, key=lambda k: k['Issue key'])
    expected_created = [1580508000, 1583013600, 1585688400]
    self.jira_ticket.get_tickets()
    self.assertEqual(self.jira_ticket._tickets, expected_tickets)
    self.assertEqual(self.jira_ticket._created, expected_created)

  def test_get_counts(self):
    tickets_old = self.jira_ticket._tickets
    created_old = self.jira_ticket._created
    self.jira_ticket._created = [1, 2, 3]
    self.jira_ticket._tickets = [
      {'Issue key': 'OSSSUP-88094', 'Summary': 'CLAB856s scratch install ', 'Assignee': 'w2yu', 'Reporter': 'wendywan', 'From': 'Chengdu', 'Created': 3}, 
      {'Issue key': 'OSSSUP-88093', 'Summary': 'clab3423 install to NetAc', 'Assignee': 'w2yu', 'Reporter': 'kuni', 'From': 'Chengdu', 'Created': 2}, 
      {'Issue key': 'OSSSUP-88092', 'Summary': 'lab upgrades are failing ', 'Assignee': 'w2yu', 'Reporter': 'sbhargav', 'From': 'Others', 'Created': 1},
      {'Issue key': 'OSSSUP-88086', 'Summary': '[CLAB849] Application Ini', 'Assignee': 'w2yu', 'Reporter': 'tedkim', 'From': 'Others', 'Created': 1},
    ]
    expected = [
      {'location': 'Others', 'creation_date': 1, 'count': 2},
      {'location': 'Chengdu', 'creation_date': 2, 'count': 1},
      {'location': 'Chengdu', 'creation_date': 3, 'count': 1},
    ]
    expected = sorted(expected, key=lambda k: k['creation_date'])
    print(f"created: {self.jira_ticket._created}")
    self.jira_ticket.get_counts()
    self.assertEqual(self.jira_ticket._counts, expected)
    self.jira_ticket._tickets = tickets_old
    self.jira_ticket._created = created_old


if __name__ == '__main__':
  unittest.main()
