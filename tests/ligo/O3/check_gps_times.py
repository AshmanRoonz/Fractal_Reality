import h5py
import os
import json

# Known events
EVENT_GPS_TIMES = {
    'GW190412': 1239082262.2,
    'GW190425': 1240215503.0,
    'GW190521': 1242442967.4,
    'GW190814': 1249852257.0,
    'GW190915_235702': 1252278640.4,
}

print("="*70)
print("CHECKING GPS TIMES IN YOUR HDF5 FILES")
print("="*70)

# Load manifest
with open('gwosc_data/manifest.json', 'r') as f:
    manifest = json.load(f)

print(f"\nFound {len(manifest)} files\n")

file_gps_times = {}

for entry in manifest:
    filename = entry['filename']
    
    if os.path.exists(filename):
        with h5py.File(filename, 'r') as f:
            gps_start = f['strain'].attrs.get('gps_start', 0)
            detector = f['strain'].attrs.get('detector', 'Unknown')
            
            # Extract GPS from filename
            basename = os.path.basename(filename)
            parts = basename.replace('.hdf5', '').split('_')
            
            for part in parts:
                if part.startswith('GPS'):
                    file_gps = int(part.replace('GPS', ''))
                    break
            
            print(f"File: {basename}")
            print(f"  GPS from filename: {file_gps}")
            print(f"  GPS from attrs: {gps_start}")
            print(f"  Detector: {detector}")
            
            # Match to known events
            best_match = None
            min_diff = float('inf')
            
            for event_name, event_gps in EVENT_GPS_TIMES.items():
                diff = abs(file_gps - event_gps)
                if diff < min_diff:
                    min_diff = diff
                    best_match = event_name
            
            print(f"  Best match: {best_match} (diff: {min_diff:.1f}s)")
            
            if file_gps not in file_gps_times:
                file_gps_times[file_gps] = {
                    'event': best_match,
                    'diff': min_diff,
                    'detectors': []
                }
            file_gps_times[file_gps]['detectors'].append(detector)
            print()

print("\n" + "="*70)
print("RECOMMENDED EVENT_GPS_TIMES DICTIONARY:")
print("="*70)
print("\nEVENT_GPS_TIMES = {")

for file_gps, info in sorted(file_gps_times.items()):
    detectors_str = ', '.join(info['detectors'])
    print(f"    '{info['event']}': {file_gps},  # {detectors_str} (diff: {info['diff']:.1f}s)")

print("}")

print("\n" + "="*70)
print("ALTERNATE: USE FILE GPS TIMES DIRECTLY")
print("="*70)
print("\nFILE_GPS_TO_EVENT = {")
for file_gps, info in sorted(file_gps_times.items()):
    print(f"    {file_gps}: '{info['event']}',")
print("}")
