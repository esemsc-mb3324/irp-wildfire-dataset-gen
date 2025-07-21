# irp-wildfire-dataset-gen
For chpa-214, a repository that contains information and scripts for generating a dataset for wildfire modeling.

## Overview

This repository serves as a reference for generating comprehensive datasets using ELMFIRE (Eulerian Level Set Model of Fire spread) to train deep learning models for wildfire behavior prediction. The approach is inspired by two key research efforts: the Google Research/USFS collaboration on high-resolution 1D fire modeling and established standards in wildfire machine learning research.

## ELMFIRE basics
Inputs:
Main inputs:
- CELLSIZE=30.0 # Grid size in meters
- DOMAINSIZE=12000.0 # Height and width of domain in meters
- SIMULATION_TSTOP=22200.0 # Simulation stop time (seconds)
Float32 inputs:
NUM_FLOAT_RASTERS=7
- WS 20-ft wind speed, mph
- WD 20-ft Wind direction, deg
- M1 1-hr   dead moisture content, %
- M10 10-hr  dead moisture content, %
- M100 100-hr dead moisture content, %
- adj Spread rate adjustment factor (-)
- phi Initial value of phi field
Int16 inputs:
NUM_INT_RASTERS=8
- slp Topographical slope (deg)
- asp Topographical aspect (deg)
- dem Elevation (m)
- fbfm Fire behavior fuel model code (-)
- cc Canopy cover (percent)
- ch Canopy height (10*meters)
- cbh Canopy base height (10*meters)
- cbd Canopy bulk density (100*kg/m3)
Final 3 inputs:
LH_MOISTURE_CONTENT=30.0 # Live herbaceous moisture content, percent
LW_MOISTURE_CONTENT=60.0 # Live woody moisture content, percent
A_SRS="EPSG: 32610" # Spatial reference system - UTM Zone 10

Outputs:
Time of arrival (s): time_of_arrival_XXXXXXX_YYYYYYY.tif
Spread rate (ft/min): vs_XXXXXXX_YYYYYYY.tif
Fireline intensity (kW/m): flin_XXXXXXX_YYYYYYY.tif
Hourly isochrones: hourly_isochrones.shp

## Research Foundation

### Key Papers

**1. Burge et al. (Google Research) - Time-Resolved Wildfire Spread Behavior**
- **Dataset Approach**: Generated 40,000 fire simulations using FARSITE on 128×128 cell domains with 30m resolution, testing four datasets of increasing complexity
- **Four-Dataset Progression**: 
  - Single fuel (homogeneous GR1 grass)
  - Multiple fuel (random fuel model per domain)
  - California (real-world heterogeneous landscapes)
  - California-WN (spatially-varying wind via WindNinja)
- **Model Architecture**: EPD-ConvLSTM model using autoregressive predictions over 15-minute increments, achieving Jaccard scores of 0.89-0.94 after 100 predictions (24+ hours)

**2. Finney et al. (USFS/Google Research) - High-Resolution 1D Fire Modeling**
- **Dataset Approach**: Generated 78,125 training cases using factorial combinations of 13 input variables on a 1D transect (100m fuel bed at 2cm resolution)
- **Variables**: Wind speed, fuel particle sizes, fuel loads, moisture content, slope, aspect, and fuel arrangement parameters
- **Outputs**: Rate of spread (ROS), flame length (FL), and flame zone depth (FZD)

### Dataset Complexity Progression

# Google #
1. **Level 1 (Single Fuel)**: Homogeneous fuel type (GR1 grass), one spot fire, uniform parameters across landscape but varying randomly across simulations
2. **Level 2 (Multiple Fuel)**: Random fuel model used for entire domain, resulting in ~40x less coverage per fuel type combination
3. **Level 3 (California)**: Real-world heterogeneous landscapes from LANDFIRE data, complex fuel arrangements
4. **Level 4 (California-WN)**: Spatially-varying wind patterns computed by WindNinja based on topography

## ELMFIRE Parameter Analysis for Dataset Generation

