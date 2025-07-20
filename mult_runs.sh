#!/bin/bash

# mult_runs.sh - Script to run ELMFIRE simulations with different stop times
# This script loops through a list of simulation stop times, modifies the 01-run.sh script,
# runs the simulation, and saves outputs to timestamped folders

# Configuration: Define the list of simulation stop times (in seconds)
SIMULATION_TIMES=(
    1800    # 30 minutes
    3600    # 1 hour
    5400    # 1.5 hours  
    7200    # 2 hours
    10800   # 3 hours
    14400   # 4 hours
    18000   # 5 hours
    21600   # 6 hours
)

# Alternative: You can also define times based on hours and convert to seconds
# Uncomment and modify this section if you prefer to specify times in hours:
# SIMULATION_HOURS=(0.5 1 1.5 2 3 4 5 6)
# SIMULATION_TIMES=()
# for hour in "${SIMULATION_HOURS[@]}"; do
#     SIMULATION_TIMES+=($(echo "$hour * 3600" | bc))
# done

# Base directory for storing all simulation results
RESULTS_BASE_DIR="./mult_timestep_outputs"

# Create results base directory if it doesn't exist
mkdir -p "$RESULTS_BASE_DIR"

# Create an outputs directory that files will temporarily be stored in
RESULTS_TEMP_DIR="./outputs"
mkdir -p "$RESULTS_TEMP_DIR"

# Backup the original 01-run.sh file
if [ ! -f "01-run.sh.backup" ]; then
    echo "Creating backup of original 01-run.sh..."
    cp 01-run.sh 01-run.sh.backup
fi

# Function to restore original file in case of interruption
cleanup() {
    echo "Restoring original 01-run.sh..."
    if [ -f "01-run.sh.backup" ]; then
        cp 01-run.sh.backup 01-run.sh
    fi
    exit 1
}

# Set trap to cleanup on interrupt
trap cleanup INT TERM

echo "Starting multiple ELMFIRE simulations..."
echo "Simulation times: ${SIMULATION_TIMES[*]} seconds"
echo "Results will be saved to: $RESULTS_BASE_DIR"
echo ""

# Counter for tracking progress
total_runs=${#SIMULATION_TIMES[@]}
current_run=0

# Loop through each simulation time
for sim_time in "${SIMULATION_TIMES[@]}"; do
    current_run=$((current_run + 1))
    
    # Convert seconds to hours for display
    hours=$(echo "scale=2; $sim_time / 3600" | bc)
    
    echo "========================================"
    echo "Run $current_run of $total_runs"
    echo "Simulation time: $sim_time seconds ($hours hours)"
    echo "========================================"
    
    # Create output directory for this simulation time
    output_dir="$RESULTS_BASE_DIR/sim_${sim_time}s"
    mkdir -p "$output_dir"
    
    # Restore original 01-run.sh from backup
    cp 01-run.sh.backup 01-run.sh
    
    # Modify the SIMULATION_TSTOP value in 01-run.sh
    echo "Modifying simulation stop time to $sim_time seconds..."
    sed -i.tmp "s/^SIMULATION_TSTOP=.*/SIMULATION_TSTOP=$sim_time.0 # Simulation stop time (seconds)/" 01-run.sh
    rm -f 01-run.sh.tmp
    
    # Run the simulation
    echo "Starting ELMFIRE simulation..."
    start_time=$(date +%s)
    
    if ./01-run.sh; then
        end_time=$(date +%s)
        runtime=$((end_time - start_time))
        echo "Simulation completed successfully in $runtime seconds"
        
        # Copy outputs to the designated directory
        echo "Copying outputs to $output_dir..."
        if [ -d "./outputs" ]; then
            mv ./outputs/* "$output_dir/"
            
            # Create a summary file with simulation parameters
            cat > "$output_dir/simulation_info.txt" << EOF

Simulation Parameters:
====================
Stop Time: $sim_time seconds ($hours hours)
Output Interval: $dtdump_value seconds
Runtime: $runtime seconds
Date: $(date)

Files Generated:
$(ls -la $output_dir)
EOF
            
            echo "Results saved to: $output_dir"
        else
            echo "Warning: No outputs directory found for simulation time $sim_time"
        fi
        
    else
        echo "Error: Simulation failed for time $sim_time seconds"
        echo "Check the simulation setup and try again"
        # Continue with next simulation rather than exit
        continue
    fi
    
    echo "Completed run $current_run of $total_runs"
    echo ""
done

# Restore original 01-run.sh
echo "Restoring original 01-run.sh..."
cp 01-run.sh.backup 01-run.sh

echo "========================================"
echo "All simulations completed!"
echo "Results are saved in: $RESULTS_BASE_DIR"
echo ""
echo "Directory structure:"
ls -la "$RESULTS_BASE_DIR"
