"""
Living Device, Stage A: the sense logger.

Created: 2026-11-18
Last updated: 2026-11-18
Version: 1.0

Plan: plans/living_device_plan_2026_11_18.md, section 7 (frozen 2026-11-18).

What it does: once a second it samples a few plain facts about this computer;
once a minute it appends one row of raw values to a local CSV. The sense byte
is not stored: it is computed from the raw rows by encode() below, so the
frozen definitions live in one place and the raw values stay available for
Stage B.

What it never records: keystrokes, window titles, program names in the clear,
addresses, screen content, audio. The foreground program is stored only as a
salted hash; the salt never leaves the log folder.

The log lives outside the repository, in %LOCALAPPDATA%\\LivingDevice, so it
cannot be committed by accident.

Run:        pythonw living_device_logger_v1.py
Self-test:  python living_device_logger_v1.py --selftest 5
            (samples for 5 seconds, prints one row, writes nothing)

Windows only. Standard library and ctypes; no installs.

History:
- 2026-11-18 v1.0: initial
"""

import argparse
import csv
import ctypes
import hashlib
import os
import sys
import time
from ctypes import wintypes
from datetime import datetime

# ----------------------------------------------------------------------------
# Frozen definitions (plan section 7). Do not change after the first row.
# ----------------------------------------------------------------------------

FIELDS = [
    "ts_local",         # ISO time with offset, at the end of the minute
    "epoch",            # seconds since 1970, same moment
    "seconds_sampled",  # how many one-second samples the row holds (60 if whole)
    "input_seconds",    # samples in which input arrived during the past second
    "cpu_load",         # mean processor load over the minute, 0 to 1
    "ac_online",        # 1 on mains, 0 on battery, -1 unknown
    "battery_pct",      # 0 to 100, -1 unknown
    "locked_seconds",   # samples in which the session was locked
    "full_seconds",     # samples in which the foreground window filled its monitor
    "fg_hash",          # salted hash of the foreground program at the last sample
]

GAP_SECONDS = 90  # a previous row older than this does not count as "a minute ago"


def encode(row, prev, cpu_floor):
    """The frozen sense byte for one row.

    row, prev: dicts with the FIELDS above (prev may be None).
    cpu_floor: median cpu_load over the three floor-setting days.
    Returns (byte, bits) with bits[k] the yes or no of sense k.
    """
    n = max(int(row["seconds_sampled"]), 1)
    half = n / 2.0
    near = prev is not None and (float(row["epoch"]) - float(prev["epoch"])) <= GAP_SECONDS

    bits = [0] * 8
    bits[0] = int(int(row["input_seconds"]) >= 1)                    # Present
    bits[1] = int(int(row["input_seconds"]) >= half)                 # Busy hands
    bits[2] = int(near and row["fg_hash"] == prev["fg_hash"]
                  and row["fg_hash"] != "none")                      # Staying
    bits[3] = int(float(row["cpu_load"]) > cpu_floor)                # Machine working
    bits[4] = int(int(row["ac_online"]) == 1)                        # Plugged in
    bits[5] = int(int(row["locked_seconds"]) >= half)                # Locked
    bits[6] = int(int(row["full_seconds"]) >= half)                  # Filling the screen
    return bits_to_byte(bits), bits


def bits_to_byte(bits):
    return sum((b & 1) << k for k, b in enumerate(bits))


def encode_stream(rows, cpu_floor):
    """Bytes for a whole log, with bit 7 (Changed) filled in.

    Changed is yes when bits 0 to 6 differ from the previous row's, and yes
    after any gap longer than GAP_SECONDS (and on the first row).
    """
    out = []
    prev_row, prev_low = None, None
    for row in rows:
        _, bits = encode(row, prev_row, cpu_floor)
        low = bits[:7]
        near = prev_row is not None and (
            float(row["epoch"]) - float(prev_row["epoch"])) <= GAP_SECONDS
        bits[7] = int((not near) or low != prev_low)
        out.append(bits_to_byte(bits))
        prev_row, prev_low = row, low
    return out