### Core ELMFIRE Inputs (Always Required)

**Fuel Data:**
- `fbfm40.tif` - Scott & Burgan 40 fuel models (categorical: 1-40)
- `cc.tif` - Canopy cover (0-100%)
- `ch.tif` - Canopy height (meters)
- `cbh.tif` - Canopy base height (meters)
- `cbd.tif` - Canopy bulk density (kg/m³)
- `adj.tif` - Fuel model adjustment factor (0-4)

**Weather Variables (Time Series):**
- `ws.tif` - Wind speed (m/s)
- `wd.tif` - Wind direction (degrees)
- `m1.tif` - 1-hour fuel moisture (%)
- `m10.tif` - 10-hour fuel moisture (%)
- `m100.tif` - 1000-hour fuel moisture (%)
- `lh.tif` - Live herbaceous moisture (%)
- `lw.tif` - Live woody moisture (%)

**Topography:**
- `dem.tif` - Digital elevation model (meters)
- `slp.tif` - Slope (degrees)
- `asp.tif` - Aspect (degrees)

**Ignition:**
- Point ignition coordinates (lat/lon)
- Ignition timing

### Level 1 Dataset: Single Fuel (Proof of Concept)

**Target Size**: 10,000-20,000 simulations

**Design Philosophy**: Following the Google Research single fuel dataset approach - homogeneous fuel type across entire landscape with uniform parameters per simulation, but randomly varying parameters across different simulations.

