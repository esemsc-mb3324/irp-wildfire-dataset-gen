import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
from matplotlib import cm
import pandas as pd
import seaborn as sns

import glob
import rasterio

case_dir = './cases'

# prints max and min for raster files of a case
def print_case_info(case_num):
    case_path = f'{case_dir}/case_{case_num}'
    print(f'Case {case_num} path: {case_path}')
    
    patterns = ["flin_*.tif", "time_of_arrival_*.tif", "vs_*.tif"]

    for pattern in patterns:
        for filepath in glob.glob(f"{case_path}/{pattern}"):
            with rasterio.open(filepath) as src:
                data = src.read(1)
                print(f"{filepath}: shape={data.shape}, min={data.min()}, max={data.max()}")

# prints case info for all cases
def print_all_cases_info(num_cases, max_cases=10):
    for i in range(1, min(num_cases, max_cases) + 1):
        print_case_info(i)

# plot rasters for one case
def plot_case(case_num):
    case_path = f'{case_dir}/case_{case_num}'
    # plot the three rasters
    flin_files = glob.glob(f"{case_path}/flin_*.tif")
    time_files = glob.glob(f"{case_path}/time_of_arrival_*.tif")
    vs_files = glob.glob(f"{case_path}/vs_*.tif")

    if flin_files and time_files and vs_files:
        flin_file = flin_files[0]
        time_file = time_files[0]
        vs_file = vs_files[0]

        with rasterio.open(flin_file) as src:
            flin_data = src.read(1)
        
        with rasterio.open(time_file) as src:
            time_data = src.read(1)
        
        with rasterio.open(vs_file) as src:
            vs_data = src.read(1)

        # Plotting the rasters
        fig, axs = plt.subplots(1, 3, figsize=(15, 5))
        
        axs[0].imshow(flin_data, cmap='hot')
        axs[0].set_title('Flame Length (flin)')
        
        axs[1].imshow(time_data, cmap='viridis')
        axs[1].set_title('Time of Arrival')
        
        axs[2].imshow(vs_data, cmap='coolwarm')
        axs[2].set_title('Spread Rate (vs)')
        
        plt.tight_layout()
        plt.show()
    else:
        print("One or more output files not found. Please check the output directory and file patterns.")

# plot all of one raster type for all cases in a grid
def plot_all_cases_raster(pattern, num_cases, max_cols=5):
    print(f'Plotting all cases for raster pattern: {pattern}')
    fig, axes = plt.subplots(nrows=1, ncols=max_cols, figsize=(15, 5))
    for i in range(1, min(num_cases, max_cols) + 1):
        case_path = f'{case_dir}/case_{i}'
        filepath = glob.glob(f"{case_path}/{pattern}")
        if filepath:
            with rasterio.open(filepath[0]) as src:
                data = src.read(1)
                ax = axes[i - 1]
                show(data, ax=ax, cmap=cm.viridis)
                ax.set_title(f"Case {i}")
                ax.set_axis_off()
    plt.tight_layout()
    plt.show()
    
# plot the distribution of all of the input parameters for all cases
# run,xign,yign,fuel,slp,asp,ws,wd,m1,m10,m100,cc,ch,cbh,cbd,lhc,lwc in input_tracking.txt
def plot_input_distribution():

    input_file = 'input_tracking.txt'
    df = pd.read_csv(input_file)

    print(f'Input parameters distribution from {input_file}:')
    print(df.describe())

    # Plotting the distributions of each parameter
    plt.figure(figsize=(15, 10))
    for i, column in enumerate(df.columns[1:], start=1):
        plt.subplot(4, 4, i)
        sns.histplot(df[column], kde=True)
        plt.title(column)
        plt.xlabel('')
        plt.ylabel('Frequency')
    
    plt.tight_layout()
    plt.show()

# for each input, plot with run number on x-axis
def plot_input_vs_run():
    input_file = 'input_tracking.txt'
    df = pd.read_csv(input_file)

    print(f'Input parameters vs Run number from {input_file}:')
    print(df.describe())

    # Plotting each parameter against run number
    plt.figure(figsize=(15, 10))
    for i, column in enumerate(df.columns[1:], start=1):
        plt.subplot(4, 4, i)
        sns.lineplot(x=df.index + 1, y=df[column])
        plt.title(column)
        plt.xlabel('Run Number')
        plt.ylabel(column)
    
    plt.tight_layout()
    plt.show()

# quick check to make sure all of the input parameters are within the expected ranges
# from input_tracking.txt: run,xign,yign,fuel,slp,asp,ws,wd,m1,m10,m100,cc,ch,cbh,cbd,lhc,lwc
# id,name,init_value,negative_perturb,upper_perturb,range,notes
# WS,wind_speed,15.0,-15.5,15.5,[−0.5,30.5],
# WD,wind_direction,180.0,-180.0,180.0,[0.0,360.0],
# M1,m1_moisture,20.0,-19.0,19.0,[1.0,39.0],
# M10,m10_moisture,20.0,-19.0,19.0,[1.0,39.0],
# M100,m100_moisture,20.0,-19.0,19.0,[1.0,39.0],
# MLH,live_herbaceous,65.0,-35.0,35.0,[30.0,100.0],
# MLW,live_woody,65.0,-35.0,35.0,[30.0,100.0],
# CC,canopy_cover,50,-50.0,50.0,[0,100],
# CH,canopy_height,2,-2.0,3.0,[0,5],
# CBH,canopy_base_height,1,-1.0,1.0,[0,canopy_height],
# CBD,canopy_bulk_density,20,-20.0,20.0,[0,40],
# SLP,slope,0,-,-,[0,45],# perturbed directly
# ASP,aspect,0,-,-,[0,360],# perturbed directly
# FBFM40,fuel_model,1,-,-,[1,40],# perturbed directly
# DEM,elevation,0,-,-,[0,0],# not perturbed
def check_input_ranges():
    input_file = 'input_tracking.txt'
    df = pd.read_csv(input_file)

    print(f'Checking input parameter ranges from {input_file}:')
    print(df.columns)
    
    # Define expected ranges
    expected_ranges = {
        'ws': (0, 30.5),
        'wd': (0.0, 360.0),
        'm1': (1.0, 39.0),
        'm10': (1.0, 39.0),
        'm100': (1.0, 39.0),
        'lhc': (30.0, 100.0),
        'lwc': (30.0, 100.0),
        'cc': (0, 100),
        'ch': (0, 5),
        'cbh': (0, 2),  # Canopy base height should not exceed canopy height
        'cbd': (0, 40),
        'slp': (0, 45),
        'asp': (0, 360),
        'fuel': (1, 40)
    }
    for column in df.columns[1:]:
        if column in expected_ranges:
            min_val, max_val = expected_ranges[column]
            if not df[column].between(min_val, max_val).all():
                print(f"Warning: {column} values out of range: {df[column].min()} to {df[column].max()}")
            else:
                print(f"{column} values are within the expected range: {min_val} to {max_val}")
        else:
            print(f"{column} is not a recognized input parameter.")
