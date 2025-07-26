#!/usr/bin/env python3
"""
ELMFIRE Monte Carlo Wrapper with Parameter Logging
Runs multiple ELMFIRE simulations with random ignition locations and parameter perturbations
"""

import numpy as np
import subprocess
import os
import shutil
import glob
import rasterio
from pathlib import Path
import time
import csv

def calculate_burned_area(time_arrival_file):
    """Calculate burned area in acres from time of arrival raster"""
    try:
        with rasterio.open(time_arrival_file) as src:
            data = src.read(1)
            # Count non-nodata pixels (burned area)
            burned_pixels = np.sum((data != -9999) & (~np.isnan(data)))
            # Convert to acres (30m x 30m pixels)
            pixel_area_m2 = 30 * 30  # 900 m2 per pixel
            area_acres = (burned_pixels * pixel_area_m2) / 4047  # m2 to acres
            return area_acres
    except Exception as e:
        print(f"    Error calculating burned area: {e}")
        return 0.0

def generate_random_ignition(domain_size_m, inner_percent=0.5):
    """Generate random ignition location within inner % of domain"""
    # Domain goes from -domain_size_m/2 to +domain_size_m/2
    domain_half = domain_size_m / 2
    inner_half = domain_half * inner_percent
    
    # Random coordinates within inner region
    x = np.random.uniform(-inner_half, inner_half)
    y = np.random.uniform(-inner_half, inner_half)
    
    return x, y

def extract_all_parameters_from_elmfire_data():
    """Extract all parameter values from the final elmfire.data file"""
    params = {}
    
    try:
        with open('./inputs/elmfire.data', 'r') as f:
            content = f.read()
        
        import re
        
        # Extract ignition coordinates
        x_match = re.search(r'X_IGN\(1\)\s*=\s*([0-9.-]+)', content)
        y_match = re.search(r'Y_IGN\(1\)\s*=\s*([0-9.-]+)', content)
        params['x_ignition'] = float(x_match.group(1)) if x_match else 0.0
        params['y_ignition'] = float(y_match.group(1)) if y_match else 0.0
        
        # Extract live moisture values
        lh_match = re.search(r'LH_MOISTURE_CONTENT\s*=\s*([0-9.-]+)', content)
        lw_match = re.search(r'LW_MOISTURE_CONTENT\s*=\s*([0-9.-]+)', content)
        params['live_herbaceous'] = float(lh_match.group(1)) if lh_match else np.nan
        params['live_woody'] = float(lw_match.group(1)) if lw_match else np.nan
        
    except Exception as e:
        print(f"    Warning: Could not extract parameters from elmfire.data: {e}")
        params = {'x_ignition': 0.0, 'y_ignition': 0.0, 'live_herbaceous': np.nan, 'live_woody': np.nan}
    
    return params

def read_raster_value(filepath):
    """Read a single representative value from a uniform raster"""
    try:
        with rasterio.open(filepath) as src:
            data = src.read(1)
            # Get a representative value (should be uniform after perturbation)
            valid_data = data[(data != -9999) & (~np.isnan(data))]
            if len(valid_data) > 0:
                return float(valid_data[0])
            return np.nan
    except Exception:
        return np.nan

def extract_raster_parameters():
    """Extract parameters from the perturbed raster files"""
    params = {}
    
    # Map parameter names to raster files
    raster_files = {
        'wind_speed': './inputs/ws.tif',
        'wind_direction': './inputs/wd.tif', 
        'm1_moisture': './inputs/m1.tif',
        'm10_moisture': './inputs/m10.tif',
        'm100_moisture': './inputs/m100.tif',
        'slope': './inputs/slp.tif',
        'aspect': './inputs/asp.tif',
        'fuel_model': './inputs/fbfm40.tif',
        'canopy_cover': './inputs/cc.tif',
        'canopy_height': './inputs/ch.tif',
        'canopy_base_height': './inputs/cbh.tif',
        'canopy_bulk_density': './inputs/cbd.tif'
    }
    
    # Read values from each raster
    for param_name, filepath in raster_files.items():
        params[param_name] = read_raster_value(filepath)
    
    return params