**Fixed Parameters:**
- **Fuel Type**: Single FBFM40 model (recommend FBFM1: Short grass, following Google's GR1 choice)
- **Topography**: Planar terrain with constant slope and aspect per simulation
- **Canopy**: Minimal canopy cover (0-5%)
- **Domain Size**: 128×128 cells at 300m resolution (~38km × 38km, smaller than Google's 30m for computational efficiency)

**Variable Parameters (Per Google Research Ranges):**

*Wind Conditions:*
- Wind speed: 0-50 km/h (Google's range)
- Wind direction: 0-360° (uniform distribution)
- Pattern: Constant wind during simulation

*Fuel Moisture:*
- 1-hr moisture: 2-40% (Google's range)
- 10-hr moisture: 2-40%
- 100-hr moisture: 2-40%
- Live herbaceous: 30-100%
- Live woody: 30-100%

*Topography:*
- Slope: 0-45° (constant per domain)
- Aspect: 0-360° (constant per domain)

*Ignition:*
- Location: Random within central 50% of domain (following Google approach)
- Shape: Small octagonal fire front (~75m width, ~2% of domain width)
- Timing: Simulation start (t=0)

*Simulation Parameters:*
- Duration: 72 hours (following Google's approach)
- Output interval: 15 minutes (Google's time step)
- Total time steps: 289 (following Google's methodology)

### Sampling Strategy

**Parameter Ranges (Level 1 - Based on Google Research):**
```
Wind Speed: [0, 50] km/h
Wind Direction: [0, 360] degrees  
Slope: [0, 45] degrees (constant per domain)
Aspect: [0, 360] degrees (constant per domain)
1hr Moisture: [2, 40] %
10hr Moisture: [2, 40] %
100hr Moisture: [2, 40] %
Live Herbaceous: [30, 100] %
Live Woody: [30, 100] %
Canopy Cover: [0, 100] %
Canopy Height: [3, 50] m
Crown Ratio: [0.1, 1.0]
Canopy Bulk Density: [0, 4000] kg/m³
```

### ELMFIRE Configuration Considerations

**Computational Domain:**
- Cellsize: 300m (balance between detail and computational cost; Google used 30m)
- Domain extent: ~38km × 38km (128×128 cells)
- Boundary conditions: Non-burnable boundaries (following Google approach)

**Simulation Settings:**
- Time step: 15 minutes (matching Google's approach)
- Stop criteria: 72 hours or domain boundary reached
- Output variables: `time_of_arrival`, `flin` (fireline intensity), `vs` (spread velocity)
- Burn fraction: Computed as fraction of burned region inside each cell (Google's approach)

**Quality Control:**
- Exclude simulations with numerical instabilities
- Filter unrealistic spread rates (>10 m/s)
- Validate against simplified analytical models (Rothermel equations)

### Validation Strategy
- Compare against historical fire perimeters
- Cross-validate with operational fire behavior models (FARSITE, FlamMap)
- Validate spread rates against field observations

## Dataset Output Structure

### File Organization
```
cases/
├── case_0.npz
├── case_1.npz
└── ...

Each case_X.npz contains:
- fire_data: (timesteps, channels, height, width)
  - Channel 0: Fireline intensity
  - Channel 1: Time of arrival  
  - Channel 2: Spread velocity
  - Channel 3: Fuel model
- metadata: Simulation parameters and geospatial info
```

### Metadata Schema
```python
metadata = {
    'channels': ['flin', 'time_of_arrival', 'vs', 'fuel_model'],
    'timesteps_in_case': [1800, 3600, 5400, ...],  # seconds
    'weather_params': {
        'wind_speed': float,
        'wind_direction': float,
        'fuel_moisture_1hr': float,
        # ... other parameters
    },
    'domain_info': {
        'cellsize': 300.0,
        'extent': [xmin, ymin, xmax, ymax],
        'projection': 'EPSG:...'
    }
}
```

## HPC Implementation Strategy

### Computational Requirements
- **Single simulation**: ~30-300 seconds (depending on domain size and complexity)
- **Target dataset (15,000 cases)**: ~1,250-3,750 CPU hours
- **Recommended approach**: Array jobs with 100-500 simulations per node

### Parallelization Strategy
```bash
# Example SLURM array job
#SBATCH --array=1-15000
#SBATCH --cpus-per-task=1
#SBATCH --time=01:00:00

# Each array job runs one ELMFIRE simulation
case_id=$SLURM_ARRAY_TASK_ID
./run_single_case.sh $case_id
```

### Data Management
- **Storage requirements**: ~50GB for Level 1 dataset
- **Backup strategy**: Redundant storage of parameter files for reproducibility
- **Processing pipeline**: Automated quality control and case validation

## Future Extensions

### Future Extensions

### Level 2+ Dataset Enhancements (Following Google Research Progression)
- **Level 2 - Multiple Fuel**: Random fuel model selection per domain (40 FBFM40 models)
- **Level 3 - California**: Real-world LANDFIRE landscapes with heterogeneous fuel distributions
- **Level 4 - California-WN**: Addition of spatially-varying wind via WindNinja integration
- **Advanced Features**: Time-varying weather, spot fires, ember transport, larger domains (following Google's ~126×126 final resolution after border trimming)

### Advanced ML Applications
- **Physics-informed neural networks**: Incorporate fire physics constraints
- **Uncertainty quantification**: Ensemble methods for prediction confidence
- **Real-time adaptation**: Online learning from incoming fire observations
- **Multi-scale modeling**: Hierarchical models from landscape to local scales

## Getting Started

1. **Setup Environment**: Ensure ELMFIRE is properly installed and configured
2. **Generate Base Cases**: Run `mult_runs.sh` to create initial simulation outputs
3. **Process Results**: Use `mult_outs_postprocess.py` to convert outputs to ML-ready format
4. **Quality Control**: Validate generated cases against expected fire behavior ranges
5. **Scale Up**: Deploy on HPC system for full dataset generation

## References

- Burge, J., et al. (2023). Recurrent Convolutional Deep Neural Networks for Modeling Time-Resolved Wildfire Spread Behavior. Fire Technology, 59, 3327-3354
- Finney, M.A., et al. (2021). Deep Learning for High-Resolution Wildfire Modeling
- Scott, J.H. & Burgan, R.E. (2005). Standard Fire Behavior Fuel Models
- Anderson, H.E. (1982). Aids to Determining Fuel Models for Estimating Fire Behavior
- Rothermel, R.C. (1972). A Mathematical Model for Predicting Fire Spread
