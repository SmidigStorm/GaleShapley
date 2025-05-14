class Applicant:
    """
    Represents an applicant in the matching problem.
    """
    def __init__(self, id, preferences=None):
        """
        Initialize an applicant.
        
        Args:
            id: Unique identifier for the applicant
            preferences: List of university IDs in order of preference
        """
        self.id = id
        self.preferences = preferences or []
        self.current_match = None
        self.next_to_propose = 0  # Index of next university to propose to
    
    def get_next_preference(self):
        """
        Get the next preferred university to apply to.
        
        Returns:
            The ID of the next university or None if preferences exhausted
        """
        if self.next_to_propose >= len(self.preferences):
            return None
        university_id = self.preferences[self.next_to_propose]
        self.next_to_propose += 1
        return university_id
    
    def __repr__(self):
        return f"Applicant({self.id})"
    
class University:
    """
    Represents a university in the matching problem.
    """
    def __init__(self, id, quota, preferences=None):
        """
        Initialize a university.
        
        Args:
            id: Unique identifier for the university
            quota: Number of available spots
            preferences: List of applicant IDs in order of preference
        """
        self.id = id
        self.quota = quota
        self.preferences = preferences or []
        self.current_matches = []  # List of currently matched applicants
    
    def prefers(self, applicant_id, current_match_id):
        """
        Check if university prefers a new applicant over another applicant.
        
        Args:
            applicant_id: ID of the applicant to check
            current_match_id: ID of an applicant to compare with
            
        Returns:
            True if university prefers applicant_id over current_match_id
        """
        applicant_rank = self.preferences.index(applicant_id) if applicant_id in self.preferences else float('inf')
        match_rank = self.preferences.index(current_match_id) if current_match_id in self.preferences else float('inf')
        return applicant_rank < match_rank
    
    def add_applicant(self, applicant_id):
        """
        Try to add an applicant to university's matches.
        
        Args:
            applicant_id: ID of applicant to add
            
        Returns:
            None if the applicant was added successfully
            ID of the rejected applicant if quota was already full
        """
        # If quota is not filled, accept the applicant
        if len(self.current_matches) < self.quota:
            self.current_matches.append(applicant_id)
            return None
        
        # Find the least preferred applicant among current matches
        least_preferred = None
        lowest_rank = -1
        
        for match_id in self.current_matches:
            match_rank = self.preferences.index(match_id) if match_id in self.preferences else float('inf')
            if least_preferred is None or match_rank > lowest_rank:
                least_preferred = match_id
                lowest_rank = match_rank
        
        # Check if new applicant is preferred over the least preferred match
        applicant_rank = self.preferences.index(applicant_id) if applicant_id in self.preferences else float('inf')
        
        if applicant_rank < lowest_rank:
            # Replace least preferred with new applicant
            self.current_matches.remove(least_preferred)
            self.current_matches.append(applicant_id)
            return least_preferred
        
        # Reject the new applicant
        return applicant_id
    
    def __repr__(self):
        return f"University({self.id}, quota={self.quota})"