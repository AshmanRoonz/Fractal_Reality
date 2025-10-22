
#!/usr/bin/env python3

"""
Fractal Track Dimension Toolkit
================================

Compute fractal dimension D of particle tracks using:

  • Box-counting method (N(ε) vs 1/ε)
  • Divider ("coastline") method (L(δ) ~ δ^{1-D})

Inputs
------
A) Pre-traced polylines (recommended):
   CSV with columns: x,y,track_id,image_id (pixel coords). Units arbitrary but consistent.

B) Raw images (PNG/JPG):
   Auto-extracts track centerlines via Canny -> morphological cleanup -> skeletonize.
   This is a convenience; manual tracing is preferred for scientific rigor.

Usage
-----
1) Install deps:  pip install -r requirements.txt
2) Run on polylines:
   python boxcount_tracks.py --polylines tracks.csv --out outdir
3) Run on images:
   python boxcount_tracks.py --images data/imgs --out outdir

Outputs
-------
- out/summary.csv     : per-track D estimates (box, divider) + QC metrics
- out/plots/*.png     : log–log fits, visual overlays
- out/debug/*.png     : (images mode) extraction diagnostics
"""

import argparse, math, os, sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# skimage used only when working from raw images
from skimage import io as skio
from skimage.color import rgb2gray
from skimage.feature import canny
from skimage.morphology import skeletonize, binary_opening, disk, remove_small_objects
from skimage.measure import label, regionprops
from skimage.util import img_as_bool

def _ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def _linreg(x, y):
    x = np.asarray(x); y = np.asarray(y)
    A = np.vstack([x, np.ones_like(x)]).T
    slope, intercept = np.linalg.lstsq(A, y, rcond=None)[0]
    # R^2
    yhat = slope*x + intercept
    ss_res = np.sum((y - yhat)**2)
    ss_tot = np.sum((y - np.mean(y))**2) + 1e-12
    r2 = 1 - ss_res/ss_tot
    return slope, intercept, r2

def resample_polyline_xy(x, y, step=1.0):
    """Resample a polyline (x,y) to approximately uniform arc-length spacing 'step'."""
    x = np.asarray(x).astype(float); y = np.asarray(y).astype(float)
    dx = np.diff(x); dy = np.diff(y)
    seg = np.sqrt(dx*dx + dy*dy)
    s = np.concatenate([[0.0], np.cumsum(seg)])
    if s[-1] < step:
        return x.copy(), y.copy()
    new_s = np.arange(0, s[-1], step)
    new_x = np.interp(new_s, s, x)
    new_y = np.interp(new_s, s, y)
    return new_x, new_y

def box_count_dimension(points, eps_scales=20, min_boxes=5):
    """
    Box-counting on a set of 2D points.
    Returns D_hat, slope, intercept, r2, dataframe of (eps, N).
    """
    pts = np.asarray(points)  # (N,2)
    if pts.shape[0] < 10:
        return np.nan, np.nan, np.nan, np.nan, None

    # Normalize to unit square for scale invariance
    mins = pts.min(axis=0); maxs = pts.max(axis=0)
    span = np.maximum(maxs - mins, 1e-9)
    norm = (pts - mins)/span

    # Log-spaced epsilon
    eps = np.logspace(-3, -0.1, eps_scales)  # from 1e-3 to ~0.79
    N_list = []
    for e in eps:
        # grid index
        idx = np.floor(norm / e).astype(int)
        # unique boxes
        unique = np.unique(idx, axis=0)
        N_list.append(len(unique))

    # Keep only scales that occupy enough boxes
    eps_valid = []
    N_valid = []
    for e, n in zip(eps, N_list):
        if n >= min_boxes:
            eps_valid.append(e); N_valid.append(n)

    if len(eps_valid) < 5:
        return np.nan, np.nan, np.nan, np.nan, None

    x = np.log(1/np.asarray(eps_valid))
    y = np.log(np.asarray(N_valid)+1e-12)

    slope, intercept, r2 = _linreg(x, y)
    D_hat = slope  # slope is the fractal dimension
    df = pd.DataFrame({"epsilon": eps_valid, "N_boxes": N_valid, "log1_eps": x, "logN": y})
    return D_hat, slope, intercept, r2, df

