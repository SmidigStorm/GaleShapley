import csv
from .models import Applicant, UniversityQuota

def load_data(applicants_file, universities_file):
    """
    Load data from CSV files.
    
    Args:
        applicants_file: Path to applicants CSV file
        universities_file: Path to universities CSV file
        
    Returns:
        Tuple of (raw_applicants, raw_universities) dictionaries
    """
    # Load applicants
    raw_applicants = {}
    with open(applicants_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_applicants[row['applicant_id']] = row
    
    # Load universities
    raw_universities = {}
    with open(universities_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            university_id = row['university_id']
            quota_data = {}
            
            # Extract quota values
            for key in row.keys():
                if key.endswith('_quota'):
                    quota_data[key] = int(row[key])
            
            raw_universities[university_id] = quota_data
    
    return raw_applicants, raw_universities

def create_applicant_preferences(raw_applicants):
    """
    Create preference lists for each applicant based on eligibility and university preference.
    
    Args:
        raw_applicants: Dictionary of raw applicant data from CSV
        
    Returns:
        Dictionary of Applicant objects with preference lists
    """
    gs_applicants = {}
    
    for app_id, app_data in raw_applicants.items():
        # Get university preferences
        s1_priority = int(app_data['S1_priority'])
        s2_priority = int(app_data['S2_priority'])
        
        # Create a list of quota categories with university priority
        quota_options = []
        
        # Check eligibility for S1 quotas
        if 'S1_Q1_eligible' in app_data and app_data['S1_Q1_eligible'] == 'Yes':
            quota_options.append(('S1_Q1', s1_priority, 1))
        if 'S1_Q2_eligible' in app_data and app_data['S1_Q2_eligible'] == 'Yes':
            quota_options.append(('S1_Q2', s1_priority, 2))
        if 'S1_Q3_eligible' in app_data and app_data['S1_Q3_eligible'] == 'Yes':
            quota_options.append(('S1_Q3', s1_priority, 3))
            
        # Check eligibility for S2 quotas
        if 'S2_Q1_eligible' in app_data and app_data['S2_Q1_eligible'] == 'Yes':
            quota_options.append(('S2_Q1', s2_priority, 1))
        if 'S2_Q2_eligible' in app_data and app_data['S2_Q2_eligible'] == 'Yes':
            quota_options.append(('S2_Q2', s2_priority, 2))
        
        # Sort by university priority, then by quota priority
        quota_options.sort(key=lambda x: (x[1], x[2]))
        
        # Extract just the quota category names for the preference list
        preferences = [option[0] for option in quota_options]
        
        # Create Applicant object
        gs_applicants[app_id] = Applicant(app_id, preferences)
    
    return gs_applicants

def create_university_quotas(raw_applicants, raw_universities):
    """
    Create UniversityQuota objects with rankings of students.
    
    Args:
        raw_applicants: Dictionary of raw applicant data from CSV
        raw_universities: Dictionary of raw university data from CSV
        
    Returns:
        Dictionary of UniversityQuota objects
    """
    university_quotas = {}
    
    # Get all university IDs
    university_ids = list(raw_universities.keys())
    
    # Process each university
    for univ_id in university_ids:
        # Get quota data
        univ_data = raw_universities[univ_id]
        
        # Process each quota
        for quota_key, quota_size in univ_data.items():
            # Extract quota name (e.g., "Q1" from "Q1_quota")
            quota_name = quota_key.split('_')[0]
            
            # Skip empty quotas
            if quota_size <= 0:
                continue
            
            quota_id = f"{univ_id}_{quota_name}"
            
            # Collect eligible students with their points
            eligible_students = []
            for app_id, app_data in raw_applicants.items():
                eligibility_key = f"{univ_id}_{quota_name}_eligible"
                points_key = f"{univ_id}_{quota_name}_points"
                
                if eligibility_key in app_data and app_data[eligibility_key] == 'Yes' and points_key in app_data:
                    points = int(app_data[points_key])
                    eligible_students.append((app_id, points))
            
            # Sort by points (higher points = higher ranking)
            eligible_students.sort(key=lambda x: x[1], reverse=True)
            
            # Create ranking list
            ranking = [student[0] for student in eligible_students]
            
            # Create UniversityQuota object
            university_quotas[quota_id] = UniversityQuota(quota_id, quota_size, ranking)
    
    return university_quotas