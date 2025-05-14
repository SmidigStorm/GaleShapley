import unittest
from src.models import Applicant, University
from src.algorithm import gale_shapley_matching

class TestGaleShapleyAlgorithm(unittest.TestCase):
    
    def test_basic_matching(self):
        # Create a simple test case with 3 applicants and 2 universities
        applicants = {
            'A1': Applicant('A1', ['U1', 'U2']),
            'A2': Applicant('A2', ['U1', 'U2']),
            'A3': Applicant('A3', ['U2', 'U1'])
        }
        
        universities = {
            'U1': University('U1', 1, ['A1', 'A2', 'A3']),
            'U2': University('U2', 2, ['A3', 'A1', 'A2'])
        }
        
        matching = gale_shapley_matching(applicants, universities)
        
        # Check that the matching is correct
        self.assertEqual(matching['U1'], ['A1'])
        self.assertEqual(set(matching['U2']), {'A2', 'A3'})
        
    def test_unequal_sets(self):
        # Test with more applicants than spots
        applicants = {
            'A1': Applicant('A1', ['U1', 'U2', 'U3']),
            'A2': Applicant('A2', ['U1', 'U3', 'U2']),
            'A3': Applicant('A3', ['U2', 'U1', 'U3']),
            'A4': Applicant('A4', ['U3', 'U2', 'U1']),
            'A5': Applicant('A5', ['U1', 'U2', 'U3']),
            'A6': Applicant('A6', ['U2', 'U3', 'U1'])
        }
        
        universities = {
            'U1': University('U1', 2, ['A3', 'A1', 'A5', 'A2', 'A6', 'A4']),
            'U2': University('U2', 1, ['A6', 'A3', 'A2', 'A1', 'A4', 'A5']),
            'U3': University('U3', 2, ['A2', 'A4', 'A1', 'A5', 'A6', 'A3'])
        }
        
        matching = gale_shapley_matching(applicants, universities)
        
        # Check total matched spots
        total_matched = sum(len(matches) for matches in matching.values())
        self.assertEqual(total_matched, 5)  # Total quota is 5
        
        # Ensure no university exceeds its quota
        self.assertLessEqual(len(matching['U1']), 2)
        self.assertLessEqual(len(matching['U2']), 1)
        self.assertLessEqual(len(matching['U3']), 2)

if __name__ == '__main__':
    unittest.main()