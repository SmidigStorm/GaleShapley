import unittest
from gale_shapley.models import Applicant, UniversityQuota
from gale_shapley.algorithm import gale_shapley_matching

class TestGaleShapleyAlgorithm(unittest.TestCase):
    def test_basic_matching(self):
        # Create applicants
        applicants = {
            'A1': Applicant('A1', ['U1_Q1', 'U2_Q1']),
            'A2': Applicant('A2', ['U1_Q1', 'U2_Q1']),
            'A3': Applicant('A3', ['U2_Q1', 'U1_Q1'])
        }
        
        # Create university quotas
        university_quotas = {
            'U1_Q1': UniversityQuota('U1_Q1', 1, ['A1', 'A2', 'A3']),
            'U2_Q1': UniversityQuota('U2_Q1', 2, ['A3', 'A1', 'A2'])
        }
        
        # Run the algorithm
        matching = gale_shapley_matching(applicants, university_quotas)
        
        # Check results
        self.assertEqual(matching['U1_Q1'], ['A1'])
        self.assertEqual(set(matching['U2_Q1']), {'A2', 'A3'})
    
    def test_complex_matching(self):
        # Create applicants with preferences across multiple quota categories
        applicants = {
            'A1': Applicant('A1', ['U1_Q1', 'U2_Q1', 'U1_Q2']),
            'A2': Applicant('A2', ['U2_Q1', 'U1_Q1', 'U2_Q2']),
            'A3': Applicant('A3', ['U1_Q2', 'U2_Q2', 'U1_Q1']),
            'A4': Applicant('A4', ['U2_Q2', 'U1_Q2', 'U2_Q1'])
        }
        
        # Create university quotas with different sizes
        university_quotas = {
            'U1_Q1': UniversityQuota('U1_Q1', 1, ['A1', 'A2', 'A3', 'A4']),
            'U1_Q2': UniversityQuota('U1_Q2', 1, ['A3', 'A4', 'A1', 'A2']),
            'U2_Q1': UniversityQuota('U2_Q1', 1, ['A2', 'A1', 'A3', 'A4']),
            'U2_Q2': UniversityQuota('U2_Q2', 1, ['A4', 'A3', 'A2', 'A1'])
        }
        
        # Run the algorithm
        matching = gale_shapley_matching(applicants, university_quotas)
        
        # Check results - all quotas should be filled
        self.assertEqual(matching['U1_Q1'], ['A1'])
        self.assertEqual(matching['U1_Q2'], ['A3'])
        self.assertEqual(matching['U2_Q1'], ['A2'])
        self.assertEqual(matching['U2_Q2'], ['A4'])
        
        # Check that all applicants are matched
        matched_applicants = []
        for quota_matches in matching.values():
            matched_applicants.extend(quota_matches)
        
        self.assertEqual(set(matched_applicants), {'A1', 'A2', 'A3', 'A4'})

if __name__ == '__main__':
    unittest.main()