# Framework Validation — Access Tests (v4)

**What's new in v4**
- `ligo_batch_and_plots.py`: Run **multiple LIGO events** (and detectors), compute
  **Higuchi FD** + **spectral flatness** metrics, and save **plots** + **CSV summary**.

You still have:
- `ligo_access_test.py` (single-event tester used by `run_access_tests.py`)
- `jwst_access_test.py`
- `env_check.py`
- `run_access_tests.py`

## Install (PowerShell)
```powershell
pip install numpy scipy gwosc h5py astropy astroquery photutils matplotlib
```

## Quick batch example
```powershell
python ligo_batch_and_plots.py --events GW150914,GW151226,GW170104 --detectors H1,L1 --out out_ligo
```

This will create `out_ligo/` with per-event **PNG plots** and a `summary.csv` like:

```
event,detector,duration_s,sample_rate,D_insp,D_ring,FD_drop_pct,F_insp,F_ring,F_drop_pct,pass,mode,notes
GW150914,H1,32.0,4096.0,0.326...,0.280...,14.24,0.899...,0.819...,8.88,true,gwosc+h5py,
...
```
