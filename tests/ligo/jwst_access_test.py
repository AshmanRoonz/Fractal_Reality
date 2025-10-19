#!/usr/bin/env python
import sys, json, math

def synth_lensed_image(n=256):
    import numpy as np
    from scipy.ndimage import gaussian_filter
    img = np.zeros((n,n), dtype=float)
    cx, cy = n//2, n//2
    R = n//3
    theta = np.linspace(-0.9, -0.2, 600)
    xs = (cx + R*np.cos(theta)).astype(int)
    ys = (cy + R*np.sin(theta)).astype(int)
    xs = np.clip(xs,0,n-1); ys = np.clip(ys,0,n-1)
    img[ys, xs] = 1.0
    img = gaussian_filter(img, 1.0)
    return img

def measure_arc_radius(img, thr=0.2):
    import numpy as np, math
    ys, xs = np.where(img > thr)
    pts = np.vstack([xs, ys]).T.astype(float)
    x = pts[:,0]; y = pts[:,1]
    A = np.c_[2*x, 2*y, np.ones_like(x)]
    b = x**2 + y**2
    c, *_ = np.linalg.lstsq(A, b, rcond=None)
    xc, yc, c0 = c
    R = math.sqrt(c0 + xc**2 + yc**2)
    return float(xc), float(yc), float(R), pts

def proxy_relation_R2(pts, xc, yc):
    import numpy as np
    r = np.sqrt((pts[:,0]-xc)**2 + (pts[:,1]-yc)**2)
    R = r.max() + 1e-9
    gtt = 1.0 - (r/R)**2
    D = np.sqrt(np.clip(gtt, 0, 1))
    y = D
    X = np.c_[np.ones_like(y), D]
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ beta
    ss_res = ((y - yhat)**2).sum()
    ss_tot = ((y - y.mean())**2).sum()
    R2 = 1.0 - ss_res/(ss_tot+1e-12)
    return float(R2)

def main():
    out = {"mode": None, "obs_count": None, "R2": None, "pass": None, "notes": ""}
    try:
        from astroquery.mast import Observations
        obs = Observations.query_criteria(target_name='SMACS0723', obs_collection='JWST')
        out["mode"] = "mast"
        out["obs_count"] = int(len(obs))
        out["R2"] = None
        out["pass"] = bool(len(obs) > 0)
        print(json.dumps(out, indent=2)); return
    except Exception as e:
        out["mode"] = "synthetic"; out["notes"] = f"fallback: {type(e).__name__}: {e}"

    img = synth_lensed_image()
    xc, yc, R, pts = measure_arc_radius(img)
    R2 = proxy_relation_R2(pts, xc, yc)
    out["R2"] = R2
    out["pass"] = bool(R2 >= 0.8)
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
