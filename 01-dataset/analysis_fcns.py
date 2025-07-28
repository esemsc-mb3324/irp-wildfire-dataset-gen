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
        plt.subplot(4, 5, i)
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
        plt.subplot(4, 5, i)
        sns.lineplot(x=df.index + 1, y=df[column])
        plt.title(column)
        plt.xlabel('Run Number')
        plt.ylabel(column)
    
    plt.tight_layout()
    plt.show()

# quick check to make sure all of the input parameters are within the expected ranges
# from input_tracking.txt: run,xign,yign,fuel,slp,asp,ws,wd,m1,m10,m100,cc,ch,cbh,cbd,lhc,lwc, firearea
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
        'ws': (0, 31),
        'wd': (0.0, 360.0),
        'm1': (1.0, 40.0),
        'm10': (1.0, 40.0),
        'm100': (1.0, 40.0),
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
                # print value out of range
                out_of_range = df[~df[column].between(min_val, max_val)]
                print(f"Out of range values for {column}:\n{out_of_range[column]}")
            else:
                print(f"{column} values are within the expected range: {min_val} to {max_val}")
        else:
            print(f"{column} is not a recognized input parameter.")

# in the new input_tracking.txt this is the format: run,xign,yign,fuel,slp,asp,ws,wd,m1,m10,m100,cc,ch,cbh,cbd,lhc,lwc,firearea
# I want to analyze the way in which the fire area changes with the input parameters
def analyze_fire_area():
    input_file = 'it_scratch_fixed.txt'
    df = pd.read_csv(input_file)

    print(f'Analyzing fire area from {input_file}:')
    
    # Check if 'firearea' column exists
    if 'firearea' in df.columns:
        print(f"Fire area statistics:\n{df['firearea'].describe()}")
        
        # Plotting fire area against each input parameter
        plt.figure(figsize=(15, 10))
        for i, column in enumerate(df.columns[1:-1], start=1):  # Exclude 'run' and 'firearea'
            plt.subplot(4, 4, i)
            sns.scatterplot(x=df[column], y=df['firearea'])
            plt.title(f'Fire Area vs {column}')
            plt.xlabel(column)
            plt.ylabel('Fire Area')
        
        plt.tight_layout()
        plt.show()
    else:
        print("No 'firearea' column found in the input file.")

# get fire area covariance with each input parameter
def fire_area_covariance():
    input_file = 'it_scratch_fixed.txt'
    df = pd.read_csv(input_file)

    print(f'Calculating fire area covariance from {input_file}:')
    
    # Check if 'firearea' column exists
    if 'firearea' in df.columns:
        covariances = {}
        for column in df.columns[1:-1]:  # Exclude 'run' and 'firearea'
            cov = df['firearea'].cov(df[column])
            covariances[column] = cov
            print(f"Covariance between fire area and {column}: {cov}")
        
        return covariances
    else:
        print("No 'firearea' column found in the input file.")
        return None


# calculate correlation coefficient between fire area and each input parameter
# and plot heatmap of the correlation coefficients
def fire_area_correlation():
    input_file = 'it_scratch_fixed.txt'
    df = pd.read_csv(input_file)

    print(f'Calculating fire area correlation from {input_file}:')
    
    # Check if 'firearea' column exists
    if 'firearea' in df.columns:
        correlation_matrix = df.corr()
        fire_area_corr = correlation_matrix['firearea'].drop('firearea')
        
        print("Correlation coefficients with fire area:")
        print(fire_area_corr)
        
        # Plotting heatmap of the correlation coefficients
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
        plt.title('Correlation Coefficients Heatmap')
        plt.show()
    else:
        print("No 'firearea' column found in the input file.")
        return None
    