def modify_bash_script(script_path, slope_val, aspect_val):
    """Modify the bash script to use specific slope/aspect values"""
    # Read the original script
    with open(script_path, 'r') as f:
        content = f.read()
    
    # Replace slope and aspect values
    content = content.replace('INT_VAL[1]=22', f'INT_VAL[1]={slope_val:.0f}')
    content = content.replace('INT_VAL[2]=180', f'INT_VAL[2]={aspect_val:.0f}')
    
    # Write modified script
    with open(script_path, 'w') as f:
        f.write(content)

def modify_elmfire_config(x_ign, y_ign):
    """Modify elmfire.data.in with ignition coordinates and ensure single ignition mode"""
    config_path = "elmfire.data.in"
    
    # Read the config
    with open(config_path, 'r') as f:
        content = f.read()
    
    # Set ignition coordinates
    import re
    content = re.sub(r'X_IGN\(1\)\s*=\s*[0-9.-]+', f'X_IGN(1)      = {x_ign:.1f}', content)
    content = re.sub(r'Y_IGN\(1\)\s*=\s*[0-9.-]+', f'Y_IGN(1)      = {y_ign:.1f}', content)
    
    # Ensure Monte Carlo is enabled but with single ignition (not random ignitions)
    content = content.replace('RANDOM_IGNITIONS = .TRUE.', 'RANDOM_IGNITIONS = .FALSE.')
    
    # Write modified config
    with open(config_path, 'w') as f:
        f.write(content)

def generate_random_parameters():
    """Generate random slope and aspect values"""
    slope = np.random.uniform(0, 45)      # Slope: 0-45 degrees
    aspect = np.random.uniform(0, 360)    # Aspect: 0-360 degrees
    return slope, aspect

def run_simulation(sim_number, x_ign, y_ign, slope_val, aspect_val, script_path="01-run.sh"):
    """Run a single ELMFIRE simulation"""
    try:
        # Create backup of original files if they don't exist
        script_backup = f"{script_path}.original"
        config_backup = "elmfire.data.in.original"
        
        if not os.path.exists(script_backup):
            shutil.copy(script_path, script_backup)
        if not os.path.exists(config_backup):
            shutil.copy("elmfire.data.in", config_backup)
        
        # Restore original files
        shutil.copy(script_backup, script_path)
        shutil.copy(config_backup, "elmfire.data.in")
        
        # Modify files with new parameters
        modify_bash_script(script_path, slope_val, aspect_val)
        modify_elmfire_config(x_ign, y_ign)
        
        # Run the simulation
        result = subprocess.run(['bash', script_path], 
                              capture_output=True, text=True, timeout=600)  # 10 min timeout
        
        if result.returncode == 0:
            # Success - calculate burned area and extract ALL parameters
            time_files = glob.glob('./outputs/time_of_arrival*.tif')
            if time_files:
                burned_area = calculate_burned_area(time_files[0])
                
                # Extract all parameters from rasters and elmfire.data
                raster_params = extract_raster_parameters()
                elmfire_params = extract_all_parameters_from_elmfire_data()
                
                # Combine all parameters
                all_params = {**raster_params, **elmfire_params}
                
                return True, burned_area, all_params
            else:
                return False, 0.0, {}
        else:
            print(f"    ELMFIRE error: {result.stderr[:200]}...")
            return False, 0.0, {}
            
    except subprocess.TimeoutExpired:
        print(f"    Simulation timed out")
        return False, 0.0, {}
    except Exception as e:
        print(f"    Error: {e}")
        return False, 0.0, {}

