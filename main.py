import argparse
import os
from src.algorithm import gale_shapley_matching
from src.utils import (
    load_preferences_from_json, 
    load_preferences_from_csv,
    save_matching_to_json,
    format_matching_result
)

def main():
    parser = argparse.ArgumentParser(description='Run the Gale-Shapley matching algorithm.')
    parser.add_argument('--json', type=str, help='Path to JSON input file')
    parser.add_argument('--applicants-csv', type=str, help='Path to applicants CSV file')
    parser.add_argument('--universities-csv', type=str, help='Path to universities CSV file')
    parser.add_argument('--output', type=str, default='data/output/matching_results.json', 
                        help='Path to output file')
    
    args = parser.parse_args()
    
    # Load data
    if args.json:
        applicants, universities = load_preferences_from_json(args.json)
    elif args.applicants_csv and args.universities_csv:
        applicants, universities = load_preferences_from_csv(args.applicants_csv, args.universities_csv)
    else:
        # Default to sample data
        print("No input files specified. Using sample data...")
        from src.models import Applicant, University
        
        # Create sample applicants
        applicants = {
            'A1': Applicant('A1', ['U3', 'U1', 'U2']),
            'A2': Applicant('A2', ['U1', 'U3', 'U2']),
            'A3': Applicant('A3', ['U2', 'U1', 'U3']),
            'A4': Applicant('A4', ['U3', 'U2', 'U1']),
            'A5': Applicant('A5', ['U1', 'U2', 'U3']),
            'A6': Applicant('A6', ['U2', 'U3', 'U1'])
        }
        
        # Create sample universities
        universities = {
            'U1': University('U1', 2, ['A3', 'A1', 'A5', 'A2', 'A6', 'A4']),
            'U2': University('U2', 1, ['A6', 'A3', 'A2', 'A1', 'A4', 'A5']),
            'U3': University('U3', 2, ['A2', 'A4', 'A1', 'A5', 'A6', 'A3'])
        }
    
    # Run algorithm
    matching = gale_shapley_matching(applicants, universities)
    
    # Display results
    formatted_result = format_matching_result(matching, applicants, universities)
    print(formatted_result)
    
    # Save results
    if args.output:
        # Make sure output directory exists
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        save_matching_to_json(matching, args.output)
        print(f"Results saved to {args.output}")

if __name__ == "__main__":
    main()