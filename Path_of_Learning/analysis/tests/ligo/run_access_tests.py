#!/usr/bin/env python
import json, subprocess, sys

def run(cmd):
    p = subprocess.run([sys.executable, cmd], capture_output=True, text=True)
    if p.returncode != 0:
        return {"error": p.stderr.strip()}
    try:
        return json.loads(p.stdout)
    except Exception:
        return {"raw": p.stdout.strip()}

def main():
    print("=== ENV CHECK ===")
    _ = subprocess.run([sys.executable, "env_check.py"])

    print("\n=== LIGO TEST ===")
    l = run("ligo_access_test.py")
    print(json.dumps(l, indent=2))

    print("\n=== JWST TEST ===")
    j = run("jwst_access_test.py")
    print(json.dumps(j, indent=2))

    print("\n=== SUMMARY ===")
    lp = l.get("pass", False) if isinstance(l, dict) else False
    jp = j.get("pass", False) if isinstance(j, dict) else False
    print(json.dumps({"LIGO_pass": lp, "JWST_pass": jp}, indent=2))

if __name__ == "__main__":
    main()
