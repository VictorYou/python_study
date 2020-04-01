import unittest
from build_promotion_history import RisPromotionHistory

class TestRisPromotionHistory(unittest.TestCase):
  def test_ris_promotion_history_init(self):
    history = RisPromotionHistory('MED_N20/3GPPNBI/20.0.0.390')
    expected_ris_status_file = 'MED_N20-3GPPNBI-20.0.0.390-status.xml'
    self.assertEqual(history._ris_status_file, expected_ris_status_file)
    
if __name__ == '__main__':
    unittest.main()
