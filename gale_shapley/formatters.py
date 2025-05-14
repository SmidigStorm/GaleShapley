def format_results_markdown(matching, gs_applicants, university_quotas, raw_applicants):
    """
    Format matching results as markdown.
    
    Args:
        matching: Dictionary mapping university quota IDs to lists of applicant IDs
        gs_applicants: Dictionary of Applicant objects
        university_quotas: Dictionary of UniversityQuota objects
        raw_applicants: Dictionary of raw applicant data from CSV
        
    Returns:
        Markdown formatted string with results
    """
    output = "# Admission Results\n\n"
    
    # Count total admitted students
    total_admitted = set()
    for quota_id, admitted_students in matching.items():
        total_admitted.update(admitted_students)
    
    output += f"Total students admitted: {len(total_admitted)} out of {len(gs_applicants)}\n\n"
    
    # Group results by university
    university_results = {}
    
    for quota_id, admitted_students in matching.items():
        # Parse university ID and quota name
        parts = quota_id.split('_')
        univ_id = parts[0]
        quota_name = '_'.join(parts[1:])
        
        # Initialize university data if not exists
        if univ_id not in university_results:
            university_results[univ_id] = {}
        
        university_results[univ_id][quota_name] = admitted_students
    
    # Display results per university and quota
    for univ_id, quotas in sorted(university_results.items()):
        output += f"## {univ_id}\n\n"
        
        for quota_name, students in sorted(quotas.items()):
            quota_id = f"{univ_id}_{quota_name}"
            quota_size = university_quotas[quota_id].quota if quota_id in university_quotas else 0
            
            output += f"### {quota_name} (Capacity: {quota_size})\n"
            
            if not students:
                output += "- No students admitted\n\n"
                continue
                
            output += "| Student | Points |\n"
            output += "|---------|--------|\n"
            
            # Sort by points for display
            sorted_students = []
            for student in students:
                points_key = f"{univ_id}_{quota_name}_points"
                points = raw_applicants[student][points_key]
                sorted_students.append((student, int(points)))
                
            sorted_students.sort(key=lambda x: x[1], reverse=True)
            
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

def save_results(content, filepath):
    """
    Save content to a file.
    
    Args:
        content: Content to save
        filepath: Path to save file
    """
    with open(filepath, 'w') as f:
        f.write(content)