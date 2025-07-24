# this script is intended to be used to set the following parameters for running elmfire
# 1. fuel model (fbfm40)
# - must be set as an integer in the range [1,40] in 01-run.sh 
#   at this location: INT_RASTER[4]=fbfm40  ; INT_VAL[4]=x where x is the fuel model code
# 2. x ignition coordinate (X_IGN(1))
# - must be set as a float in elmfire.data.in in the &SIMULATOR section at this
#   location: X_IGN(1) = x where x is the ignition coordinate in meters
# 3. y ignition coordinate (Y_IGN(1))
# - must be set as a float in elmfire.data.in in the &SIMULATOR section at this
#   location: Y_IGN(1) = y where y is the ignition coordinate in meters
# 4. slope (slp)
# - must be set as an integer in the range [0,90] in 01-run.sh 
#   at this location: INT_RASTER[1]=slp     ; INT_VAL[1]=x where x is the slope in degrees
# 5. aspect (asp)
# - must be set as an integer in the range [0,360] in 01-run.sh 
#   at this location: INT_RASTER[2]=asp     ; INT_VAL[2]=x where x is the aspect in degrees

import os
import sys
import numpy as np
import re

def set_parameters():
   # Generate random parameters
   fuel_model = np.random.randint(1, 41)  # [1, 40]
   x_ign = np.random.uniform(-960, 960)  # Middle 50% of domain [-1920, 1920]
   y_ign = np.random.uniform(-960, 960)  # Middle 50% of domain [-1920, 1920]
   slope = np.random.randint(0, 91)  # [0, 90]
   aspect = np.random.randint(0, 361)  # [0, 360]
   
   # Modify 01-run.sh
   with open('01-run.sh', 'r') as f:
       bash_content = f.read()
   
   bash_content = re.sub(r'INT_VAL\[1\]=\d+', f'INT_VAL[1]={slope}', bash_content)
   bash_content = re.sub(r'INT_VAL\[2\]=\d+', f'INT_VAL[2]={aspect}', bash_content)
   bash_content = re.sub(r'INT_VAL\[4\]=\d+', f'INT_VAL[4]={fuel_model}', bash_content)
   
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