# ----------------------------------------------------------------------------
# Windows calls
# ----------------------------------------------------------------------------

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.UINT), ("dwTime", wintypes.DWORD)]


class SYSTEM_POWER_STATUS(ctypes.Structure):
    _fields_ = [
        ("ACLineStatus", ctypes.c_ubyte),
        ("BatteryFlag", ctypes.c_ubyte),
        ("BatteryLifePercent", ctypes.c_ubyte),
        ("SystemStatusFlag", ctypes.c_ubyte),
        ("BatteryLifeTime", wintypes.DWORD),
        ("BatteryFullLifeTime", wintypes.DWORD),
    ]


class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", wintypes.RECT),
        ("rcWork", wintypes.RECT),
        ("dwFlags", wintypes.DWORD),
    ]


user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.MonitorFromWindow.argtypes = [wintypes.HWND, wintypes.DWORD]
user32.MonitorFromWindow.restype = wintypes.HANDLE
user32.GetMonitorInfoW.argtypes = [wintypes.HANDLE, ctypes.POINTER(MONITORINFO)]
user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.OpenInputDesktop.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
user32.OpenInputDesktop.restype = wintypes.HANDLE
user32.GetUserObjectInformationW.argtypes = [
    wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD,
    ctypes.POINTER(wintypes.DWORD)]
user32.CloseDesktop.argtypes = [wintypes.HANDLE]
kernel32.GetTickCount.restype = wintypes.DWORD
kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.QueryFullProcessImageNameW.argtypes = [
    wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.GetSystemTimes.argtypes = [ctypes.POINTER(wintypes.FILETIME)] * 3

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
MONITOR_DEFAULTTONEAREST = 2
DESKTOP_READOBJECTS = 0x0001
UOI_NAME = 2
SHELL_CLASSES = {"Progman", "WorkerW", "Shell_TrayWnd"}


def idle_ms():
    """Milliseconds since the last keyboard or mouse input."""
    info = LASTINPUTINFO()
    info.cbSize = ctypes.sizeof(info)
    if not user32.GetLastInputInfo(ctypes.byref(info)):
        return 1 << 30
    return (kernel32.GetTickCount() - info.dwTime) & 0xFFFFFFFF


def power():
    s = SYSTEM_POWER_STATUS()
    if not kernel32.GetSystemPowerStatus(ctypes.byref(s)):
        return -1, -1
    ac = s.ACLineStatus if s.ACLineStatus in (0, 1) else -1
    pct = s.BatteryLifePercent if s.BatteryLifePercent <= 100 else -1
    return ac, pct


def _ft(ft):
    return (ft.dwHighDateTime << 32) | ft.dwLowDateTime


def cpu_times():
    """(idle, total) processor time; total includes idle."""
    idle, kern, usr = wintypes.FILETIME(), wintypes.FILETIME(), wintypes.FILETIME()
    kernel32.GetSystemTimes(ctypes.byref(idle), ctypes.byref(kern), ctypes.byref(usr))
    return _ft(idle), _ft(kern) + _ft(usr)


def is_locked():
    """True when the input desktop is not the user's own (lock screen)."""
    h = user32.OpenInputDesktop(0, False, DESKTOP_READOBJECTS)
    if not h:
        return True
    try:
        buf = ctypes.create_unicode_buffer(256)
        needed = wintypes.DWORD(0)
        ok = user32.GetUserObjectInformationW(
            h, UOI_NAME, buf, ctypes.sizeof(buf), ctypes.byref(needed))
        return (not ok) or buf.value.lower() != "default"
    finally:
        user32.CloseDesktop(h)


def foreground(salt):
    """(hash of the foreground program, fills-its-monitor flag)."""
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return "none", 0

    pid = wintypes.DWORD(0)
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    name = ""
    hproc = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
    if hproc:
        try:
            buf = ctypes.create_unicode_buffer(1024)
            size = wintypes.DWORD(len(buf))
            if kernel32.QueryFullProcessImageNameW(hproc, 0, buf, ctypes.byref(size)):
                name = os.path.basename(buf.value).lower()
        finally:
            kernel32.CloseHandle(hproc)
    fg_hash = hashlib.sha256(salt + name.encode("utf-8")).hexdigest()[:16] if name else "unknown"

    full = 0
    cls = ctypes.create_unicode_buffer(64)
    user32.GetClassNameW(hwnd, cls, len(cls))
    if cls.value not in SHELL_CLASSES:
        rect = wintypes.RECT()
        mi = MONITORINFO()
        mi.cbSize = ctypes.sizeof(mi)
        mon = user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)
        if user32.GetWindowRect(hwnd, ctypes.byref(rect)) and mon and \
                user32.GetMonitorInfoW(mon, ctypes.byref(mi)):
            m = mi.rcMonitor
            full = int(rect.left <= m.left and rect.top <= m.top
                       and rect.right >= m.right and rect.bottom >= m.bottom)
    return fg_hash, full


