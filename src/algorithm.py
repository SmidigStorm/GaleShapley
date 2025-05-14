def gale_shapley_matching(applicants, universities):
    """
    Implements the Gale-Shapley algorithm for stable matching.
    
    Args:
        applicants: Dictionary of Applicant objects keyed by ID
        universities: Dictionary of University objects keyed by ID
        
    Returns:
        Dictionary mapping university IDs to lists of applicant IDs
    """
    # Create a queue of free applicants
    free_applicants = list(applicants.keys())
    
    # Continue until there are no free applicants left or all have exhausted preferences
    while free_applicants:
        applicant_id = free_applicants.pop(0)
        applicant = applicants[applicant_id]
        
        # Get next university to propose to
        university_id = applicant.get_next_preference()
        
        # If applicant has exhausted preferences, continue to next applicant
        if university_id is None:
            continue
        
        university = universities[university_id]
        
        # Try to match applicant with university
        rejected_id = university.add_applicant(applicant_id)
        
        if rejected_id is None or rejected_id != applicant_id:
            # Applicant was accepted
            applicant.current_match = university_id
            
            # If another applicant was rejected, add them back to free applicants
            if rejected_id is not None and rejected_id != applicant_id:
                applicants[rejected_id].current_match = None
                free_applicants.append(rejected_id)
        else:
            # Applicant was rejected, put back in the queue
            free_applicants.append(applicant_id)
    
    # Build the final matching result
    result = {}
    for university_id, university in universities.items():
        result[university_id] = university.current_matches.copy()
    
    return result