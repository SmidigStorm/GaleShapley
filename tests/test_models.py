import unittest
from gale_shapley.models import Applicant, UniversityQuota

class TestApplicant(unittest.TestCase):
    def test_get_next_preference(self):
        # Create an applicant with preferences
        applicant = Applicant('A1', ['U1_Q1', 'U2_Q1', 'U1_Q2'])
        
        # Test getting preferences in sequence
        self.assertEqual(applicant.get_next_preference(), 'U1_Q1')
        self.assertEqual(applicant.get_next_preference(), 'U2_Q1')
        self.assertEqual(applicant.get_next_preference(), 'U1_Q2')
        self.assertIsNone(applicant.get_next_preference())  # No more preferences

class TestUniversityQuota(unittest.TestCase):
    def test_prefers(self):
        # Create a university quota with preferences
        univ_quota = UniversityQuota('U1_Q1', 2, ['A1', 'A2', 'A3', 'A4'])
        
        # Test preference comparisons
        self.assertTrue(univ_quota.prefers('A1', 'A2'))   # A1 is preferred over A2
        self.assertTrue(univ_quota.prefers('A2', 'A4'))   # A2 is preferred over A4
        self.assertFalse(univ_quota.prefers('A3', 'A2'))  # A3 is not preferred over A2
        self.assertFalse(univ_quota.prefers('A5', 'A4'))  # A5 is not in preferences
    
    def test_add_applicant(self):
        # Create a university quota with preferences
        univ_quota = UniversityQuota('U1_Q1', 2, ['A1', 'A2', 'A3', 'A4'])
        
        # Test adding applicants within quota
        self.assertIsNone(univ_quota.add_applicant('A2'))  # A2 is accepted
        self.assertEqual(univ_quota.current_matches, ['A2'])
        
        self.assertIsNone(univ_quota.add_applicant('A4'))  # A4 is accepted
        self.assertEqual(set(univ_quota.current_matches), {'A2', 'A4'})
        
        # Test adding a more preferred applicant when quota is full
        self.assertEqual(univ_quota.add_applicant('A3'), 'A4')  # A3 replaces A4
        self.assertEqual(set(univ_quota.current_matches), {'A2', 'A3'})
        
        # Test adding a top preferred applicant when quota is full
        self.assertEqual(univ_quota.add_applicant('A1'), 'A3')  # A1 replaces A3
        self.assertEqual(set(univ_quota.current_matches), {'A1', 'A2'})
        
        # Test adding a less preferred applicant when quota is full
        self.assertEqual(univ_quota.add_applicant('A4'), 'A4')  # A4 is rejected
        self.assertEqual(set(univ_quota.current_matches), {'A1', 'A2'})

if __name__ == '__main__':
    unittest.main()