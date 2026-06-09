import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

MEASUREMENT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "processed",
    "rf_occupancy_simulated.csv"
)

def generate_mock_occupancy_data() -> pd.DataFrame:
    """
    Generates a realistic mock RF measurement dataset over the last 24 hours.
    Frequencies monitored:
    - 98.5 MHz (FM radio, highly active, steady)
    - 121.5 MHz (Aviation guard, sparse pulses)
    - 433.92 MHz (ISM/LoRa, periodic bursts)
    - 880.2 MHz (Cellular, medium/high active)
    - 1090.0 MHz (ADS-B, periodic bursts, higher at daytime)
    - 2412.0 MHz (Wi-Fi, very busy)
    """
    np.random.seed(42)
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)
    
    # 15-minute intervals for 24 hours = 96 time steps
    times = [start_time + timedelta(minutes=15 * i) for i in range(96)]
    
    frequencies = [98.5, 121.5, 433.92, 880.2, 1090.0, 2412.0]
    data = []
    
    for t in times:
        hour = t.hour
        # Diurnal activity coefficient (activity is lower between 1 AM and 6 AM)
        activity_coeff = 0.2 if 1 <= hour <= 5 else (0.8 if 8 <= hour <= 20 else 0.5)
        
        for freq in frequencies:
            # Base noise floor around -100 dBm to -95 dBm
            power = np.random.normal(-98.0, 2.0)
            
            # Simulate actual signals on top of noise
            if freq == 98.5:
                # FM Radio is constantly broadcasting
                power = np.random.normal(-55.0, 3.0)
            elif freq == 121.5:
                # Aviation emergency - very rare
                if np.random.rand() < 0.02 * activity_coeff:
                    power = np.random.normal(-65.0, 5.0)
            elif freq == 433.92:
                # ISM devices - periodic bursts
                if np.random.rand() < 0.3 * activity_coeff:
                    power = np.random.normal(-72.0, 8.0)
            elif freq == 880.2:
                # Cellular downlink - always active, variable load
                cellular_load = 0.3 + 0.6 * activity_coeff
                power = np.random.normal(-98.0 + 40.0 * cellular_load, 4.0)
            elif freq == 1090.0:
                # ADS-B transponders - busy during daytime flights
                flight_density = 0.1 if hour < 6 else (0.9 if 9 <= hour <= 19 else 0.5)
                if np.random.rand() < 0.6 * flight_density:
                    power = np.random.normal(-60.0 + 10.0 * np.random.rand(), 6.0)
            elif freq == 2412.0:
                # Wi-Fi - busy, higher in evenings
                wifi_usage = 0.2 if hour < 6 else (0.9 if 18 <= hour <= 23 else 0.6)
                power = np.random.normal(-98.0 + 45.0 * wifi_usage, 3.0)
                
            data.append({
                "timestamp": t.strftime("%Y-%m-%d %H:%M:%S"),
                "frequency_mhz": freq,
                "power_db": round(power, 2),
                "location": "Aero-Monitor-01",
                "source": "Simulated SDR Receiver"
            })
            
    df = pd.DataFrame(data)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(MEASUREMENT_PATH), exist_ok=True)
    df.to_csv(MEASUREMENT_PATH, index=False)
    return df

def load_occupancy_data() -> pd.DataFrame:
    """
    Loads simulated RF measurement data. Generates it if missing.
    """
    if not os.path.exists(MEASUREMENT_PATH):
        return generate_mock_occupancy_data()
    df = pd.read_csv(MEASUREMENT_PATH)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def get_occupancy_stats(threshold_db: float = -75.0) -> pd.DataFrame:
    """
    Computes occupancy percentage (time spent above threshold) for each monitored frequency.
    """
    df = load_occupancy_data()
    
    # Group by frequency and calculate fraction of time power is above threshold
    stats = []
    for freq, group in df.groupby('frequency_mhz'):
        total_records = len(group)
        active_records = len(group[group['power_db'] > threshold_db])
        occupancy_pct = (active_records / total_records) * 100.0
        
        avg_power = group['power_db'].mean()
        max_power = group['power_db'].max()
        min_power = group['power_db'].min()
        
        # Match with service name
        service = "Unknown"
        if freq == 98.5:
            service = "FM Broadcast"
        elif freq == 121.5:
            service = "Aviation Communications"
        elif freq == 433.92:
            service = "ISM / LoRa"
        elif freq == 880.2:
            service = "Mobile Cellular"
        elif freq == 1090.0:
            service = "ADS-B Transponder"
        elif freq == 2412.0:
            service = "Wi-Fi 2.4 GHz"
            
        stats.append({
            "frequency_mhz": freq,
            "service": service,
            "occupancy_pct": round(occupancy_pct, 1),
            "avg_power_db": round(avg_power, 1),
            "max_power_db": round(max_power, 1),
            "min_power_db": round(min_power, 1)
        })
        
    return pd.DataFrame(stats)

def get_activity_heatmap_data() -> Tuple[list, list, np.ndarray]:
    """
    Formats the measurement data into matrix coordinates for heatmaps.
    Returns:
        timestamps (list), frequencies (list), power_matrix (np.ndarray)
    """
    df = load_occupancy_data()
    # Sort frequencies and times
    freqs = sorted(df['frequency_mhz'].unique())
    times = sorted(df['timestamp'].unique())
    
    # Pivot dataframe
    pivot_df = df.pivot(index='timestamp', columns='frequency_mhz', values='power_db')
    
    # Convert index timestamps to string format for display
    time_labels = [pd.to_datetime(t).strftime("%H:%M") for t in times]
    
    return time_labels, freqs, pivot_df.values.T
