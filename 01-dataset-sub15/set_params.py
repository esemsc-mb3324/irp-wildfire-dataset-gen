# this script is intended to be used to set the following parameters for running elmfire
# fbfm40, ignition coordinates, slope, aspect, wind speed, wind direction, dead moisture contents,
# canopy cover, canopy height, canopy base height, canopy bulk density, live herbaceous moisture
# content, and live woody moisture content.
# the parameters are set in 01-run.sh and elmfire.data.in
# the parameters are set according to the ranges in input_ranges.txt

import sys
import numpy as np
import re

def set_parameters():
    # Get run number from command line argument
    if len(sys.argv) < 2:
        print("Usage: python set_params.py <run_number>")
        sys.exit(1)
    run_number = sys.argv[1]
    tstop = float(sys.argv[2]) if len(sys.argv) > 2 else 22100.0  # Default simulation stop time
    domain_size = float(sys.argv[3]) if len(sys.argv) > 3 else 3840.0  # Default domain size

    # Generate random parameters
    fuel_model = np.random.randint(1, 16)  # [1, 15]
    x_ign = np.random.uniform(-domain_size/2, domain_size/2)  # Middle 50% of domain [-1920, 1920]
    y_ign = np.random.uniform(-domain_size/2, domain_size/2)  # Middle 50% of domain [-1920, 1920]
    slope = np.random.randint(0, 46)  # [0, 45]
    aspect = np.random.randint(0, 361)  # [0, 360]

    # Float raster parameters
    wind_speed = np.random.uniform(0, 31) # [0, 30]
    wind_direction = np.random.uniform(0.0, 360.0) # [0, 360]
    m1_moisture = np.random.uniform(2.0, 40.0) # [2, 40]
    m10_moisture = np.random.uniform(2.0, 40.0) # [2, 40]
    m100_moisture = np.random.uniform(2.0, 40.0) # [2, 40]

    # Integer raster parameters
    canopy_cover = np.random.randint(0, 101)  # [0, 100]
    canopy_height = np.random.randint(0, 6)  # [0, 5] (each unit = 10m)
    # canopy_base_height must be < 3 and < canopy_height
    cbh_max = min(3, canopy_height)  # cbh_max is exclusive upper bound
    if cbh_max > 0:
        canopy_base_height = np.random.randint(0, cbh_max)
    else:
        canopy_base_height = 0
    canopy_bulk_density = np.random.randint(0, 41)  # [0, 40] in 100kg/m^3

    # Live moisture parameters
    live_herbaceous = np.random.uniform(30.0, 100.0) # [30, 100]
    live_woody = np.random.uniform(30.0, 100.0) # [30, 100]

    # Modify 01-run.sh
    with open('01-run.sh', 'r') as f:
        bash_content = f.read()

    # write in domain size
    bash_content = re.sub(r'DOMAINSIZE=[0-9.-]+', f'DOMAINSIZE={domain_size}', bash_content)
    bash_content = re.sub(r'SIMULATION_TSTOP=[0-9.-]+', f'SIMULATION_TSTOP={tstop}', bash_content)

    # Float rasters
    bash_content = re.sub(r'FLOAT_VAL\[1\]=[0-9.-]+', f'FLOAT_VAL[1]={wind_speed:.1f}', bash_content)
    bash_content = re.sub(r'FLOAT_VAL\[2\]=[0-9.-]+', f'FLOAT_VAL[2]={wind_direction:.1f}', bash_content)
    bash_content = re.sub(r'FLOAT_VAL\[3\]=[0-9.-]+', f'FLOAT_VAL[3]={m1_moisture:.1f}', bash_content)
    bash_content = re.sub(r'FLOAT_VAL\[4\]=[0-9.-]+', f'FLOAT_VAL[4]={m10_moisture:.1f}', bash_content)
    bash_content = re.sub(r'FLOAT_VAL\[5\]=[0-9.-]+', f'FLOAT_VAL[5]={m100_moisture:.1f}', bash_content)

    # Integer rasters
    bash_content = re.sub(r'INT_VAL\[1\]=\d+', f'INT_VAL[1]={slope}', bash_content)
    bash_content = re.sub(r'INT_VAL\[2\]=\d+', f'INT_VAL[2]={aspect}', bash_content)
    bash_content = re.sub(r'INT_VAL\[4\]=\d+', f'INT_VAL[4]={fuel_model}', bash_content)
    bash_content = re.sub(r'INT_VAL\[5\]=\d+', f'INT_VAL[5]={canopy_cover}', bash_content)
    bash_content = re.sub(r'INT_VAL\[6\]=\d+', f'INT_VAL[6]={canopy_height}', bash_content)
    bash_content = re.sub(r'INT_VAL\[7\]=\d+', f'INT_VAL[7]={canopy_base_height}', bash_content)
    bash_content = re.sub(r'INT_VAL\[8\]=\d+', f'INT_VAL[8]={canopy_bulk_density}', bash_content)

    # Live moisture content
    bash_content = re.sub(r'LH_MOISTURE_CONTENT=[0-9.-]+', f'LH_MOISTURE_CONTENT={live_herbaceous:.1f}', bash_content)
    bash_content = re.sub(r'LW_MOISTURE_CONTENT=[0-9.-]+', f'LW_MOISTURE_CONTENT={live_woody:.1f}', bash_content)

    with open('01-run.sh', 'w') as f:
        f.write(bash_content)

    # Modify elmfire.data.in
    with open('elmfire.data.in', 'r') as f:
        config_content = f.read()

    config_content = re.sub(r'X_IGN\(1\)\s*=\s*[0-9.-]+', f'X_IGN(1)      = {x_ign:.1f}', config_content)
    config_content = re.sub(r'Y_IGN\(1\)\s*=\s*[0-9.-]+', f'Y_IGN(1)      = {y_ign:.1f}', config_content)

    with open('elmfire.data.in', 'w') as f:
        f.write(config_content)

    # write the run number and parameters to a new line like a csv in input_tracking.txt
    with open('input_tracking.txt', 'a') as f:
        f.write(f"{run_number},{x_ign:.1f},{y_ign:.1f},{fuel_model},{slope},{aspect},{wind_speed:.1f},{wind_direction:.1f},"
                f"{m1_moisture:.1f},{m10_moisture:.1f},{m100_moisture:.1f},{canopy_cover},{canopy_height},"
                f"{canopy_base_height},{canopy_bulk_density},{live_herbaceous:.1f},{live_woody:.1f}\n")

set_parameters()