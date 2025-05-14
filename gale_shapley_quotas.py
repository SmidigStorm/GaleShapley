import os
import csv
from gale_shapley.models import Applicant, University
from gale_shapley.algorithm import gale_shapley_matching

def create_applicant_preferences(applicants):
    """
    Create preference lists for each applicant based on eligibility and university preference.
    
    Returns:
        Dictionary of Applicant objects with preference lists
    """
    gale_shapley_applicants = {}
    
    for app_id, app_data in applicants.items():
        # Get university preferences
        s1_priority = int(app_data['S1_priority'])
        s2_priority = int(app_data['S2_priority'])
        
        # Initialize preference list
        preferences = []
        
        # Create a list of quota categories with university priority
        quota_options = []
        
        # Check eligibility for S1 quotas
        if app_data['S1_Q1_eligible'] == 'Yes':
            quota_options.append(('S1_Q1', s1_priority, 1))
        if app_data['S1_Q2_eligible'] == 'Yes':
            quota_options.append(('S1_Q2', s1_priority, 2))
        if app_data['S1_Q3_eligible'] == 'Yes':
            quota_options.append(('S1_Q3', s1_priority, 3))
            
        # Check eligibility for S2 quotas
        if app_data['S2_Q1_eligible'] == 'Yes':
            quota_options.append(('S2_Q1', s2_priority, 1))
        if app_data['S2_Q2_eligible'] == 'Yes':
            quota_options.append(('S2_Q2', s2_priority, 2))
        
        # Sort by university priority, then by quota priority
        quota_options.sort(key=lambda x: (x[1], x[2]))
        
        # Extract just the quota category names for the preference list
        preferences = [option[0] for option in quota_options]
        
        # Create Applicant object
        gale_shapley_applicants[app_id] = Applicant(app_id, preferences)
    
    return gale_shapley_applicants

def create_quota_universities(applicants, universities):
    """
    Create University objects for each quota category.
    
    Returns:
        Dictionary of University objects with rankings of students
    """
    gale_shapley_universities = {}
    
    # Initialize university objects
    for univ_id, univ_data in universities.items():
        for quota_name in ['Q1', 'Q2', 'Q3']:
            # Skip Q3 for S2 since it doesn't exist
            if quota_name == 'Q3' and univ_id == 'S2':
                continue
                
            quota_id = f"{univ_id}_{quota_name}"
            quota_size = univ_data[f'{quota_name}_quota']
            
            # Create ranking of students
            ranking = []
            
            # Collect eligible students with their points
            eligible_students = []
            for app_id, app_data in applicants.items():
                if app_data[f'{univ_id}_{quota_name}_eligible'] == 'Yes':
                    points = int(app_data[f'{univ_id}_{quota_name}_points'])
                    eligible_students.append((app_id, points))
            
            # Sort by points (higher points = higher ranking)
            eligible_students.sort(key=lambda x: x[1], reverse=True)
            
            # Create ranking list
            ranking = [student[0] for student in eligible_students]
            
            # Create University object
            gale_shapley_universities[quota_id] = University(quota_id, quota_size, ranking)
    
    return gale_shapley_universities

def format_quota_matching_results(matching, gs_applicants, gs_universities, raw_applicants):
    """
    Format matching results for display.
    """
    output = "# Admission Results\n\n"
    
    # Count total admitted students
    total_admitted = set()
    for quota_id, admitted_students in matching.items():
        total_admitted.update(admitted_students)
    
    output += f"Total students admitted: {len(total_admitted)} out of {len(gs_applicants)}\n\n"
    
    # Group results by university
    university_results = {
        'S1': {'Q1': [], 'Q2': [], 'Q3': []},
        'S2': {'Q1': [], 'Q2': []}
    }
    
    for quota_id, admitted_students in matching.items():
        univ_id, quota_name = quota_id.split('_')
        university_results[univ_id][quota_name] = admitted_students
    
    # Display results per university and quota
    for univ_id, quotas in university_results.items():
        output += f"## {univ_id}\n\n"
        
        for quota_name, students in quotas.items():
            if quota_name == 'Q3' and univ_id == 'S2':
                continue  # Skip Q3 for S2 since it doesn't exist
                
            quota_id = f"{univ_id}_{quota_name}"
            quota_size = gs_universities[quota_id].quota if quota_id in gs_universities else 0
            
            output += f"### {quota_name} (Capacity: {quota_size})\n"
            
            if not students:
                output += "- No students admitted\n\n"
                continue
                
            output += "| Student | Points |\n"
            output += "|---------|--------|\n"
            
            # Sort by points for display
            sorted_students = []
            for student in students:
                points = raw_applicants[student][f"{univ_id}_{quota_name}_points"]
                sorted_students.append((student, points))
                
            sorted_students.sort(key=lambda x: int(x[1]), reverse=True)
            
            for student, points in sorted_students:
                output += f"| {student} | {points} |\n"
            
            output += "\n"
    
    # Display unmatched students
    unmatched = set(gs_applicants.keys()) - total_admitted
    if unmatched:
        output += "## Unmatched Students\n\n"
        for student in sorted(unmatched):
            output += f"- {student}\n"
    
    return output

if __name__ == "__main__":
    # Ensure output directory exists
    os.makedirs('data/output', exist_ok=True)
    
    # Load data
    applicants_file = 'data/input/applicants.csv'
    universities_file = 'data/input/universities.csv'
    
    print(f"Loading data from {applicants_file} and {universities_file}...")
    
    # Load raw data
    raw_applicants = {}
    with open(applicants_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_applicants[row['applicant_id']] = row
    
    raw_universities = {}
    with open(universities_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_universities[row['university_id']] = {
                'Q1_quota': int(row['Q1_quota']),
                'Q2_quota': int(row['Q2_quota']),
                'Q3_quota': int(row['Q3_quota'] if 'Q3_quota' in row else 0)
            }
    
    # Create Gale-Shapley applicants and universities
    gs_applicants = create_applicant_preferences(raw_applicants)
    gs_universities = create_quota_universities(raw_applicants, raw_universities)
    
    print(f"Created {len(gs_applicants)} applicants and {len(gs_universities)} quota categories.")
    
    # Debug - print applicant preferences
    print("\nApplicant Preferences:")
    for app_id, applicant in gs_applicants.items():
        print(f"{app_id}: {applicant.preferences}")
    
    # Debug - print university rankings
    print("\nUniversity (Quota) Rankings:")
    for univ_id, university in gs_universities.items():
        print(f"{univ_id} (Quota: {university.quota}): {university.preferences[:5]}...")
    
    # Run Gale-Shapley algorithm
    matching = gale_shapley_matching(gs_applicants, gs_universities)
    
    # Format results
    formatted_result = format_quota_matching_results(matching, gs_applicants, gs_universities, raw_applicants)
    print("\nMatching Results:")
    print(formatted_result)
    
    # Save results
    output_file = 'data/output/results.md'
    with open(output_file, 'w') as f:
        f.write(formatted_result)
    
    print(f"\nResults saved to {output_file}")