#!/usr/bin/env python3
"""
Simple configuration for ELMFIRE postprocessing.
Modify these variables to change processing settings.
"""

# Input/Output Directories
CASES_DIR = './cases'                    # Directory containing case_# subdirectories
OUTPUT_DIR = './elmfire_sims'            # Output directory for processed simulations

# Processing Parameters
TIMESTEP_MINUTES = 15                    # Timestep interval in minutes
MAX_TIME_HOURS = 72.0                    # Maximum simulation time in hours (72hr = 259200s)

# Variables to Process
# Available options: 'toa', 'burnscar', 'flin', 'vs'
VARIABLES = [
    'toa',           # Time of arrival
    'burnscar',     # Binary burn scar (derived from TOA)
    'flin',          # Fireline intensity 
    'vs'             # Spread rate
]

# File Handling
NODATA_VALUE = -9999                     # Standard nodata value

if __name__ == "__main__":
    print("ELMFIRE Postprocessor Configuration")
    print(f"Cases directory: {CASES_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Variables: {VARIABLES}")
    print(f"Timestep: {TIMESTEP_MINUTES} minutes")
    print(f"Max time: {MAX_TIME_HOURS} hours")