def main():
    """Main Monte Carlo simulation runner"""
    
    # Configuration
    NUM_SIMULATIONS = 100
    DOMAIN_SIZE_M = 3840.0   # Match your script
    INNER_PERCENT = 0.5      # Use inner 50% for ignitions
    OUTPUT_DIR = "monte_carlo_outputs"
    
    print("=== ELMFIRE Monte Carlo Wrapper with Parameter Logging ===")
    print(f"Running {NUM_SIMULATIONS} simulations")
    print(f"Domain size: {DOMAIN_SIZE_M}m")
    print(f"Ignition area: Inner {INNER_PERCENT*100}% of domain")
    print(f"Output directory: {OUTPUT_DIR}")
    print()
    
    # Create output directory for storing results
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Set random seed for reproducibility (optional)
    np.random.seed(42)
    
    # Initialize CSV file for logging all parameters
    csv_file = os.path.join(OUTPUT_DIR, "simulation_parameters.csv")
    csv_headers = [
        'simulation', 'x_ignition', 'y_ignition', 'burned_area_acres',
        'wind_speed', 'wind_direction', 'm1_moisture', 'm10_moisture', 'm100_moisture',
        'slope', 'aspect', 'fuel_model', 'canopy_cover', 'canopy_height', 
        'canopy_base_height', 'canopy_bulk_density', 'live_herbaceous', 'live_woody'
    ]
    
    # Run simulations
    successful_runs = 0
    results = []
    
    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(csv_headers)
        
        for i in range(1, NUM_SIMULATIONS + 1):
            print(f"Simulation {i:3d}/{NUM_SIMULATIONS}: ", end="", flush=True)
            
            # Generate random parameters
            x_ign, y_ign = generate_random_ignition(DOMAIN_SIZE_M, INNER_PERCENT)
            slope_val, aspect_val = generate_random_parameters()
            
            # Run simulation
            success, burned_area, all_params = run_simulation(i, x_ign, y_ign, slope_val, aspect_val)
            
            if success:
                successful_runs += 1
                actual_x = all_params.get('x_ignition', x_ign)
                actual_y = all_params.get('y_ignition', y_ign)
                results.append((i, actual_x, actual_y, burned_area))
                
                # Move outputs to numbered directory
                sim_output_dir = os.path.join(OUTPUT_DIR, f"sim_{i:03d}")
                if os.path.exists('./outputs'):
                    if os.path.exists(sim_output_dir):
                        shutil.rmtree(sim_output_dir)
                    shutil.move('./outputs', sim_output_dir)
                
                # Write all parameters to CSV
                row = [
                    i, actual_x, actual_y, burned_area,
                    all_params.get('wind_speed', np.nan),
                    all_params.get('wind_direction', np.nan),
                    all_params.get('m1_moisture', np.nan),
                    all_params.get('m10_moisture', np.nan),
                    all_params.get('m100_moisture', np.nan),
                    all_params.get('slope', np.nan),
                    all_params.get('aspect', np.nan),
                    all_params.get('fuel_model', np.nan),
                    all_params.get('canopy_cover', np.nan),
                    all_params.get('canopy_height', np.nan),
                    all_params.get('canopy_base_height', np.nan),
                    all_params.get('canopy_bulk_density', np.nan),
                    all_params.get('live_herbaceous', np.nan),
                    all_params.get('live_woody', np.nan)
                ]
                writer.writerow(row)
                csvfile.flush()  # Ensure data is written immediately
                
                print(f"SUCCESS - Ignition: ({actual_x:7.1f}, {actual_y:7.1f}) - Slope: {all_params.get('slope', slope_val):4.1f}° - Aspect: {all_params.get('aspect', aspect_val):5.1f}° - Burned: {burned_area:8.1f} acres")
            else:
                print(f"FAILED  - Ignition: ({x_ign:7.1f}, {y_ign:7.1f}) - Slope: {slope_val:4.1f}° - Aspect: {aspect_val:5.1f}°")
    
    # Summary
    print(f"\n=== SUMMARY ===")
    print(f"Successful simulations: {successful_runs}/{NUM_SIMULATIONS}")
    print(f"Parameters logged to: {csv_file}")
    
    if results:
        burned_areas = [r[3] for r in results]
        print(f"Burned area range: {min(burned_areas):.1f} - {max(burned_areas):.1f} acres")
        print(f"Mean burned area: {np.mean(burned_areas):.1f} ± {np.std(burned_areas):.1f} acres")
    
    # Restore original files
    if os.path.exists("01-run.sh.original"):
        shutil.copy("01-run.sh.original", "01-run.sh")
    if os.path.exists("elmfire.data.in.original"):
        shutil.copy("elmfire.data.in.original", "elmfire.data.in")
    
    print("Done!")

if __name__ == "__main__":
    main()