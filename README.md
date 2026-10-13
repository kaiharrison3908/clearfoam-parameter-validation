# clearFoam

**An open-source toolbox based on OpenFOAM to simulate biofilm growth and degradation**

## About

clearFoam is a comprehensive computational fluid dynamics (CFD) toolbox built on OpenFOAM for simulating biofilm growth and degradation processes. The toolbox includes custom solvers, utilities, and a user-friendly Python GUI for easy simulation management.

## Features

- **Custom OpenFOAM Solver**: `clearFoam2D` solver for biofilm simulation
- **Specialized Utilities**: Tools for analyzing biomass, autoinducers, enzymes, and EPS
- **Python GUI**: Easy-to-use interface for running simulations and post-processing
- **Docker Integration**: Containerized OpenFOAM environment for consistent execution
- **Parameter Management**: GUI-based parameter configuration
- **Data Visualization**: Built-in plotting and data export capabilities

## Prerequisites

Before getting started, ensure you have the following installed:

- **Docker**: Required for running OpenFOAM container
  - Install from: https://docs.docker.com/get-docker/

- **Python 3.x**: For running the GUI application
  - Required packages: `tkinter`, `matplotlib` (usually included with Python)

- **Git**: For cloning the repository

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://gitlab.igem.org/2025/software-tools/duke.git
cd duke/clearFoam
```

### 2. Verify Docker Installation

Make sure Docker is running on your system:

```bash
docker --version
```

If you're using Windows, you may need to fix line endings and file permissions with:

```bash
apt-get update && apt-get install -y dos2unix 
find . -type f -maxdepth 1 -exec dos2unix {} \; 
find . -type f -maxdepth 1 -exec chmod +x {} \;
```

### 3. Run the clearFoam GUI Application

Launch the Python GUI application:

```bash
python clearfoam.py
```

Or on some systems:

```bash
python3 clearfoam.py
```

## Getting Started

### First Time Setup

1. **Launch the Application**: Run `python clearfoam.py`
2. **Docker Setup**: The application will automatically:
   - Check for Docker installation
   - Download the OpenFOAM Docker image (if not present)
   - Create and start a Docker container

3. **Prepare the Build**: Click "Prepare (allwmake + clean)" to compile the custom solvers and utilities

### Running a Simulation

1. **Set Parameters** (Optional): Click "Set Parameters" to modify simulation parameters
2. **Run Simulation**: Click "Run Simulation" to start the clearFoam2D solver
3. **Post-Processing**: Use the post-processing tools to analyze results:
   - Click "Run Post-Processing" to generate data files
   - Select a data type from the dropdown (biomass, autoinducer, etc.)
   - Use "View" to plot data or "Download" to save files

### Available Post-Processing Tools

- **biomass**: Total biomass analysis
- **sessileBiomass**: Sessile biomass analysis
- **autoinducer**: Autoinducer concentration analysis
- **eps**: Extracellular polymeric substances analysis
- **eps_max**: Maximum EPS analysis
- **biomass_max**: Maximum biomass analysis
- **enzyme**: Enzyme concentration analysis
- **dispersedBiomass**: Dispersed biomass analysis

## Project Structure

```
clearFoam/
├── clearfoam.py           # Main GUI application
├── allwmake              # Build script for all components
├── allwclean             # Clean script
├── solvers/
│   └── clearFoam2D/      # Custom OpenFOAM solver
├── utilities/            # Post-processing utilities
├── libraries/            # Custom OpenFOAM libraries
└── dev/
    └── clearFoam/
        └── base/         # Example simulation case
```

## Troubleshooting

### Docker Issues

- **Docker not found**: Ensure Docker is installed and added to your system PATH
- **Permission denied**: On Linux, you may need to add your user to the docker group:

  ```bash
  sudo usermod -aG docker $USER
  ```

- **Container fails to start**: Check if Docker daemon is running

### Python Issues

- **tkinter not found**: Install tkinter (usually `python3-tk` on Ubuntu/Debian)
- **matplotlib not found**: Install with `pip install matplotlib`

### Simulation Issues

- **Build failures**: Ensure the "Prepare" step completed successfully
- **Solver crashes**: Check simulation parameters and mesh quality

## Advanced Usage

### Manual OpenFOAM Commands

If you prefer command-line operation, you can run OpenFOAM commands directly in the container:

```bash
docker run -it -v <local_path>:/home/openfoam/<container_path> opencfd/openfoam-default:<version>
cd /home/openfoam/clearFoam
./allwmake -j
cd dev/clearFoam/base
./clean
./run
```

### Custom Case Setup

To run your own simulation case:

1. Copy the `dev/clearFoam/base` directory as a template
2. Modify the case parameters in the `system/` and `constant/` directories
3. Update mesh and boundary conditions as needed
4. Run through the GUI or manually

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](license) file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## Support

For questions, issues, or support:
- Create an issue on GitHub: https://gitlab.igem.org/2025/software-tools/duke/issues

## Parameter Validation Improvements

This branch adds parameter validation to ClearFOAM to help prevent invalid model inputs from reaching the simulation solver.

### Changes
- Added a parameter validation module to check model inputs before simulation.
- Integrated validation into the ClearFOAM GUI.
- Added checks that reject zero-valued `Yxs`, `mmax`, and `E_crit` parameters, which are used as divisors in the model.
- Added automated tests covering valid inputs and invalid parameter values.

### Testing

The validation tests pass locally:

- **11 tests passed**
- **7 subtests passed**

To run the tests from the project environment:

```bash
python -m pytest -q
```

These changes are intended to improve input handling and provide clearer feedback when model parameters are invalid.
- Contact the development team

## Acknowledgments

- Built on OpenFOAM (https://www.openfoam.com/)
- Uses OpenCFD's OpenFOAM Docker images
- Developed for biofilm research applications
