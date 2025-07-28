#!/usr/bin/env python3
"""
ELMFIRE Output Postprocessor - Simplified Version

This script processes ELMFIRE simulation outputs to create timestep-based numpy arrays
for time of arrival, burn scar, flame length intensity (flin), and spread rate (vs).
"""

import os
import sys
import glob
import numpy as np
import rasterio
import argparse
from pathlib import Path
from typing import List, Dict

def load_tif_as_array(filepath: str) -> np.ndarray:
    """Load a GeoTIFF file as a numpy array."""
    with rasterio.open(filepath) as src:
        data = src.read(1)
        if src.nodata is not None:
            data = np.where(data == src.nodata, -9999, data)
        return data

def burnscar_creation(toa_array: np.ndarray, timestep_seconds: float) -> np.ndarray:
    """Create burn scar array based on time of arrival."""
    burnscar = np.where(
        (toa_array != -9999) & (toa_array <= timestep_seconds), 
        1, 
        0
    )
    return burnscar.astype(np.int8)

def var_sim_from_toa(toa_array: np.ndarray, 
                     var_array: np.ndarray, 
                     timestep_seconds: float,
                     variable_name: str = 'toa') -> np.ndarray:
    """Extract variable state at a specific timestep based on time of arrival."""
    if variable_name.lower() == 'toa' or variable_name.lower() == 'time_of_arrival':
        result = np.where(
            (toa_array != -9999) & (toa_array <= timestep_seconds),
            toa_array,
            -9999
        )
    else:
        result = np.where(
            (toa_array != -9999) & (toa_array <= timestep_seconds),
            var_array,
            -9999
        )
    return result

def timesteps_from_toa_one_case(case_dir: str, 
                               variables: List[str] = ['toa', 'burnscar'],
                               timestep_minutes: int = 15,
                               max_time_hours: float = 72.0) -> Dict[str, List[np.ndarray]]:
    """Create timestep-based simulation arrays for one case."""
    case_path = Path(case_dir)
    case_num = case_path.name.split('_')[-1]
    
    # Find required files
    toa_files = glob.glob(str(case_path / 'time_of_arrival_*.tif'))
    flin_files = glob.glob(str(case_path / 'flin_*.tif'))
    vs_files = glob.glob(str(case_path / 'vs_*.tif'))
    
    if not toa_files:
        raise FileNotFoundError(f"No time_of_arrival files found in {case_dir}")
    
    # Load time of arrival (required for all variables)
    # print the toa_array
    toa_array = load_tif_as_array(toa_files[0])
    
    # Load other variable arrays if needed
    variable_arrays = {'toa': toa_array}
    
    if 'flin' in variables and flin_files:
        variable_arrays['flin'] = load_tif_as_array(flin_files[0])
    
    if 'vs' in variables and vs_files:
        variable_arrays['vs'] = load_tif_as_array(vs_files[0])
    
    # Generate timesteps
    timestep_seconds = timestep_minutes * 60
    max_time_seconds = max_time_hours * 3600
    timesteps = np.arange(0, max_time_seconds + timestep_seconds, timestep_seconds)
    
    # Process each variable
    results = {}
    
    for variable in variables:
        results[variable] = []
        
        for ts in timesteps:
            if variable == 'burnscar':
                array = burnscar_creation(toa_array, ts)
            elif variable in variable_arrays:
                array = var_sim_from_toa(
                    toa_array, 
                    variable_arrays[variable], 
                    ts, 
                    variable
                )
            else:
                print(f"Warning: Variable '{variable}' not available for case {case_num}")
                continue
            
            results[variable].append(array)
    
    return results

def save_case_arrays(case_dir: str, 
                    arrays_dict: Dict[str, List[np.ndarray]], 
                    timestep_minutes: int = 15,
                    output_base_dir: str = './elmfire_sims'):
    """Save arrays to .npy files in elmfire_sims directory."""
    case_path = Path(case_dir)
    case_num = case_path.name.split('_')[-1]
    
    # Create output directory
    output_base = Path(output_base_dir)
    output_dir = output_base / f"case_{case_num}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestep_seconds = timestep_minutes * 60
    
    for variable, array_list in arrays_dict.items():
        for i, array in enumerate(array_list):
            timestep = (i) * timestep_seconds
            filename = f"case_{case_num}_{variable}_{timestep}.npy"
            filepath = output_dir / filename
            np.save(filepath, array)
    
    print(f"  Saved {len([item for sublist in arrays_dict.values() for item in sublist])} files to {output_dir}")

