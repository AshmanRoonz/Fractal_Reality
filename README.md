
# Fractal Track Dimension Toolkit

Measure the fractal dimension (D) of particle tracks using **box-counting** and **divider** methods.

## Quick start

```bash
# 1) (optional) Create a venv
# python -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\activate)

# 2) Install deps
pip install -r requirements.txt

# 3) Run the synthetic demo (sanity check)
python boxcount_tracks.py --demo --out out_demo

# 4) Analyze your own *polylines* (recommended)
#    CSV columns: x,y,track_id,image_id
python boxcount_tracks.py --polylines tracks.csv --out out_tracks

# 5) Or run on *images* (best-effort auto-extraction)
python boxcount_tracks.py --images data/imgs --out out_imgs
```

Outputs:
- `out/summary.csv` with D estimates per track
- `out/plots/*` log–log fit visuals
- `out/debug/*` extraction snapshots (images mode)

## Notes

- **Scientific rigor:** Prefer manual or semi-automatic tracing to create high-quality polylines. Auto-extraction is provided for convenience only.
- **Two estimators:** Use both (box & divider). Agreement is a good QC signal.
- **Target prediction:** Your framework predicts **D ≈ 1.5** for quantum-like worldlines (within experimental/systematic bounds).

---

## Creating polylines from images

Many tools can trace paths and export CSV (e.g., Fiji/ImageJ with plugins, or custom scripts). Minimum columns:

```
x,y,track_id,image_id
12.0,45.1,0,bubble_001
12.5,45.7,0,bubble_001
...
```

## Reproducibility

- Fix random seeds when stochastic steps are used (not needed in pure polyline mode).
- Report both **slope** and **R²** for each fit.
- Keep preprocessing transparent; include images and parameters in your repo.
