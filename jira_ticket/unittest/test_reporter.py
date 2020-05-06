import unittest
import sys
sys.path.append("..")

from reporter import TicketReader

class TestTicketReader(unittest.TestCase):
  def test_reporter(self):
    expected_result = ['wendywan', 'sbhargav', 'tedkim', 'kuni']
    expected_result.sort()
    self.assertEqual(TicketReader('result.csv').reporter(), ','.join(expected_result))


if __name__ == '__main__':
  unittest.main()
