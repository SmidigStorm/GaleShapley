# Gale-Shapley University Admissions

This package implements the Gale-Shapley algorithm for solving the stable matching problem in university admissions with multiple quota categories.

## Features

- Implementation of the Gale-Shapley algorithm for stable matching
- Support for multiple universities with different quota categories
- Customizable student preferences and university rankings
- Support for eligibility requirements for different quota categories
- Comprehensive reporting and result analysis

# Basic Usage
```bash
# Run with default data files
python main.py

# Enable verbose output for more details
python main.py --verbose
```

# Custom Input Files
```bash
# Specify custom input files
python main.py --applicants data/input/custom_applicants.csv --universities data/input/custom_universities.csv

# Specify custom output location
python main.py --output data/output/custom_results.md
```