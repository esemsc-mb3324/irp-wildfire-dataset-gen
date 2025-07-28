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
