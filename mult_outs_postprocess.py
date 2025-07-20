import numpy as np
import os
import glob
import rasterio

# Desired shape: (timesteps, channel/band, h, w)

# function to convert geotiff to numpy array
def tif_to_npy(file_path, handle_nodata=True):
    """
    Load a GeoTIFF file as a numpy array, optionally handling NoData values
    """
    with rasterio.open(file_path) as src:
        data = src.read(1)
        # replace nodata values with nan if there are some
        if handle_nodata and src.nodata is not None:
            data = np.where(data==src.nodata, np.nan, data)

        return data, src.meta

# function to load multiptle timesteps
def load_mult_timestep_elmfire_data(base_dir, variable_name):
    """
    Load data from multiple simulation timesteps
    
    Parameters:
    - base_dir: Path to mult_timestep_outputs directory
    - variable_name: 'time_of_arrival', 'flin', or 'vs'
    """
    timestep_dirs = glob.glob(os.path.join(base_dir, 'sim_*'))

    # function to extract timestep for proper sorting
    def extract_timestep(dir_name):
        basename = os.path.basename(dir_name)
        timestep_str = basename.replace('sim_', '').replace('s', '')
        return int(timestep_str)
    
    # sort mult_outputs_dir by timestep
    timestep_dirs.sort(key=extract_timestep)

    sim_data = []
    sim_metadata = []
    timestep_metadata = []


    for ts_dir in timestep_dirs:
        # get timestep seconds from directory name to store
        timestep_seconds = int(os.path.basename(ts_dir).replace('sim_', '').replace('s', ''))
        timestep_hours = timestep_seconds / 3600.0

        # find the files
        pattern = os.path.join(ts_dir, f'{variable_name}_*.tif')
        files = glob.glob(pattern)

        # if the files exist, take the first match and then convert to np and
        # append data to lists
        if files:
            file_path = files[0]
            # 
            try:
                data, metadata = tif_to_npy(file_path)
                sim_data.append(data)
                sim_metadata.append({
                    'seconds': timestep_seconds,
                    'hours': timestep_hours,
                    'file': file_path
                })
                timestep_metadata.append(metadata)
                print(f"Loaded timestep {timestep_hours:.1f}h: {data.shape}")
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        else:
            print(f"No {variable_name} file found in {ts_dir}")

    # convert sim_data to numpy array
    return sim_data, sim_metadata, timestep_metadata

# load all 3 data types that we want, and load the fuel data (array and meta)
# if it's the last timestep because they're all the same and cat to be the
# desired shape: (timesteps, channel/band, h, w)
desired_vars = ['flin', 'time_of_arrival', 'vs']

all_fire_vars = []
all_fire_meta = []

for var in desired_vars:
    var_data, sim_metadata, timestep_metadata = load_mult_timestep_elmfire_data(
        base_dir='mult_timestep_outputs',
        variable_name=var
    )
    stacked_var = np.stack(var_data, axis=0)  # shape: (timesteps, h, w)
    all_fire_vars.append(stacked_var)
    all_fire_meta.append({'var': var, 'meta': timestep_metadata})

# get the number of timesteps for each variable
ts_counts = [len(data) for data in all_fire_vars]

# raise an error if the number of timesteps is not the same for all variables
if len(set(ts_counts)) != 1:
    raise ValueError("All variables must have the same number of timesteps")

fuel_array, fuel_meta = tif_to_npy('./inputs/fbfm40.tif', handle_nodata=False)
num_timesteps = ts_counts[0]

if num_timesteps>1 and fuel_array is not None:
    # fuel_array is (h, w), we need to expand it to (timesteps, h, w)
    # assuming the number of timesteps is the same as the first variable
    fuel_repeated = np.repeat(fuel_array[np.newaxis, ...], num_timesteps, axis=0)  # (timesteps, h, w)
else:
    # if num_timesteps is 1, we can just use the fuel_array as is
    fuel_repeated = fuel_array[np.newaxis, ...]

# concatenate all fire variables with the fuel data
# fuel_repeated should be (timesteps, h, w)
if len(all_fire_vars) > 0:
    all_fire_vars = [np.expand_dims(var, axis=1) for var in all_fire_vars]  # add channel dimension
    all_fire_vars = np.concatenate(all_fire_vars, axis=1)  # concatenate along channel dimension
    fuel_prepped = np.expand_dims(fuel_repeated, axis=1)  # add channel dimension
    all_fire_vars = np.concatenate([all_fire_vars, fuel_prepped], axis=1)

# save the processed data in cases directory
output_dir = './cases'
os.makedirs(output_dir, exist_ok=True)
case_dirs = glob.glob(os.path.join(output_dir, 'case_*'))

print(case_dirs)
if len(case_dirs)==0:
    print('no cases yet')
    new_case_num = 0
else:
    # get the maximum case number so we can save as the next case
    # function to extract case num for proper sorting
    def extract_casenum(dir_name):
        basename = os.path.basename(dir_name)
        timestep_str = basename.replace('case_', '')
        return int(timestep_str)
    # sort case_dirs by casenum
    case_nums = []
    case_nums = [extract_casenum(dir_name) for dir_name in case_dirs]
    # get the max case num
    max_case_num = max(case_nums)
    new_case_num = max_case_num + 1

# set output file path (going to save in cases directory as new case)
output_file = os.path.join(output_dir, f'case_{new_case_num}.npz')

# timesteps in case
ts_in_case = [entry['seconds'] for entry in sim_metadata]

# Prepare metadata (can be a dict, but must be converted for npz)
metadata = {
    'channels': ['flin', 'time_of_arrival', 'vs', 'fuel_model'],
    'timesteps_in_case': ts_in_case,
    'num_timesteps': num_timesteps,
    'fuel_meta': fuel_meta,
    'fire_meta': all_fire_meta
}

np.savez_compressed(output_file, fire_data=all_fire_vars, metadata=np.array([metadata], dtype=object))
print(f"Saved case {new_case_num} data to {output_file}")
