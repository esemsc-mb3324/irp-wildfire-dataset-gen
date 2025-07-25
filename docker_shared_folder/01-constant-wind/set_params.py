# this script is intended to be used to set the following parameters for running elmfire
# fbfm40, ignition coordinates, slope, aspect, wind speed, wind direction, dead moisture contents,
# canopy cover, canopy height, canopy base height, canopy bulk density, live herbaceous moisture
# content, and live woody moisture content.
# the parameters are set in 01-run.sh and elmfire.data.in
# the parameters are set according to the ranges in input_ranges.txt
import numpy as np
import re

def set_parameters():
   # Generate random parameters
   # Direct perturbations
   fuel_model = np.random.randint(1, 41)  # [1, 40]
   x_ign = np.random.uniform(-960, 960)  # Middle 50% of domain [-1920, 1920]
   y_ign = np.random.uniform(-960, 960)  # Middle 50% of domain [-1920, 1920]
   slope = np.random.randint(0, 46)  # [0, 45]
   aspect = np.random.randint(0, 361)  # [0, 360]
   
   # Float raster parameters
   wind_speed = np.random.uniform(-0.5, 30.5)
   wind_direction = np.random.uniform(0.0, 360.0)
   m1_moisture = np.random.uniform(1.0, 39.0)
   m10_moisture = np.random.uniform(1.0, 39.0)
   m100_moisture = np.random.uniform(1.0, 39.0)
   
   # Integer raster parameters
   canopy_cover = np.random.randint(0, 101)  # [0, 100]
   canopy_height = np.random.randint(0, 6)  # [0, 5]
   canopy_base_height = np.random.randint(0, canopy_height)  # [0, canopy_height]
   canopy_bulk_density = np.random.randint(0, 41)  # [0, 40]
   
   # Live moisture parameters
   live_herbaceous = np.random.uniform(30.0, 100.0)
   live_woody = np.random.uniform(30.0, 100.0)
   
   # Modify 01-run.sh
   with open('01-run.sh', 'r') as f:
       bash_content = f.read()
   
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

set_parameters()