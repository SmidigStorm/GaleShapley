import os
import argparse
from gale_shapley import (
    load_data,
    create_applicant_preferences,
    create_university_quotas,
    gale_shapley_matching,
    handle_guaranteed_students,  # Add this import
    format_results_markdown,
    save_results
)

def main():
    """
    Main entry point for running the Gale-Shapley algorithm for university admissions.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run the Gale-Shapley algorithm for university admissions.')
    parser.add_argument('--applicants', type=str, default='data/input/applicants.csv',
                        help='Path to applicants CSV file')
    parser.add_argument('--universities', type=str, default='data/input/universities.csv',
                        help='Path to universities CSV file')
    parser.add_argument('--output', type=str, default='data/output/results.md',
                        help='Path to output markdown file')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Ensure directories exist
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Load data
    if args.verbose:
        print(f"Loading data from {args.applicants} and {args.universities}...")
    
    raw_applicants, raw_universities = load_data(args.applicants, args.universities)
    
    if args.verbose:
        print(f"Loaded {len(raw_applicants)} applicants and {len(raw_universities)} universities.")
    
    # Create Gale-Shapley entities
    gs_applicants = create_applicant_preferences(raw_applicants)
    university_quotas = create_university_quotas(raw_applicants, raw_universities)
    
    if args.verbose:
        print(f"Created {len(gs_applicants)} applicant objects and {len(university_quotas)} university quota objects.")
        
        # Print sample of applicant preferences
        print("\nSample Applicant Preferences:")
        for i, (app_id, applicant) in enumerate(gs_applicants.items()):
            print(f"{app_id}: {applicant.preferences}")
            if i >= 2:  # Show just a few examples
                print("...")
                break
        
        # Print sample of university quota rankings
        print("\nSample University Quota Rankings:")
        for i, (quota_id, quota) in enumerate(university_quotas.items()):
            print(f"{quota_id} (Quota: {quota.quota}): {quota.preferences[:5]}...")
            if i >= 2:  # Show just a few examples
                print("...")
                break
    
    # Run Gale-Shapley algorithm
    if args.verbose:
        print("\nRunning Gale-Shapley algorithm...")
    
    matching = gale_shapley_matching(gs_applicants, university_quotas)
    
    matching = handle_guaranteed_students(matching, raw_applicants, gs_applicants, university_quotas)
    
    if args.verbose:
        print("Algorithm completed successfully.")
    
    # Format results
    formatted_result = format_results_markdown(matching, gs_applicants, university_quotas, raw_applicants)
    
    # Save results
    save_results(formatted_result, args.output)
    
    if args.verbose:
        print(f"\nResults saved to {args.output}")
    
    # Also print results to console
    print("\n" + formatted_result)
    
    return 0

if __name__ == "__main__":
    main()