# select cases with the most fire area
def select_cases_with_most_fire_area(num_cases):
    input_file = 'it_scratch_fixed.txt'
    df = pd.read_csv(input_file)

    print(f'Selecting top {num_cases} cases with the most fire area from {input_file}:')
    
    if 'firearea' in df.columns:
        top_cases = df.nlargest(num_cases, 'firearea')
        print(f"Top {num_cases} cases with the most fire area:\n{top_cases}")
        
        # Save to a new file
        top_cases.to_csv('top_fire_area_cases.csv', index=False)
    else:
        print("No 'firearea' column found in the input file.")

# get the cases with the most fire are and plot their time of arrival on subplots
def plot_top_fire_area_cases(num_cases):
    input_file = 'input_tracking.txt'
    df = pd.read_csv(input_file)

    print(f'Plotting top {num_cases} cases with the most fire area from {input_file} (excluding fire area == 3419.5):')
    
    if 'firearea' in df.columns:
        # Filter out cases with firearea == 3419.5
        df_filtered = df[df['firearea'] != 3419.5]
        top_cases = df_filtered.nlargest(num_cases, 'firearea')
        print(f"Top {num_cases} cases with the most fire area:\n{top_cases[['run', 'firearea']]}")
        
        # Set up 3 rows and 5 columns for subplots
        fig, axes = plt.subplots(nrows=3, ncols=5, figsize=(18, 10))
        axes = axes.flatten()
        
        for ax_idx, (i, row) in enumerate(top_cases.iterrows()):
            case_num = row['run']
            x_ign = row['xign']
            y_ign = row['yign']
            case_path = f'{case_dir}/case_{int(case_num)}'
            print(case_path)
            time_files = glob.glob(f"{case_path}/time_of_arrival_*.tif")
            
            if time_files:
                with rasterio.open(time_files[0]) as src:
                    time_data = src.read(1)
                    ax = axes[ax_idx]
                    show(time_data, ax=ax, cmap=cm.viridis)
                    ax.set_title(
                        f"Case {case_num}\nFire Area: {row['firearea']:.1f}\n"
                        f"x_ign: {x_ign:.1f}, y_ign: {y_ign:.1f}"
                    )
            else:
                print(f"No time of arrival file found for case {case_num}.")
        
        # Hide unused subplots if less than 15 cases
        for j in range(len(top_cases), len(axes)):
            axes[j].set_visible(False)
        
        plt.tight_layout()
        plt.show()
    else:
        print("No 'firearea' column found in the input file.")

