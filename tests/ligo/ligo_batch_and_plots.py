#!/usr/bin/env python
"""
Batch LIGO runner with plots and CSV summary.

Usage:
  python ligo_batch_and_plots.py --events GW150914,GW151226,GW170104 --detectors H1,L1 --out out_ligo
"""

import argparse, io, csv, os, json

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def bandpass(signal, fs, f_lo=35.0, f_hi=350.0, order=4):
    from scipy.signal import butter, filtfilt
    ny = fs/2.0
    lo = max(f_lo/ny, 1e-6)
    hi = min(f_hi/ny, 0.999999)
    b, a = butter(order, [lo, hi], btype="band")
    return filtfilt(b, a, signal)

def zscore(x):
    import numpy as np
    mu = float(x.mean())
    sd = float(x.std()) + 1e-12
    return (x - mu)/sd

def higuchi_fd(x, kmax=16):
    import numpy as np
    x = np.asarray(x, dtype=float)
    N = len(x)
    Lk = []
    k_vals = range(1, kmax+1)
    for k in k_vals:
        Lm = []
        for m in range(k):
            idx = np.arange(m, N, k)
            if len(idx) < 2:
                continue
            xm = x[idx]
            lm = (np.sum(np.abs(np.diff(xm))) * (N - 1)) / ( (len(idx) - 1) * k )
            Lm.append(lm)
        Lk.append(np.mean(Lm) if Lm else 0.0)
    logk = np.log(1.0/np.array(list(k_vals)))
    logL = np.log(np.array(Lk) + 1e-12)
    a, b = np.polyfit(logk, logL, 1)
    return float(a)

