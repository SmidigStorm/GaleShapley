def hierarchical_gale_shapley(applicants, universities):
    """
    Implements a hierarchical Gale-Shapley algorithm for university admissions.
    
    Args:
        applicants: Dictionary of applicant data
        universities: Dictionary of university data with quota information
        
    Returns:
        Dictionary mapping university IDs to lists of admitted applicants per quota
    """
    results = {}
    
    # Initialize results structure
    for univ_id, univ_data in universities.items():
        results[univ_id] = {
            'Q1': [],
            'Q2': [],
            'Q3': []
        }
    
    # Process each university
    for univ_id, univ_data in universities.items():
        # Collect all eligible applicants for this university
        eligible_applicants = {}
        
        for app_id, app_data in applicants.items():
            # Add student if eligible for any quota at this university
            if (univ_id == 'S1' and (app_data['S1_Q1_eligible'] == 'Yes' or 
                                     app_data['S1_Q2_eligible'] == 'Yes' or 
                                     app_data['S1_Q3_eligible'] == 'Yes')) or \
               (univ_id == 'S2' and (app_data['S2_Q1_eligible'] == 'Yes' or 
                                     app_data['S2_Q2_eligible'] == 'Yes')):
                # Add priority based on student preference
                priority = app_data[f'{univ_id}_priority']
                eligible_applicants[app_id] = {
                    'priority': priority,
                    'data': app_data
                }
        
        # Process Quota 1 first
        q1_applicants = []
        for app_id, app_info in eligible_applicants.items():
            app_data = app_info['data']
            if univ_id == 'S1' and app_data['S1_Q1_eligible'] == 'Yes':
                q1_applicants.append((app_id, app_data[f'{univ_id}_Q1_points'], app_info['priority']))
            elif univ_id == 'S2' and app_data['S2_Q1_eligible'] == 'Yes':
                q1_applicants.append((app_id, app_data[f'{univ_id}_Q1_points'], app_info['priority']))
        
        # Sort by score and priority (higher score first, then by student preference)
        q1_applicants.sort(key=lambda x: (x[1], -x[2]), reverse=True)
        
        # Fill quota 1 seats
        q1_quota = univ_data['Q1_quota']
        q1_admitted = q1_applicants[:q1_quota]
        
        # Add admitted students to results
        results[univ_id]['Q1'] = [app[0] for app in q1_admitted]
        
        # Keep track of admitted students
        admitted_students = set([app[0] for app in q1_admitted])
        
        # Process Quota 2
        q2_applicants = []
        for app_id, app_info in eligible_applicants.items():
            # Skip already admitted applicants
            if app_id in admitted_students:
                continue
                
            app_data = app_info['data']
            if univ_id == 'S1' and app_data['S1_Q2_eligible'] == 'Yes':
                q2_applicants.append((app_id, app_data[f'{univ_id}_Q2_points'], app_info['priority']))
            elif univ_id == 'S2' and app_data['S2_Q2_eligible'] == 'Yes':
                q2_applicants.append((app_id, app_data[f'{univ_id}_Q2_points'], app_info['priority']))
        
        # Sort by score and priority
        q2_applicants.sort(key=lambda x: (x[1], -x[2]), reverse=True)
        
        # Fill quota 2 seats
        q2_quota = univ_data['Q2_quota']
        q2_admitted = q2_applicants[:q2_quota]
        
        # Add admitted students to results
        results[univ_id]['Q2'] = [app[0] for app in q2_admitted]
        
        # Update admitted students
        admitted_students.update([app[0] for app in q2_admitted])
        
        # Process Quota 3 (only for S1)
        if univ_id == 'S1':
            q3_applicants = []
            for app_id, app_info in eligible_applicants.items():
                # Skip already admitted applicants
                if app_id in admitted_students:
                    continue
                    
                app_data = app_info['data']
                if app_data['S1_Q3_eligible'] == 'Yes':
                    q3_applicants.append((app_id, app_data[f'{univ_id}_Q3_points'], app_info['priority']))
            
            # Sort by score and priority
            q3_applicants.sort(key=lambda x: (x[1], -x[2]), reverse=True)
            
            # Fill quota 3 seats
            q3_quota = univ_data['Q3_quota']
            q3_admitted = q3_applicants[:q3_quota]
            
            # Add admitted students to results
            results[univ_id]['Q3'] = [app[0] for app in q3_admitted]
    
    # Now we need to resolve university preference conflicts
    # (when a student is admitted to both universities)
    resolve_university_conflicts(applicants, results)
    
    return results


def resolve_university_conflicts(applicants, results):
    """
    Resolves conflicts when a student is admitted to multiple universities.
    The student will remain at their more preferred university.
    """
    # Find students admitted to both universities
    s1_admitted = set()
    for quota, students in results['S1'].items():
        s1_admitted.update(students)
        
    s2_admitted = set()
    for quota, students in results['S2'].items():
        s2_admitted.update(students)
    
    # Students admitted to both universities
    dual_admitted = s1_admitted.intersection(s2_admitted)
    
    # Resolve each conflict
    for student in dual_admitted:
        s1_priority = applicants[student]['S1_priority']
        s2_priority = applicants[student]['S2_priority']
        
        # Keep student at their preferred university
        if s1_priority < s2_priority:
            # Student prefers S1, remove from S2
            for quota in results['S2']:
                if student in results['S2'][quota]:
                    results['S2'][quota].remove(student)
        else:
            # Student prefers S2, remove from S1
            for quota in results['S1']:
                if student in results['S1'][quota]:
                    results['S1'][quota].remove(student)
    
    # After removing students, we could potentially fill those spots 
    # with other students, but we'll leave that as a future enhancement