# get all of the fire cases for which there is 0 fire area and plot the distribution of their x and y ignition points
def plot_zero_fire_cases(firearea_threshold=0.2):
    input_file = 'input_tracking.txt'
    df = pd.read_csv(input_file)

    print(f'Plotting cases with zero fire area from {input_file}:')
    
    if 'firearea' in df.columns:
        zero_fire_cases = df[df['firearea'] <= firearea_threshold]
        print(f"Cases with <= {firearea_threshold} fire area:\n{zero_fire_cases[['run', 'xign', 'yign', 'firearea']]}")
        
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=zero_fire_cases, x='xign', y='yign', hue='run', palette='viridis', s=100)
        plt.title(f'Ignition Points of Cases with <= {firearea_threshold} Fire Area')
        plt.xlabel('X Ignition Point')
        plt.ylabel('Y Ignition Point')
        plt.legend(title='Run Number', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.show()
    else:
        print("No 'firearea' column found in the input file.")


# plot fire area against each input parameter
def plot_fire_area_vs_inputs():
    input_file = 'input_tracking.txt'
    df = pd.read_csv(input_file)

    print(f'Plotting fire area against each input parameter from {input_file}:')
    
    if 'firearea' in df.columns:
        plt.figure(figsize=(15, 10))
        for i, column in enumerate(df.columns[1:-1], start=1):  # Exclude 'run' and 'firearea'
            plt.subplot(4, 5, i)
            sns.scatterplot(x=df[column], y=df['firearea'])
            plt.title(f'Fire Area vs {column}')
            plt.xlabel(column)
            plt.ylabel('Fire Area')
        
        plt.tight_layout()
        plt.show()
    else:
        print("No 'firearea' column found in the input file.")

# get the maximum fuel model for which there is fire area
def max_fuel_model_fire_area():
    input_file = 'input_tracking.txt'
    df = pd.read_csv(input_file)

    print(f'Finding maximum fuel model with fire area from {input_file}:')
    
    if 'firearea' in df.columns and 'fuel' in df.columns:
        max_fuel_model = df[df['firearea'] > 0]['fuel'].max()
        print(f"Maximum fuel model with fire area > 0: {max_fuel_model}")
        return max_fuel_model
    else:
        print("No 'firearea' or 'fuel' column found in the input file.")
        return None
    
# plot the distribution of a given variable for all cases with fire area under a given threshold
def plot_var_dist_for_firearea_underthreshold(variable='yign', threshold=0.2):
    input_file = 'input_tracking.txt'
    df = pd.read_csv(input_file)

    print(f'Plotting distribution of {variable} for cases with fire area under {threshold} from {input_file}:')
    
    if 'firearea' in df.columns and variable in df.columns:
        filtered_cases = df[df['firearea'] <= threshold]
        print(f"Number of cases with fire area <= {threshold}: {len(filtered_cases)}")
        
        plt.figure(figsize=(10, 6))
        sns.histplot(filtered_cases[variable], kde=True)
        plt.title(f'Distribution of {variable} for Cases with Fire Area <= {threshold}')
        plt.xlabel(variable)
        plt.ylabel('Frequency')
        plt.tight_layout()
        plt.show()
    else:
        print(f"No 'firearea' or '{variable}' column found in the input file.")


# check how many cases there are with model < 16
def check_model_distribution(model_threshold=16):
    input_file = 'input_tracking.txt'
    df = pd.read_csv(input_file)

    print(f'Checking distribution of fuel model < {model_threshold} from {input_file}:')
    
    if 'fuel' in df.columns:
        count_below_threshold = (df['fuel'] < model_threshold).sum()
        print(f"Number of cases with fuel model < {model_threshold}: {count_below_threshold}")
        
        # Plotting the distribution of fuel models
        plt.figure(figsize=(10, 6))
        sns.histplot(df['fuel'], bins=range(1, 42), kde=False)
        plt.axvline(model_threshold, color='red', linestyle='--', label=f'Model Threshold: {model_threshold}')
        plt.title('Distribution of Fuel Models')
        plt.xlabel('Fuel Model')
        plt.ylabel('Frequency')
        plt.legend()
        plt.tight_layout()
        plt.show()
    else:
        print("No 'fuel' column found in the input file.")

# averag fire area for each fuel model
def average_fire_area_per_fuel_model():
    input_file = 'input_tracking.txt'
    df = pd.read_csv(input_file)

    print(f'Calculating average fire area per fuel model from {input_file}:')
    
    if 'fuel' in df.columns and 'firearea' in df.columns:
        avg_fire_area = df.groupby('fuel')['firearea'].mean().reset_index()
        print("Average fire area per fuel model:")
        print(avg_fire_area)
        
        # Plotting the average fire area per fuel model
        plt.figure(figsize=(10, 6))
        sns.barplot(x='fuel', y='firearea', data=avg_fire_area)
        plt.title('Average Fire Area per Fuel Model')
        plt.xlabel('Fuel Model')
        plt.ylabel('Average Fire Area')
        plt.tight_layout()
        plt.show()
    else:
        print("No 'fuel' or 'firearea' column found in the input file.")


# print all cases for which fuel model is less than 16
def print_cases_with_fuel_model_less_than(model_threshold=16):
    input_file = 'input_tracking.txt'
    df = pd.read_csv(input_file)

    print(f'Printing cases with fuel model < {model_threshold} from {input_file}:')
    
    if 'fuel' in df.columns:
        filtered_cases = df[df['fuel'] < model_threshold]
        print(f"Number of cases with fuel model < {model_threshold}: {len(filtered_cases)}")
        print(filtered_cases[['run', 'fuel', 'firearea']])
    else:
        print("No 'fuel' column found in the input file.")