def spectral_flatness(x, fs, nperseg=None):
    """Return (flatness, f, Pxx). Always a tuple.
       Adaptive nperseg; robust band fallback."""
    from scipy.signal import welch
    import numpy as np
    if nperseg is None:
        nperseg = min(1024, max(256, len(x)//2))
    f, Pxx = welch(x, fs=fs, nperseg=nperseg, noverlap=nperseg//2)
    Pxx = np.clip(Pxx, 1e-20, None)

    # Primary band 35–350 Hz
    band = (f >= 35.0) & (f <= 350.0)
    if not np.any(band):
        # Fallback to all positive freqs
        band = f > 0.0
    Px = Pxx[band]
    if Px.size == 0:
        return 0.0, f, Pxx

    gmean = np.exp(np.mean(np.log(Px)))
    amean = np.mean(Px)
    flat = float(gmean / amean)
    return flat, f, Pxx

def try_real_data(event="GW150914", detector="H1"):
    from gwosc.locate import get_event_urls
    import requests, h5py
    urls = get_event_urls(event, detector=detector)
    h5_urls = [u for u in urls if u.lower().endswith(".hdf5")]
    if not h5_urls:
        raise RuntimeError(f"No HDF5 URLs found for {event} {detector}")
    h5_urls.sort(key=lambda u: len(u))
    u = h5_urls[0]
    r = requests.get(u, timeout=30)
    r.raise_for_status()
    with h5py.File(io.BytesIO(r.content), "r") as f:
        strain = f["strain"]["Strain"][:]
        fs = float(f["strain"]["Strain"].attrs.get("SampleRate", 4096.0))
    return fs, strain, "gwosc+h5py", ""

def analyze(fs, x):
    import numpy as np
    from scipy.signal import hilbert

    x = bandpass(x, fs, 35.0, 350.0, order=4)
    x = zscore(x)

    env = np.abs(hilbert(x))
    peak_i = int(np.argmax(env))

    def seg(start_s, end_s):
        s0 = max(0, peak_i + int(start_s*fs))
        s1 = min(len(x), peak_i + int(end_s*fs))
        return x[s0:s1]

    insp = seg(-0.25, -0.05)
    ring = seg(+0.02, +0.35)

    if len(insp) < 1024 or len(ring) < 1024:
        half = int(0.5*fs)
        insp = x[max(0, peak_i-2*half):max(0, peak_i-half)]
        ring = x[min(len(x), peak_i+half):min(len(x), peak_i+2*half)]

    D_insp  = higuchi_fd(insp, kmax=16)
    D_ring  = higuchi_fd(ring, kmax=16)
    fd_drop_pct = 100.0 * (D_insp - D_ring) / max(D_insp, 1e-9)

    F_insp, f_insp, Pxx_insp = spectral_flatness(insp, fs)
    F_ring, f_ring, Pxx_ring = spectral_flatness(ring, fs)
    sf_drop_pct = 100.0 * (F_insp - F_ring) / max(F_insp, 1e-9)

    passed = (fd_drop_pct >= 5.0) or (sf_drop_pct >= 20.0)

    return {
        "D_insp": D_insp, "D_ring": D_ring, "FD_drop_pct": fd_drop_pct,
        "F_insp": F_insp, "F_ring": F_ring, "F_drop_pct": sf_drop_pct,
        "passed": passed, "insp": insp, "ring": ring,
        "f_insp": f_insp, "Pxx_insp": Pxx_insp, "f_ring": f_ring, "Pxx_ring": Pxx_ring,
        "peak_i": peak_i, "env": env, "x_proc": x
    }

def save_plots(outdir, event, detector, fs, res):
    import numpy as np, matplotlib.pyplot as plt

    prefix = os.path.join(outdir, f"{event}_{detector}")

    # 1) Time series around the peak (±0.5s)
    x = res["x_proc"]; peak_i = res["peak_i"]
    w = int(fs*0.5)
    s0 = max(0, peak_i - w); s1 = min(len(x), peak_i + w)
    t = np.arange(s0, s1)/fs - (peak_i/fs)
    plt.figure()
    plt.plot(t, x[s0:s1])
    plt.xlabel("Time (s)"); plt.ylabel("Strain (z-scored)")
    plt.title(f"{event} {detector} — Time series around peak")
    plt.savefig(prefix + "_timeseries.png", dpi=150, bbox_inches="tight")
    plt.close()

    # 2) Envelope around peak
    env = res["env"]
    plt.figure()
    plt.plot(t, env[s0:s1])
    plt.xlabel("Time (s)"); plt.ylabel("Envelope (a.u.)")
    plt.title(f"{event} {detector} — Hilbert envelope around peak")
    plt.savefig(prefix + "_envelope.png", dpi=150, bbox_inches="tight")
    plt.close()

    # 3) PSD (inspiral)
    f = res["f_insp"]; Pxx = res["Pxx_insp"]
    plt.figure()
    plt.semilogy(f, Pxx)
    plt.xlim(10, fs/2); plt.xlabel("Frequency (Hz)"); plt.ylabel("PSD")
    plt.title(f"{event} {detector} — PSD (inspiral window)")
    plt.savefig(prefix + "_psd_insp.png", dpi=150, bbox_inches="tight")
    plt.close()

    # 4) PSD (ringdown)
    f = res["f_ring"]; Pxx = res["Pxx_ring"]
    plt.figure()
    plt.semilogy(f, Pxx)
    plt.xlim(10, fs/2); plt.xlabel("Frequency (Hz)"); plt.ylabel("PSD")
    plt.title(f"{event} {detector} — PSD (ringdown window)")
    plt.savefig(prefix + "_psd_ring.png", dpi=150, bbox_inches="tight")
    plt.close()

    # 5) Metrics text dump
    with open(prefix + "_metrics.txt", "w") as ftxt:
        ftxt.write(json.dumps({
            "D_inspiral": res["D_insp"],
            "D_ringdown": res["D_ring"],
            "FD_drop_pct": res["FD_drop_pct"],
            "F_inspiral": res["F_insp"],
            "F_ringdown": res["F_ring"],
            "F_drop_pct": res["F_drop_pct"],
            "pass_logic": "FD_drop_pct>=5% OR F_drop_pct>=20%",
            "passed": res["passed"]
        }, indent=2))

def run_event_detector(event, detector, outdir):
    import numpy as np
    # fetch
    mode, notes = "", ""
    try:
        fs, x, mode, notes = try_real_data(event, detector)
    except Exception as e:
        # fallback synthetic
        def synthetic_chirp(n=4096*8, fs=4096.0):
            import numpy as np
            t = np.arange(n)/fs
            f0, f1 = 30.0, 200.0
            tau = 0.15
            merger = int(0.55*n)
            phase = 2*np.pi*(f0*t + (f1-f0)/(2*t[-1])*t**2)
            sig = 1e-21*np.sin(phase)
            rd = np.exp(-(np.arange(n-merger)/(fs*tau)))
            sig[merger:] *= rd
            return t, sig
        t, x = synthetic_chirp()
        fs = 4096.0
        mode = "synthetic"
        notes = f"fallback: {type(e).__name__}: {e}"

    res = analyze(fs, x)
    save_plots(outdir, event, detector, fs, res)
    row = {
        "event": event, "detector": detector,
        "duration_s": len(x)/fs, "sample_rate": fs,
        "D_insp": res["D_insp"], "D_ring": res["D_ring"], "FD_drop_pct": res["FD_drop_pct"],
        "F_insp": res["F_insp"], "F_ring": res["F_ring"], "F_drop_pct": res["F_drop_pct"],
        "pass": res["passed"], "mode": mode, "notes": notes
    }
    return row

def main():
    import numpy as np
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", type=str, default="GW150914,GW151226,GW170104")
    ap.add_argument("--detectors", type=str, default="H1,L1")
    ap.add_argument("--out", type=str, default="out_ligo")
    args = ap.parse_args()

    outdir = args.out
    ensure_dir(outdir)

    events = [e.strip() for e in args.events.split(",") if e.strip()]
    dets   = [d.strip() for d in args.detectors.split(",") if d.strip()]

    rows = []
    for e in events:
        for d in dets:
            try:
                row = run_event_detector(e, d, outdir)
                rows.append(row)
                print(f"[OK] {e} {d}")
            except Exception as ex:
                rows.append({
                    "event": e, "detector": d, "duration_s": None, "sample_rate": None,
                    "D_insp": None, "D_ring": None, "FD_drop_pct": None,
                    "F_insp": None, "F_ring": None, "F_drop_pct": None,
                    "pass": False, "mode": "error", "notes": f"{type(ex).__name__}: {ex}"
                })
                print(f"[ERR] {e} {d}: {ex}")

    # Write CSV summary
    csv_path = os.path.join(outdir, "summary.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "event","detector","duration_s","sample_rate",
            "D_insp","D_ring","FD_drop_pct",
            "F_insp","F_ring","F_drop_pct",
            "pass","mode","notes"
        ])
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"\nWrote {len(rows)} rows → {csv_path}")
    print(f"Plots saved in: {outdir}\\")

if __name__ == "__main__":
    main()
