# LIGO Analysis - Learning Exercise

**Status: Learning Project**

This directory contains my early experiments learning to work with scientific data pipelines. It represents my journey learning:

- **GitHub & Version Control** - My first real repository
- **Python Scientific Stack** - numpy, scipy, pandas, matplotlib
- **Research Data Access** - GWOSC API, HDF5 file formats
- **Algorithm Implementation** - Higuchi fractal dimension, correlation dimension
- **Data Visualization** - Publication-style plots

## Important Disclaimer

**These scripts use simulated gravitational wave signals, not real LIGO strain data.**

The code demonstrates:
- How to structure a fractal dimension analysis pipeline
- How to work with time series data
- How to generate publication-quality visualizations

The code does NOT provide:
- Empirical validation of any theoretical framework
- Actual gravitational wave analysis (use LALSuite/PyCBC for that)
- Peer-reviewed scientific results

## What I Learned

### Technical Skills
- Accessing data from GWOSC (Gravitational Wave Open Science Center)
- HDF5 file handling with h5py
- Implementing the Higuchi algorithm for fractal dimension
- Statistical analysis with scipy.stats
- Creating multi-panel scientific figures

### Project Organization
- Separating data, analysis, and visualization code
- Writing clear docstrings and comments
- Version controlling a scientific project
- Creating reproducible analysis pipelines

## Directory Structure

```
ligo/
├── gw_o3_analysis.py      # Main analysis script (simulated data)
├── O3/                    # O3 run specific experiments
├── O4/                    # O4 run specific experiments
├── O3_O4/                 # Comparison scripts
├── data/                  # Sample outputs and images
└── README.md              # This file
```

## Running the Code

```bash
# Install dependencies
pip install numpy scipy matplotlib pandas h5py

# Run the main analysis (uses simulated waveforms)
python gw_o3_analysis.py
```

## Acknowledgments

- LIGO Scientific Collaboration for making data publicly available
- GWOSC for the Open Science Center and tutorials
- The Python scientific computing community

---

*This is a learning exercise, preserved as documentation of my growth as a programmer and data analyst. The theoretical framework (Circumpunct) stands on its own mathematical foundations and does not depend on these exploratory analyses.*
