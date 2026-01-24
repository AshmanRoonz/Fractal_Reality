#!/usr/bin/env python
import json, io, math

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

def bandpass(signal, fs, f_lo=35.0, f_hi=350.0, order=4):
    from scipy.signal import butter, filtfilt
    ny = fs/2.0
    lo = max(f_lo/ny, 1e-6)
    hi = min(f_hi/ny, 0.999999)
    b, a = butter(order, [lo, hi], btype="band")
    return filtfilt(b, a, signal)

def zscore(x):
    import numpy as np
    mu = np.mean(x)
    sd = np.std(x) + 1e-12
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
    import numpy as np
    logk = np.log(1.0/np.array(list(k_vals)))
    logL = np.log(np.array(Lk) + 1e-12)
    a, b = np.polyfit(logk, logL, 1)
    return float(a)

def spectral_flatness(x, fs, nperseg=1024):
    from scipy.signal import welch
    import numpy as np
    f, Pxx = welch(x, fs=fs, nperseg=nperseg, noverlap=nperseg//2)
    Pxx = np.clip(Pxx, 1e-20, None)
    band = (f >= 35.0) & (f <= 350.0)
    if not np.any(band):
        return 0.0
    Px = Pxx[band]
    gmean = np.exp(np.mean(np.log(Px)))
    amean = np.mean(Px)
    return float(gmean / amean)

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

    F_insp  = spectral_flatness(insp, fs)
    F_ring  = spectral_flatness(ring, fs)
    sf_drop_pct = 100.0 * (F_insp - F_ring) / max(F_insp, 1e-9)

    passed = (fd_drop_pct >= 5.0) or (sf_drop_pct >= 20.0)

    return D_insp, D_ring, fd_drop_pct, F_insp, F_ring, sf_drop_pct, passed

def main():
    out = {"mode": None, "duration_s": None, "sample_rate": None,
           "D_inspiral": None, "D_ringdown": None, "D_drop_pct": None,
           "F_inspiral": None, "F_ringdown": None, "F_drop_pct": None,
           "pass": None, "notes": ""}
    try:
        fs, x, mode, notes = try_real_data("GW150914","H1")
        out["mode"] = mode; out["notes"] = notes
        out["sample_rate"] = float(fs)
        out["duration_s"] = float(len(x)/fs)
    except Exception as e:
        t, x = synthetic_chirp()
        fs = 4096.0
        out["mode"] = "synthetic"
        out["sample_rate"] = fs
        out["duration_s"] = float(t[-1]-t[0])
        out["notes"] = f"fallback: {type(e).__name__}: {e}"

    D_insp, D_ring, fd_drop_pct, F_insp, F_ring, sf_drop_pct, passed = analyze(fs, x)
    out["D_inspiral"] = D_insp
    out["D_ringdown"] = D_ring
    out["D_drop_pct"] = fd_drop_pct
    out["F_inspiral"] = F_insp
    out["F_ringdown"] = F_ring
    out["F_drop_pct"] = sf_drop_pct
    out["pass"] = passed
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
