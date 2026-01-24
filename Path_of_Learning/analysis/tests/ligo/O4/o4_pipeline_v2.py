"""
Automated O4 Gravitational Wave Fractal Dimension Analysis Pipeline
===================================================================

Full automation using GWOSC API v2 for data retrieval and processing.
Uses corrected calibration: D = Higuchi - 0.5

Requirements:
    pip install numpy scipy matplotlib pandas h5py requests tqdm

Usage:
    python o4_pipeline_v2.py --min-snr 15 --max-events 10
"""

import numpy as np
from scipy import stats, signal as sp_signal
import matplotlib.pyplot as plt
import pandas as pd
import h5py
import requests
import os
from datetime import datetime
from pathlib import Path
import argparse
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# GWOSC API v2 CLIENT
# ============================================================================

class GWOSCClient:
    BASE_URL = "https://gwosc.org/api/v2"
    
    @staticmethod
    def extract_parameter(default_params, param_name):
        """Extract parameter value from default_parameters array"""
        if not default_params:
            return None
        for param in default_params:
            if param.get('name') == param_name:
                return param.get('best')
        return None
    
    @staticmethod
    def get_event_catalog(min_snr=None, max_events=None):
        """Retrieve event catalog from GWOSC API v2"""
        
        print("Fetching event catalog from GWOSC API v2...")
        
        params = {
            'include-default-parameters': 'true',
            'pagesize': 100  # Get 100 per page
        }
        
        # Note: Can't filter by SNR in query, must filter after
        url = f"{GWOSCClient.BASE_URL}/event-versions"
        
        all_events = []
        page = 1
        
        # Fetch multiple pages if needed
        while True:
            params['page'] = page
            response = requests.get(url, params=params)
            
            if response.status_code != 200:
                raise Exception(f"API failed: {response.status_code}\n{response.text}")
            
            data = response.json()
            
            if 'results' not in data or len(data['results']) == 0:
                break
            
            all_events.extend(data['results'])
            
            # Check if we have enough events or reached last page
            if max_events and len(all_events) >= max_events * 10:  # Get extra for filtering
                break
            
            if not data.get('next'):
                break
            
            page += 1
            
            if page > 5:  # Limit to 5 pages (500 events) for safety
                break
        
        print(f"  Retrieved {len(all_events)} total event versions from API")
        
        # Parse events and extract parameters
        events = []
        for event_version in all_events:
            default_params = event_version.get('default_parameters', [])
            
            # Extract parameters from default_parameters array
            network_snr = GWOSCClient.extract_parameter(default_params, 'network_matched_filter_snr')
            mass_1 = GWOSCClient.extract_parameter(default_params, 'mass_1_source')
            mass_2 = GWOSCClient.extract_parameter(default_params, 'mass_2_source')
            chi_eff = GWOSCClient.extract_parameter(default_params, 'chi_eff')
            lum_dist = GWOSCClient.extract_parameter(default_params, 'luminosity_distance')
            far = GWOSCClient.extract_parameter(default_params, 'far')
            
            events.append({
                'name': event_version.get('name', ''),
                'version': event_version.get('version'),
                'GPS': event_version.get('gps'),
                'catalog': event_version.get('catalog'),
                'detectors': event_version.get('detectors', []),
                'network_snr': network_snr,
                'mass_1': mass_1,
                'mass_2': mass_2,
                'chi_eff': chi_eff,
                'luminosity_distance': lum_dist,
                'far': far
            })
        
        df = pd.DataFrame(events)
        
        # Remove duplicates (keep latest version)
        df = df.sort_values(['name', 'version'], ascending=[True, False])
        df = df.drop_duplicates(subset=['name'], keep='first')
        
        # Filter by SNR (now that we have it)
        if min_snr:
            df = df[df['network_snr'].notna()]
            df = df[df['network_snr'] >= min_snr]
        
        df = df.sort_values('network_snr', ascending=False)
        
        if max_events:
            df = df.head(max_events)
        
        print(f"  ✓ Retrieved {len(df)} events" + (f" with SNR >= {min_snr}" if min_snr else ""))
        return df
    
    @staticmethod
    def download_strain_data(event_name, gps_time, detector, 
                            duration=32, output_dir='gwosc_data'):
        """Download strain data using API v2 with fallback to bulk files"""
        
        Path(output_dir).mkdir(exist_ok=True)
        
        start_time = int(gps_time - duration/2)
        filename = f"{output_dir}/{event_name}_{detector}_{start_time}.hdf5"
        
        if os.path.exists(filename):
            return filename
        
        # Method 1: Try event-specific 32s files (works for O1/O2 events)
        try:
            url = f"{GWOSCClient.BASE_URL}/event-versions/{event_name}/strain-files"
            params = {
                'detector': detector,
                'sample-rate': 4,
                'duration': 32,
                'file-format': 'hdf5'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                file_info = response.json()
                
                if 'results' in file_info:
                    files = file_info['results']
                else:
                    files = file_info if isinstance(file_info, list) else [file_info]
                
                if len(files) > 0:
                    download_url = files[0].get('download_url')
                    
                    if download_url:
                        file_response = requests.get(download_url, timeout=60)
                        
                        if file_response.status_code == 200:
                            with open(filename, 'wb') as f:
                                f.write(file_response.content)
                            return filename
        except Exception as e:
            pass
        
        # Method 2: Fallback to 4096s bulk files (works for O3/O4 events)
        try:
            # Query bulk strain files endpoint
            url = f"{GWOSCClient.BASE_URL}/strain-files"
            params = {
                'detector': detector,
                'start': int(gps_time - 2048),  # 4096s file centered on event
                'stop': int(gps_time + 2048),
                'sample-rate': 4
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                file_info = response.json()
                
                if 'results' in file_info and len(file_info['results']) > 0:
                    # Get the HDF5 URL
                    hdf5_url = file_info['results'][0].get('hdf5_url')
                    
                    if hdf5_url:
                        file_response = requests.get(hdf5_url, timeout=120)
                        
                        if file_response.status_code == 200:
                            with open(filename, 'wb') as f:
                                f.write(file_response.content)
                            return filename
        except Exception as e:
            pass
        
        return None

# ============================================================================
# FRACTAL DIMENSION CALCULATION
# ============================================================================

def higuchi_fd(signal_data, k_max=25):
    """Calculate Higuchi fractal dimension"""
    N = len(signal_data)
    
    if N < 100:
        return np.nan, 0.0
    
    L_k = []
    
    for k in range(1, k_max + 1):
        L_m = []
        for m in range(k):
            indices = np.arange(m, N, k, dtype=int)
            if len(indices) < 2:
                continue
            
            curve_length = 0
            for i in range(1, len(indices)):
                curve_length += abs(signal_data[indices[i]] - signal_data[indices[i-1]])
            
            curve_length *= (N - 1) / ((len(indices) - 1) * k * k)
            L_m.append(curve_length)
        
        if L_m:
            L_k.append(np.mean(L_m))
    
    if len(L_k) < 5:
        return np.nan, 0.0
    
    k_values = np.arange(1, len(L_k) + 1)
    log_k = np.log(k_values)
    log_L = np.log(L_k)
    
    slope, intercept, r_value, _, _ = stats.linregress(log_k, log_L)
    
    return -slope, r_value ** 2

def calibrate_fd(higuchi_value):
    """Corrected calibration: D = Higuchi - 0.5"""
    if np.isnan(higuchi_value):
        return np.nan
    return higuchi_value - 0.5

# ============================================================================
# SIGNAL PROCESSING
# ============================================================================

def load_and_process_strain(filename, gps_time, segment='full'):
    """Load and process strain data"""
    
    with h5py.File(filename, 'r') as f:
        strain = f['strain']['Strain'][:]
        
        try:
            gps_start = f['meta']['GPSstart'][()]
        except:
            gps_start = float(filename.split('_')[-1].replace('.hdf5', ''))
        
        sample_rate = 4096
        event_index = int((gps_time - gps_start) * sample_rate)
        
        if segment == 'full':
            start_idx = event_index - 16 * sample_rate
            end_idx = event_index + 16 * sample_rate
        elif segment == 'inspiral':
            start_idx = event_index - int(0.5 * sample_rate)
            end_idx = event_index
        elif segment == 'ringdown':
            start_idx = event_index
            end_idx = event_index + int(0.3 * sample_rate)
        
        start_idx = max(0, start_idx)
        end_idx = min(len(strain), end_idx)
        
        strain_segment = strain[start_idx:end_idx]
    
    sos = sp_signal.butter(4, [30, 400], btype='band', fs=4096, output='sos')
    return sp_signal.sosfilt(sos, strain_segment)

# ============================================================================
# EVENT ANALYSIS
# ============================================================================

def analyze_single_event(event_row, output_dir='gwosc_data'):
    """Analyze single event"""
    
    event_name = event_row['name']
    gps_time = event_row['GPS']
    available_detectors = event_row.get('detectors', ['H1', 'L1', 'V1'])
    
    print(f"\n{'='*60}")
    print(f"{event_name} (GPS: {gps_time:.1f}, SNR: {event_row['network_snr']:.1f})")
    print(f"{'='*60}")
    
    results = []
    
    for detector in ['H1', 'L1', 'V1']:
        if detector not in available_detectors:
            continue
        
        print(f"  {detector}...", end=' ')
        
        try:
            filename = GWOSCClient.download_strain_data(
                event_name, gps_time, detector, output_dir=output_dir
            )
            
            if filename is None:
                print("✗ Download failed")
                continue
            
            strain_full = load_and_process_strain(filename, gps_time, 'full')
            strain_inspiral = load_and_process_strain(filename, gps_time, 'inspiral')
            strain_ringdown = load_and_process_strain(filename, gps_time, 'ringdown')
            
            fd_full_raw, r2_full = higuchi_fd(strain_full)
            fd_insp_raw, r2_insp = higuchi_fd(strain_inspiral)
            fd_ring_raw, r2_ring = higuchi_fd(strain_ringdown)
            
            D_full = calibrate_fd(fd_full_raw)
            D_inspiral = calibrate_fd(fd_insp_raw)
            D_ringdown = calibrate_fd(fd_ring_raw)
            
            FD_drop_pct = ((D_inspiral - D_ringdown) / D_inspiral * 100 
                          if not np.isnan(D_inspiral) and not np.isnan(D_ringdown) 
                          else np.nan)
            
            passed_QC = (not np.isnan(FD_drop_pct)) and (FD_drop_pct >= 5.0)
            
            results.append({
                'event': event_name,
                'detector': detector,
                'GPS': gps_time,
                'network_snr': event_row['network_snr'],
                'mass_1': event_row['mass_1'],
                'mass_2': event_row['mass_2'],
                'D_full': D_full,
                'D_inspiral': D_inspiral,
                'D_ringdown': D_ringdown,
                'FD_drop_pct': FD_drop_pct,
                'R2_full': r2_full,
                'R2_inspiral': r2_insp,
                'R2_ringdown': r2_ring,
                'passed_QC': passed_QC
            })
            
            print(f"✓ D={D_full:.3f}, ΔD={FD_drop_pct:.1f}%")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            continue
    
    return results

def analyze_catalog(events_df, output_dir='gwosc_data'):
    """Process entire catalog"""
    
    print(f"\nProcessing {len(events_df)} events...")
    all_results = []
    
    for idx, event in tqdm(events_df.iterrows(), total=len(events_df)):
        results = analyze_single_event(event, output_dir)
        all_results.extend(results)
    
    results_df = pd.DataFrame(all_results)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_df.to_csv(f'O4_fractal_results_{timestamp}.csv', index=False)
    
    return results_df

# ============================================================================
# STATISTICAL ANALYSIS
# ============================================================================

def statistical_summary(results_df):
    """Statistical analysis"""
    
    print("\n" + "="*70)
    print("STATISTICAL ANALYSIS")
    print("="*70)
    
    df_valid = results_df.dropna(subset=['D_full'])
    
    if len(df_valid) == 0:
        print("✗ No valid results")
        return
    
    D_all = df_valid['D_full'].values
    
    print(f"\n1. OVERALL FRACTAL DIMENSION")
    print(f"   N = {len(df_valid)} observations")
    print(f"   Mean D = {D_all.mean():.3f} ± {D_all.std():.3f}")
    print(f"   Median D = {np.median(D_all):.3f}")
    print(f"   Range: [{D_all.min():.3f}, {D_all.max():.3f}]")
    print(f"   SEM = {D_all.std()/np.sqrt(len(D_all)):.3f}")
    
    print(f"\n2. FRAMEWORK VALIDATION (H₀: μ = 1.5)")
    t_stat, p_value = stats.ttest_1samp(D_all, 1.5)
    print(f"   t-statistic = {t_stat:.3f}")
    print(f"   p-value = {p_value:.4f}")
    
    if p_value >= 0.05:
        print(f"   ✓ CONSISTENT with D = 1.5")
    else:
        print(f"   ✗ INCONSISTENT with D = 1.5")
    
    ci_lower = D_all.mean() - 1.96 * D_all.std() / np.sqrt(len(D_all))
    ci_upper = D_all.mean() + 1.96 * D_all.std() / np.sqrt(len(D_all))
    print(f"   95% CI: [{ci_lower:.3f}, {ci_upper:.3f}]")
    
    df_phase = results_df.dropna(subset=['D_inspiral', 'D_ringdown'])
    if len(df_phase) > 0:
        print(f"\n3. PHASE TRANSITION")
        print(f"   Inspiral:  {df_phase['D_inspiral'].mean():.3f} ± {df_phase['D_inspiral'].std():.3f}")
        print(f"   Ringdown:  {df_phase['D_ringdown'].mean():.3f} ± {df_phase['D_ringdown'].std():.3f}")
        print(f"   Mean ΔD:   {df_phase['FD_drop_pct'].mean():.2f}%")
        print(f"   QC Pass:   {df_phase['passed_QC'].sum()}/{len(df_phase)}")

# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--min-snr', type=float, default=10.0)
    parser.add_argument('--max-events', type=int, default=None)
    parser.add_argument('--output-dir', type=str, default='gwosc_data')
    
    args = parser.parse_args()
    
    print("="*70)
    print("O4 GRAVITATIONAL WAVE FRACTAL DIMENSION ANALYSIS")
    print("="*70)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Min SNR: {args.min_snr}, Max events: {args.max_events or 'all'}")
    
    events_df = GWOSCClient.get_event_catalog(
        min_snr=args.min_snr,
        max_events=args.max_events
    )
    
    if len(events_df) == 0:
        print("✗ No events found")
        return
    
    print(f"\nTop events:")
    print(events_df[['name', 'network_snr', 'mass_1', 'mass_2']].head(10))
    
    results_df = analyze_catalog(events_df, output_dir=args.output_dir)
    
    if len(results_df) == 0:
        print("✗ No results")
        return
    
    print(f"\n{'='*70}")
    print(f"Analyzed: {len(results_df)} observations")
    print(f"{'='*70}")
    
    statistical_summary(results_df)
    
    print("\n✓ Pipeline complete!")

if __name__ == "__main__":
    main()