def divider_dimension(points, deltas=20):
    """
    Divider (coastline) method: measure polyline length with ruler size delta.
    Fit L(delta) ~ delta^{1-D}  => log L = (1-D) log delta + const
    Returns D_hat, slope, intercept, r2, dataframe of (delta, L).
    """
    pts = np.asarray(points)
    if pts.shape[0] < 10:
        return np.nan, np.nan, np.nan, np.nan, None

    mins = pts.min(axis=0); maxs = pts.max(axis=0)
    span = np.maximum(maxs - mins, 1e-9)
    norm = (pts - mins)/span

    # define deltas in log-space between 1e-3 and 0.5
    deltas_arr = np.logspace(-3, -0.3, deltas)

    Ls = []
    for delta in deltas_arr:
        # Walk the polyline with step ~delta (Greedy along the sequence)
        L = 0.0
        i = 0
        while i < len(norm)-1:
            j = i+1
            acc = 0.0
            while j < len(norm):
                d = np.linalg.norm(norm[j] - norm[j-1])
                acc += d
                if acc >= delta:
                    break
                j += 1
            L += acc
            i = j
        Ls.append(L)

    x = np.log(deltas_arr + 1e-12)
    y = np.log(np.asarray(Ls) + 1e-12)
    slope, intercept, r2 = _linreg(x, y)
    # slope = 1 - D  =>  D = 1 - slope
    D_hat = 1.0 - slope
    df = pd.DataFrame({"delta": deltas_arr, "L": Ls, "log_delta": x, "logL": y})
    return D_hat, slope, intercept, r2, df

def extract_tracks_from_image(img, sigma=1.2, thr_low=0.1, thr_high=0.3, min_size=64):
    """
    Best-effort extraction: edges -> open -> skeleton -> label connected tracks -> centerlines.
    Returns a list of (N,2) arrays of pixel coordinates.
    """
    if img.ndim == 3 and img.shape[2] == 3:
        g = rgb2gray(img)
    else:
        g = img.astype(float)
        g = (g - g.min())/(g.max()-g.min()+1e-9)
    edges = canny(g, sigma=sigma, low_threshold=thr_low, high_threshold=thr_high)
    opened = binary_opening(edges, footprint=disk(1))
    opened = remove_small_objects(opened, min_size=min_size)
    skel = skeletonize(opened)
    lab = label(skel)
    tracks = []
    for region in regionprops(lab):
        coords = region.coords  # (row, col)
        if coords.shape[0] < 50:
            continue
        # Convert to (x,y) in pixel coords
        xy = np.stack([coords[:,1], coords[:,0]], axis=1).astype(float)
        tracks.append(xy)
    return tracks, {"edges": edges, "opened": opened, "skeleton": skel}

