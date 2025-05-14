import csv
import os

def load_data(applicants_file, universities_file):
    """
    Load applicant and university data from CSV files.
    """
    applicants = {}
    with open(applicants_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            applicants[row['applicant_id']] = row
    
    universities = {}
    with open(universities_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            universities[row['university_id']] = {
                'Q1_quota': int(row['Q1_quota']),
                'Q2_quota': int(row['Q2_quota']),
                'Q3_quota': int(row['Q3_quota'] if 'Q3_quota' in row else 0)
            }
    
    return applicants, universities

def format_results(results, applicants):
    """
    Format the results for display.
    """
    output = "# Admission Results\n\n"
    
    # Count total admitted students
    total_admitted = set()
    for univ, quotas in results.items():
        for quota, students in quotas.items():
            total_admitted.update(students)
    
    output += f"Total students admitted: {len(total_admitted)} out of {len(applicants)}\n\n"
    
    # Display results per university and quota
    for univ, quotas in results.items():
        output += f"## {univ}\n\n"
        
        for quota, students in quotas.items():
            if quota == 'Q3' and univ == 'S2':
                continue  # Skip Q3 for S2 since it doesn't exist
                
            output += f"### {quota} (Capacity: {universities[univ][f'{quota}_quota']})\n"
            
            if not students:
                output += "- No students admitted\n\n"
                continue
                
            output += "| Student | Points |\n"
            output += "|---------|--------|\n"
            
            # Sort by points for display
            sorted_students = []
            for student in students:
                points = applicants[student][f"{univ}_{quota}_points"]
                sorted_students.append((student, points))
                
            sorted_students.sort(key=lambda x: int(x[1]), reverse=True)
            
            for student, points in sorted_students:
                output += f"| {student} | {points} |\n"
            
            output += "\n"
    
    # Display unmatched students
    unmatched = set(applicants.keys()) - total_admitted
    if unmatched:
        output += "## Unmatched Students\n\n"
        for student in sorted(unmatched):
            output += f"- {student}\n"
    
    return output

if __name__ == "__main__":
    # Ensure data directories exist
    os.makedirs('data/input', exist_ok=True)
    os.makedirs('data/output', exist_ok=True)
    
    # Create applicants.csv file
    with open('data/input/applicants.csv', 'w') as f:
        f.write("applicant_id,S1_priority,S2_priority,S1_Q1_eligible,S1_Q2_eligible,S1_Q3_eligible,S1_Q1_points,S1_Q2_points,S1_Q3_points,S2_Q1_eligible,S2_Q2_eligible,S2_Q1_points,S2_Q2_points\n")
        f.write("Tesla,1,2,No,No,Yes,55,50,55,No,Yes,50,55\n")
        f.write("Edison,2,1,No,No,Yes,50,50,50,No,Yes,50,50\n")
        f.write("Bell,1,2,No,No,Yes,50,40,50,No,Yes,40,50\n")
        f.write("Turing,1,2,No,Yes,Yes,40,30,40,Yes,Yes,30,40\n")
        f.write("Jobs,1,2,No,Yes,Yes,35,35,35,Yes,Yes,35,35\n")
        f.write("Franklin,2,1,No,Yes,Yes,30,45,30,Yes,Yes,45,30\n")
        f.write("Einstein,1,2,No,Yes,Yes,30,30,30,Yes,Yes,30,30\n")
        f.write("DaVinci,2,1,Yes,Yes,Yes,30,30,30,Yes,Yes,30,30\n")
        f.write("Curie,1,2,No,Yes,Yes,30,20,30,Yes,Yes,20,30\n")
        f.write("Newton,2,1,No,Yes,Yes,30,10,30,Yes,Yes,10,30\n")
    
    # Create universities.csv file
    with open('data/input/universities.csv', 'w') as f:
        f.write("university_id,Q1_quota,Q2_quota,Q3_quota\n")
        f.write("S1,1,3,6\n")
        f.write("S2,4,6,0\n")
    
    # Load data
    applicants, universities = load_data('data/input/applicants.csv', 'data/input/universities.csv')
    
    # Run hierarchical algorithm
    from hierarchical_algorithm import hierarchical_gale_shapley
    results = hierarchical_gale_shapley(applicants, universities)
    
    # Format and display results
    output = format_results(results, applicants)
    print(output)
    
    # Save results to file
    with open('data/output/results.md', 'w') as f:
        f.write(output)
    
    print("\nResults saved to data/output/results.md")