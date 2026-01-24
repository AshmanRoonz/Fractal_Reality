# LIGO Analysis - Learning Exercise

**Status: Learning Project**

This directory contains my early experiments learning to work with scientific data pipelines. It represents my journey learning:

- **GitHub & Version Control** - My first real repository
- **Python Scientific Stack** - numpy, scipy, pandas, matplotlib, h5py
- **Research Data Access** - GWOSC API v2, downloading real strain data
- **Algorithm Implementation** - Higuchi fractal dimension, correlation dimension
- **Data Visualization** - Publication-style plots

## What We Actually Did

**We downloaded and analyzed real LIGO data.** The O4 pipeline (`O4/o4_pipeline_v2.py`) uses the GWOSC API to:
- Fetch the event catalog
- Download actual strain data (HDF5 files)
- Calculate fractal dimension using Higuchi method
- Run statistical analysis

### Results

From 36 observations across 17 real O4 events:
- **Mean D = 1.287 ± 0.26**
- **Median D = 1.362**
- This is notably different from the predicted 1.5

### What We Learned (The Honest Part)

The noise control experiment (`noise_control_experiment.py`) revealed something important:

> The D ≈ 1.5 we initially saw may be a property of **detector noise**, not gravitational waves.

Evidence:
- No correlation between SNR and fractal dimension (r = 0.004)
- High-SNR and low-SNR events show same D values
- White noise inherently has D ≈ 1.5

**This is what learning looks like.** We ran the experiment, found our hypothesis wasn't supported by the data, and documented it honestly.

## Directory Structure

```
ligo/
├── gw_o3_analysis.py      # Initial analysis (includes simulation mode)
├── O3/                    # O3 run analysis
├── O4/                    # O4 run analysis (real GWOSC data)
│   └── o4_pipeline_v2.py  # Full automated pipeline
├── O3_O4/                 # Comparison across runs
├── data/                  # Results and outputs
├── noise_control_experiment.py  # Critical methodology test
└── README.md              # This file
```

## Running the Code

```bash
# Install dependencies
pip install numpy scipy matplotlib pandas h5py requests tqdm

# Run O4 analysis (downloads real data from GWOSC)
python O4/o4_pipeline_v2.py --min-snr 15 --max-events 10
```

## Acknowledgments

- LIGO Scientific Collaboration for making data publicly available
- GWOSC for the Open Science Center and API

---

*This analysis didn't validate our prediction — and that's okay. The D = 1.5 prediction from the Circumpunct framework is derived mathematically (D = 1 + β at β = 0.5). Whether gravitational waves specifically exhibit this dimension is a separate empirical question that our analysis couldn't confirm.*