# ----------------------------------------------------------------------------
# The loop
# ----------------------------------------------------------------------------

def log_dir():
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    path = os.path.join(base, "LivingDevice")
    os.makedirs(path, exist_ok=True)
    return path


def load_salt(path):
    f = os.path.join(path, "salt.bin")
    if not os.path.exists(f):
        with open(f, "wb") as fh:
            fh.write(os.urandom(32))
    with open(f, "rb") as fh:
        return fh.read()


class Minute:
    """Accumulates one-second samples into one row."""

    def __init__(self):
        self.n = 0
        self.input_s = 0
        self.locked_s = 0
        self.full_s = 0
        self.fg_hash = "none"
        self.cpu0 = cpu_times()

    def sample(self, salt):
        self.n += 1
        if idle_ms() < 1000:
            self.input_s += 1
        if is_locked():
            self.locked_s += 1
            self.fg_hash = "none"
        else:
            h, full = foreground(salt)
            self.fg_hash = h
            self.full_s += full

    def row(self):
        idle1, total1 = cpu_times()
        d_idle, d_total = idle1 - self.cpu0[0], total1 - self.cpu0[1]
        load = 1.0 - (d_idle / d_total) if d_total > 0 else 0.0
        ac, pct = power()
        now = datetime.now().astimezone()
        return {
            "ts_local": now.isoformat(timespec="seconds"),
            "epoch": f"{now.timestamp():.0f}",
            "seconds_sampled": self.n,
            "input_seconds": self.input_s,
            "cpu_load": f"{min(max(load, 0.0), 1.0):.4f}",
            "ac_online": ac,
            "battery_pct": pct,
            "locked_seconds": self.locked_s,
            "full_seconds": self.full_s,
            "fg_hash": self.fg_hash,
        }


def single_instance(path):
    """Hold an exclusive lock for the life of the process, or exit."""
    import msvcrt
    fh = open(os.path.join(path, "logger.lock"), "a+")
    try:
        fh.seek(0)
        msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError:
        sys.exit(0)  # another logger is already running
    return fh


def run():
    path = log_dir()
    _lock = single_instance(path)
    salt = load_salt(path)
    csv_path = os.path.join(path, "log.csv")
    new = not os.path.exists(csv_path)

    with open(csv_path, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if new:
            w.writeheader()
            fh.flush()

        minute = Minute()
        current = int(time.time() // 60)
        while True:
            time.sleep(max(0.0, 1.0 - (time.time() % 1.0)))  # wake on the second
            now_min = int(time.time() // 60)
            if now_min != current:
                if minute.n > 0:
                    w.writerow(minute.row())
                    fh.flush()
                minute = Minute()
                current = now_min
            minute.sample(salt)


def selftest(seconds):
    salt = b"selftest"  # not the real salt; nothing is written
    minute = Minute()
    for _ in range(seconds):
        time.sleep(1.0)
        minute.sample(salt)
    row = minute.row()
    for k in FIELDS:
        print(f"{k:16} {row[k]}")
    byte, bits = encode(row, None, cpu_floor=0.10)
    print("bits 0 to 6     ", bits[:7], "(with a placeholder load floor of 0.10)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", type=int, metavar="SECONDS")
    args = ap.parse_args()
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass
    if args.selftest:
        selftest(args.selftest)
    else:
        run()