def analyze_polyline_set(df, outdir: Path, prefix="poly"):
    out_plots = outdir / "plots"
    _ensure_dir(out_plots)

    rows = []
    for (image_id, track_id), group in df.groupby(["image_id", "track_id"]):
        x = group["x"].values
        y = group["y"].values
        # Resample to uniform spacing for stability
        x_r, y_r = resample_polyline_xy(x, y, step=max(1.0, 0.002*max(len(x), len(y))))
        pts = np.stack([x_r, y_r], axis=1)

        D_box, s_b, b_b, r2_b, df_box = box_count_dimension(pts)
        D_div, s_d, b_d, r2_d, df_div = divider_dimension(pts)

        rows.append({
            "image_id": image_id,
            "track_id": track_id,
            "D_box": D_box,
            "R2_box": r2_b,
            "D_divider": D_div,
            "R2_divider": r2_d,
            "n_points": len(pts)
        })

        # Plot for this track
        fig, ax = plt.subplots(figsize=(4.8,3.6))
        if df_box is not None:
            ax.scatter(df_box["log1_eps"], df_box["logN"], s=16, label="box-count")
            ax.plot(df_box["log1_eps"], s_b*df_box["log1_eps"]+b_b, label=f"fit D={D_box:.3f}, R2={r2_b:.3f}")
        ax.set_xlabel("log(1/ε)")
        ax.set_ylabel("log N(ε)")
        ax.set_title(f"{prefix}:{image_id}:{track_id}")
        ax.legend(loc="best", fontsize=8)
        fig.tight_layout()
        fig.savefig(out_plots / f"{prefix}_{image_id}_{track_id}_box.png", dpi=150)
        plt.close(fig)

        # Divider plot
        if df_div is not None:
            fig, ax = plt.subplots(figsize=(4.8,3.6))
            ax.scatter(df_div["log_delta"], df_div["logL"], s=16, label="divider")
            ax.plot(df_div["log_delta"], s_d*df_div["log_delta"]+b_d, label=f"fit D={D_div:.3f}, R2={r2_d:.3f}")
            ax.set_xlabel("log δ")
            ax.set_ylabel("log L(δ)")
            ax.set_title(f"{prefix}:{image_id}:{track_id}")
            ax.legend(loc="best", fontsize=8)
            fig.tight_layout()
            fig.savefig(out_plots / f"{prefix}_{image_id}_{track_id}_divider.png", dpi=150)
            plt.close(fig)

    summary = pd.DataFrame(rows)
    summary.to_csv(outdir / "summary.csv", index=False)
    return summary

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--polylines", type=str, default=None, help="CSV with columns x,y,track_id,image_id")
    ap.add_argument("--images", type=str, default=None, help="Folder with PNG/JPG images")
    ap.add_argument("--out", type=str, required=True, help="Output directory")
    ap.add_argument("--demo", action="store_true", help="Run synthetic demo (spiral + Brownian + straight)")
    args = ap.parse_args()

    outdir = Path(args.out); _ensure_dir(outdir)
    _ensure_dir(outdir / "plots"); _ensure_dir(outdir / "debug")

    if args.polylines:
        df = pd.read_csv(args.polylines)
        required = {"x","y","track_id","image_id"}
        if not required.issubset(set(df.columns)):
            raise ValueError(f"CSV must contain columns {required}")
        summary = analyze_polyline_set(df, outdir, prefix="csv")
        print("Wrote", outdir/"summary.csv")
        print(summary.describe())

    if args.images:
        img_dir = Path(args.images)
        img_files = [p for p in img_dir.iterdir() if p.suffix.lower() in [".png",".jpg",".jpeg"]]
        rows = []
        for p in img_files:
            img = skio.imread(p)
            tracks, debug = extract_tracks_from_image(img)
            # save debug panels
            fig, axs = plt.subplots(1,3, figsize=(9,3))
            axs[0].imshow(debug["edges"], cmap="gray"); axs[0].set_title("edges"); axs[0].axis("off")
            axs[1].imshow(debug["opened"], cmap="gray"); axs[1].set_title("opened"); axs[1].axis("off")
            axs[2].imshow(debug["skeleton"], cmap="gray"); axs[2].set_title("skeleton"); axs[2].axis("off")
            fig.tight_layout(); fig.savefig(outdir/"debug"/f"{p.stem}_debug.png", dpi=130); plt.close(fig)

            # Convert to a dataframe to reuse analyzer
            recs = []
            for k, xy in enumerate(tracks):
                recs.append(pd.DataFrame({
                    "x": xy[:,0], "y": xy[:,1],
                    "track_id": k, "image_id": p.stem
                }))
            if len(recs)==0:
                continue
            df = pd.concat(recs, ignore_index=True)
            summary = analyze_polyline_set(df, outdir, prefix=p.stem)
            rows.append(summary)

        if rows:
            big = pd.concat(rows, ignore_index=True)
            big.to_csv(outdir/"summary_all_images.csv", index=False)
            print("Wrote", outdir/"summary_all_images.csv")
            print(big.groupby("image_id")[["D_box","D_divider"]].mean())

    if args.demo:
        # Generate synthetic tracks: straight (D~1), Brownian proj (D~1.5), space-filling-ish curve (D~ ~2 in plane)
        def make_line(n=200):
            t = np.linspace(0,1,n)
            return np.stack([t, 0.3*t], axis=1)
        def make_brownian(n=200, seed=0):
            rng = np.random.default_rng(seed)
            steps = rng.normal(size=(n,2))
            pts = steps.cumsum(axis=0)
            pts -= pts.min(axis=0)
            pts /= pts.max(axis=0) + 1e-9
            return pts
        def make_spiral(n=300):
            t = np.linspace(0.1, 6*np.pi, n)
            r = np.linspace(0.01, 0.45, n)
            x = 0.5 + r*np.cos(t); y = 0.5 + r*np.sin(t)
            return np.stack([x,y], axis=1)

        demos = [
            ("demo","line", make_line()),
            ("demo","brownian", make_brownian()),
            ("demo","spiral", make_spiral()),
        ]
        recs = []
        for img_id, track_id, pts in demos:
            recs.append(pd.DataFrame({"x": pts[:,0], "y": pts[:,1], "track_id": track_id, "image_id": img_id}))
        df = pd.concat(recs, ignore_index=True)
        summary = analyze_polyline_set(df, outdir, prefix="demo")
        print(summary)

if __name__ == "__main__":
    main()
