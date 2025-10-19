#!/usr/bin/env python
import sys, platform, importlib.util, ssl, urllib.request

REQUIRED = ["numpy","scipy","matplotlib","astropy","astroquery","photutils","gwosc","h5py"]

def has_pkg(name):
    import importlib.util
    return importlib.util.find_spec(name) is not None

def check_net(url="https://www.google.com", timeout=5):
    try:
        with urllib.request.urlopen(url, timeout=timeout, context=ssl.create_default_context()) as resp:
            return resp.status == 200
    except Exception:
        return False

print("Python:", sys.version.replace("\n"," "))
print("Platform:", platform.platform())
print("\nPackages:")
missing = []
for p in REQUIRED:
    ok = has_pkg(p)
    print(f"  - {p}: {'OK' if ok else 'MISSING'}")
    if not ok: missing.append(p)

print("\nInternet access test:", "OK" if check_net() else "FAILED")

if missing:
    print("\nSome packages are missing. Suggested install commands:")
    print("  pip install " + " ".join(missing))
    print("  # or with conda: conda install -c conda-forge " + " ".join(missing))
else:
    print("\nAll required packages appear installed.")
