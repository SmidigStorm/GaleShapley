import json
import csv
import os

def load_preferences_from_json(filename):
    """
    Load applicant and university preferences from a JSON file.
    
    Args:
        filename: Path to JSON file
        
    Returns:
        Tuple of (applicants, universities) dictionaries
    """
    with open(filename, 'r') as f:
        data = json.load(f)
    
    from src.models import Applicant, University
    
    applicants = {}
    for applicant_id, prefs in data.get('applicants', {}).items():
        applicants[applicant_id] = Applicant(applicant_id, prefs)
    
    universities = {}
    for university_id, univ_data in data.get('universities', {}).items():
        universities[university_id] = University(
            university_id, 
            univ_data.get('quota', 1), 
            univ_data.get('preferences', [])
        )
    
    return applicants, universities

def save_matching_to_json(matching, filename):
    """
    Save matching results to a JSON file.
    
    Args:
        matching: Dictionary of university IDs to lists of applicant IDs
        filename: Path to save JSON file
    """
    # Convert any non-serializable types to strings
    serializable_matching = {}
    for univ_id, applicant_ids in matching.items():
        serializable_matching[str(univ_id)] = [str(a_id) for a_id in applicant_ids]
    
    with open(filename, 'w') as f:
        json.dump(serializable_matching, f, indent=2)

def load_preferences_from_csv(applicants_file, universities_file):
    """
    Load applicant and university preferences from CSV files.
    
    Args:
        applicants_file: Path to applicants CSV file
        universities_file: Path to universities CSV file
        
    Returns:
        Tuple of (applicants, universities) dictionaries
    """
    from src.models import Applicant, University
    
    applicants = {}
    with open(applicants_file, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header
        
        for row in reader:
            applicant_id = row[0]
            preferences = row[1:] if len(row) > 1 else []
            preferences = [p for p in preferences if p]  # Remove empty preferences
            applicants[applicant_id] = Applicant(applicant_id, preferences)
    
    universities = {}
    with open(universities_file, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header
        
        for row in reader:
            if len(row) < 3:  # Need at least ID, quota, and 1 preference
                continue
                
            university_id = row[0]
            quota = int(row[1])
            preferences = row[2:] if len(row) > 2 else []
            preferences = [p for p in preferences if p]  # Remove empty preferences
            universities[university_id] = University(university_id, quota, preferences)
    
    return applicants, universities

def format_matching_result(matching, applicants, universities):
    """
    Format matching results for display.
    
    Args:
        matching: Dictionary of university IDs to lists of applicant IDs
        applicants: Dictionary of Applicant objects
        universities: Dictionary of University objects
        
    Returns:
        Formatted string showing matches
    """
    result = "Matching Results:\n"
    result += "=" * 50 + "\n"
    
    for university_id, matched_applicants in matching.items():
        university = universities[university_id]
        result += f"University {university_id} (Quota: {university.quota}):\n"
        
        if not matched_applicants:
            result += "  No matched applicants\n"
        else:
            for applicant_id in matched_applicants:
                applicant = applicants[applicant_id]
                university_rank = applicant.preferences.index(university_id) + 1 if university_id in applicant.preferences else "N/A"
                applicant_rank = university.preferences.index(applicant_id) + 1 if applicant_id in university.preferences else "N/A"
                
                result += f"  - Applicant {applicant_id} "
                result += f"(University's {applicant_rank} choice, "
                result += f"Applicant's {university_rank} choice)\n"
        
        result += "\n"
    
    # List unmatched applicants
    unmatched = []
    for applicant_id, applicant in applicants.items():
        is_matched = False
        for matches in matching.values():
            if applicant_id in matches:
                is_matched = True
                break
        
        if not is_matched:
            unmatched.append(applicant_id)
    
    if unmatched:
        result += "Unmatched Applicants:\n"
        for applicant_id in unmatched:
            result += f"  - Applicant {applicant_id}\n"
    
    return result