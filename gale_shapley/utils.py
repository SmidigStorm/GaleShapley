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
        
        # Check eligibility for S1 and its quotas
        s1_program_eligible = app_data.get('S1_Kvalifisert?') == 'Ja'
        
        if s1_program_eligible:
            if 'S1_Q1_eligible' in app_data and app_data['S1_Q1_eligible'] == 'Yes':
                quota_options.append(('S1_Q1', s1_priority, 1))
            if 'S1_Q2_eligible' in app_data and app_data['S1_Q2_eligible'] == 'Yes':
                quota_options.append(('S1_Q2', s1_priority, 2))
            if 'S1_Q3_eligible' in app_data and app_data['S1_Q3_eligible'] == 'Yes':
                quota_options.append(('S1_Q3', s1_priority, 3))
        
        # Check eligibility for S2 and its quotas
        s2_program_eligible = app_data.get('S2_Kvalifisert?') == 'Ja'
            
        if s2_program_eligible:
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
                # Check base eligibility for the study program
                program_eligibility_key = f"{univ_id}_Kvalifisert?"
                
                # Check quota-specific eligibility
                quota_eligibility_key = f"{univ_id}_{quota_name}_eligible"
                points_key = f"{univ_id}_{quota_name}_points"
                
                # Student must be eligible for both the program AND the specific quota
                if (
                    program_eligibility_key in app_data and
                    app_data[program_eligibility_key] == 'Ja' and
                    quota_eligibility_key in app_data and 
                    app_data[quota_eligibility_key] == 'Yes' and 
                    points_key in app_data
                ):
                    points = int(app_data[points_key])
                    eligible_students.append((app_id, points))
            
            # Sort by points (higher points = higher ranking)
            eligible_students.sort(key=lambda x: x[1], reverse=True)
            
            # Create ranking list - ONLY including eligible students
            ranking = [student[0] for student in eligible_students]
            
            # Create UniversityQuota object
            university_quotas[quota_id] = UniversityQuota(quota_id, quota_size, ranking)
    
    return university_quotas

def handle_guaranteed_students(matching, raw_applicants, gs_applicants, university_quotas):
    """
    Ensure that guaranteed students are offered a place according to their preferences,
    placing them in the rightmost (lowest priority) quota that has spots.
    
    Args:
        matching: Current matching result from the algorithm
        raw_applicants: Raw applicant data from CSV
        gs_applicants: Gale-Shapley applicant objects
        university_quotas: Gale-Shapley university quota objects
        
    Returns:
        Updated matching dictionary
    """
    # Find which students have guarantees for which universities
    students_with_guarantees = {}
    
    for app_id, app_data in raw_applicants.items():
        guaranteed_universities = []
        
        if app_data.get('S1_guaranteed') == 'Yes':
            guaranteed_universities.append('S1')
        if app_data.get('S2_guaranteed') == 'Yes':
            guaranteed_universities.append('S2')
        
        if guaranteed_universities:
            students_with_guarantees[app_id] = guaranteed_universities
    
    # If no students have guarantees, no action needed
    if not students_with_guarantees:
        return matching
    
    # For each student with guarantees
    for student_id, guaranteed_univs in students_with_guarantees.items():
        # Check where (if anywhere) the student is currently matched
        current_match = None
        current_match_quota = None
        
        for quota_id, matches in matching.items():
            if student_id in matches:
                current_match = quota_id.split('_')[0]  # Extract university part
                current_match_quota = quota_id
                break
        
        # Get student's preference order for universities
        university_preferences = []
        for pref in gs_applicants[student_id].preferences:
            univ = pref.split('_')[0]
            if univ in guaranteed_univs and univ not in university_preferences:
                university_preferences.append(univ)
        
        # If student is already matched to their highest preferred guaranteed university, no action needed
        if current_match in university_preferences:
            current_univ_index = university_preferences.index(current_match)
            if current_univ_index == 0:  # Already in highest preferred guaranteed university
                continue
        
        # Student needs to be placed in a guaranteed spot
        # Try each guaranteed university in preference order
        for guaranteed_univ in university_preferences:
            # Find all quotas for this university that the student is eligible for
            eligible_quotas = []
            
            for quota_id in matching.keys():
                univ_id, quota_name = quota_id.split('_', 1)
                
                if univ_id == guaranteed_univ:
                    program_eligibility_key = f"{univ_id}_Kvalifisert?"
                    quota_eligibility_key = f"{univ_id}_{quota_name}_eligible"
                    
                    if (raw_applicants[student_id].get(program_eligibility_key) == 'Ja' and
                        raw_applicants[student_id].get(quota_eligibility_key) == 'Yes'):
                        eligible_quotas.append(quota_id)
            
            # Sort quotas by name in reverse order (Q3, Q2, Q1) to prioritize rightmost quota
            eligible_quotas.sort(reverse=True)
            
            # Try to place student in eligible quotas
            for quota_id in eligible_quotas:
                # Remove from current match if any
                if current_match_quota and student_id in matching[current_match_quota]:
                    matching[current_match_quota].remove(student_id)
                    current_match_quota = None
                
                # Add student to this quota
                if len(matching[quota_id]) < university_quotas[quota_id].quota:
                    # There's space available
                    matching[quota_id].append(student_id)
                    current_match_quota = quota_id
                    break
                else:
                    # Need to remove the lowest-ranked student
                    quota_preferences = university_quotas[quota_id].preferences
                    
                    # Find the lowest-ranked student currently matched
                    current_matches = matching[quota_id]
                    lowest_ranked = None
                    lowest_rank = -1
                    
                    for match_id in current_matches:
                        if match_id in quota_preferences:
                            rank = quota_preferences.index(match_id)
                            if lowest_ranked is None or rank > lowest_rank:
                                lowest_ranked = match_id
                                lowest_rank = rank
                    
                    # Replace the lowest-ranked student
                    if lowest_ranked:
                        matching[quota_id].remove(lowest_ranked)
                        matching[quota_id].append(student_id)
                        current_match_quota = quota_id
                        break
            
            # If we successfully placed the student, break out of the university loop
            if current_match_quota:
                break
    
    return matching