def create_sims_from_toa_all_cases(cases_dir: str = './cases',
                                  variables: List[str] = ['toa', 'burnscar'],
                                  timestep_minutes: int = 15,
                                  max_time_hours: float = 72.0,
                                  output_base_dir: str = './elmfire_sims'):
    """Process all cases and save to elmfire_sims."""
    cases_path = Path(cases_dir)
    output_path = Path(output_base_dir)
    
    if not cases_path.exists():
        raise FileNotFoundError(f"Cases directory not found: {cases_dir}")
    
    # Create output base directory
    output_path.mkdir(exist_ok=True)
    
    # Find all case directories
    case_dirs = [d for d in cases_path.iterdir() if d.is_dir() and d.name.startswith('case_')]
    case_dirs.sort(key=lambda x: int(x.name.split('_')[-1]))
    
    if not case_dirs:
        raise FileNotFoundError(f"No case directories found in {cases_dir}")
    
    print(f"ELMFIRE Postprocessor")
    print(f"Found {len(case_dirs)} cases to process")
    print(f"Variables: {variables}")
    print(f"Timestep: {timestep_minutes} minutes")
    print(f"Max time: {max_time_hours} hours")
    print(f"Output: {output_base_dir}")
    print("-" * 50)
    
    success_count = 0
    for case_dir in case_dirs:
        try:
            print(f"Processing {case_dir.name}...")
            
            # Generate arrays for this case
            arrays_dict = timesteps_from_toa_one_case(
                str(case_dir), 
                variables, 
                timestep_minutes, 
                max_time_hours
            )
            
            # Save arrays to files
            save_case_arrays(str(case_dir), arrays_dict, timestep_minutes, output_base_dir)
            success_count += 1
            
        except Exception as e:
            print(f"  Error processing {case_dir.name}: {e}")
            continue
    
    print("-" * 50)
    print(f"Processing complete! {success_count}/{len(case_dirs)} cases successful")
    print(f"Results saved to: {output_base_dir}")

def verify_case_outputs(case_dir: str, timestep_minutes: int = 15, output_base_dir: str = './elmfire_sims'):
    """Verify outputs for a single case."""
    case_path = Path(case_dir)
    case_num = case_path.name.split('_')[-1]
    npy_dir = Path(output_base_dir) / f"case_{case_num}"
    
    if not npy_dir.exists():
        return f"No output directory found for case {case_num}"
    
    npy_files = list(npy_dir.glob("*.npy"))
    
    if not npy_files:
        return f"No .npy files found for case {case_num}"
    
    # Group files by variable
    variables = {}
    shapes = set()
    
    for filepath in npy_files:
        print(filepath)  # Debugging line to see file paths
        parts = filepath.stem.split('_')
        if len(parts) >= 4:
            variable = parts[2]
            timestep = int(parts[3])
            
            if variable not in variables:
                variables[variable] = []
            variables[variable].append(timestep)
            
            # Check array shape
            array = np.load(filepath)
            shapes.add(array.shape)
    
    return {
        "case": case_num,
        "variables": list(variables.keys()),
        "file_counts": {var: len(times) for var, times in variables.items()},
        "shapes": list(shapes),
        "total_files": len(npy_files)
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ELMFIRE Output Postprocessor")
    parser.add_argument("--case_dir", type=str, help="Path to a single case directory")
    parser.add_argument("--variables", nargs="+", help="Variables to process (e.g. toa burnscar flin vs)")
    parser.add_argument("--verify", action="store_true", help="Verify existing outputs")
    parser.add_argument("--help_only", action="store_true", help="Show help and exit")

    args = parser.parse_args()

    if args.help_only:
        parser.print_help()
        sys.exit(0)

    if args.verify:
        print("Verifying outputs...")
        cases_path = Path('./cases')
        case_dirs = sorted([d for d in cases_path.iterdir() if d.is_dir() and d.name.startswith('case_')])
        for case_dir in case_dirs[:5]:
            verification = verify_case_outputs(str(case_dir))
            print(f"Case {case_dir.name}: {verification}")
        sys.exit(0)

    # If a case_dir is specified
    if args.case_dir:
        variables = args.variables if args.variables else ['toa', 'burnscar', 'flin', 'vs']
        if not os.path.isdir(args.case_dir):
            print(f"Error: {args.case_dir} is not a valid directory.")
            sys.exit(1)
        print(f"Processing all cases in: {args.case_dir} with variables: {variables}")
        create_sims_from_toa_all_cases(
            args.case_dir,
            variables=variables,
            timestep_minutes=15,
            max_time_hours=72.0
        )
        print("Done.")
        sys.exit(0)

    # If only variables are specified, process all cases with those variables
    if args.variables:
        print(f"Processing all cases with variables: {args.variables}")
        create_sims_from_toa_all_cases(
            cases_dir='./cases',
            variables=args.variables,
            timestep_minutes=15,
            max_time_hours=72.0,
            output_base_dir='./elmfire_sims'
        )
        sys.exit(0)

    # Default: process all cases with default variables
    create_sims_from_toa_all_cases(
        cases_dir='./cases',
        variables=['toa', 'burnscar', 'flin', 'vs'],
        timestep_minutes=15,
        max_time_hours=72.0,
        output_base_dir='./elmfire_sims'
    )
    