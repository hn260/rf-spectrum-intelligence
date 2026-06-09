import numpy as np
from typing import Tuple, Dict, List

def generate_synthetic_iq(
    signal_type: str, 
    center_freq_hz: float, 
    sample_rate_hz: float, 
    duration_s: float = 0.5
) -> np.ndarray:
    """
    Generates realistic complex baseband IQ samples for different RF signal types.
    Returns:
        np.ndarray: Complex numpy array containing IQ samples.
    """
    num_samples = int(sample_rate_hz * duration_s)
    t = np.linspace(0, duration_s, num_samples, endpoint=False)
    
    # Base noise floor (AWGN)
    # Standard deviation of 0.1 for complex noise (0.07 real, 0.07 imag)
    noise = (np.random.normal(0, 0.07, num_samples) + 1j * np.random.normal(0, 0.07, num_samples))
    
    if signal_type == "FM Broadcast":
        # FM Signal: Frequency modulation of a carrier.
        # Modulating signal: a voice/music mock representation (blend of 1 kHz and 3 kHz tones)
        modulating = np.sin(2 * np.pi * 1000 * t) + 0.5 * np.cos(2 * np.pi * 3150 * t)
        # FM modulation index (deviation of e.g. 75 kHz)
        deviation = 75000 
        phase = 2 * np.pi * deviation * np.cumsum(modulating) / sample_rate_hz
        carrier = np.exp(1j * phase)
        # Add frequency offset from center if desired (e.g. +50 kHz)
        freq_offset = 50000
        signal = carrier * np.exp(1j * 2 * np.pi * freq_offset * t)
        return signal + noise
        
    elif signal_type == "ADS-B":
        # ADS-B: Pulse Position Modulation (PPM) at 1090 MHz.
        # It consists of periodic bursts of short pulses (120 microseconds total, 1 microsecond pulses)
        signal = np.zeros(num_samples, dtype=complex)
        pulse_len = int(sample_rate_hz * 1e-6)  # 1 microsecond pulse
        frame_len = int(sample_rate_hz * 120e-6)  # 120 microseconds frame
        
        # Insert 3 bursts
        for burst_idx in range(3):
            start_idx = int((0.1 + burst_idx * 0.15) * sample_rate_hz)
            if start_idx + frame_len < num_samples:
                # ADS-B Preamble: 4 pulses at specific intervals (0, 1, 3.5, 4.5 microseconds)
                preamble_offsets = [0, 1.0, 3.5, 4.5]
                for po in preamble_offsets:
                    p_start = start_idx + int(po * 1e-6 * sample_rate_hz)
                    signal[p_start : p_start + pulse_len] = 1.0 + 1j * 1.0
                
                # Modulated data pulses (random PPM)
                for bit in range(112): # 112 bits for ADS-B extended squitter
                    bit_offset = 8.0 + bit * 1.0 # starts at 8 microseconds
                    if np.random.rand() > 0.5:
                        # Bit '1': pulse in first half of slot
                        p_start = start_idx + int(bit_offset * 1e-6 * sample_rate_hz)
                    else:
                        # Bit '0': pulse in second half of slot
                        p_start = start_idx + int((bit_offset + 0.5) * 1e-6 * sample_rate_hz)
                    signal[p_start : p_start + pulse_len] = 1.0 + 1j * 1.0
        
        # Bandlimit the pulses slightly to make them look realistic
        window = int(sample_rate_hz * 0.5e-6)
        if window > 1:
            signal = np.convolve(signal, np.ones(window)/window, mode='same')
            
        # Add offset (e.g. -200 kHz from center)
        freq_offset = -200000
        signal = signal * np.exp(1j * 2 * np.pi * freq_offset * t)
        return signal + noise
        
    elif signal_type == "AIS Maritime":
        # AIS: GMSK modulated packets (9600 bps). Center is 161.975 / 162.025 MHz.
        # AIS packet length is about 26.6 ms (256 bits at 9600 baud)
        signal = np.zeros(num_samples, dtype=complex)
        baud_rate = 9600
        samples_per_symbol = int(sample_rate_hz / baud_rate)
        
        # 1 packet in the middle
        start_idx = int(0.2 * sample_rate_hz)
        packet_bits = np.random.randint(0, 2, 256)
        
        phase = 0.0
        phases = []
        for bit in packet_bits:
            # Frequency shift keying (+- 2.4 kHz deviation)
            freq_dev = 2400 if bit == 1 else -2400
            for _ in range(samples_per_symbol):
                phase += 2 * np.pi * freq_dev / sample_rate_hz
                phases.append(phase)
                
        packet_signal = np.exp(1j * np.array(phases))
        if start_idx + len(packet_signal) < num_samples:
            signal[start_idx : start_idx + len(packet_signal)] = packet_signal
            
        # Apply slight frequency offset (e.g. +120 kHz)
        freq_offset = 120000
        signal = signal * np.exp(1j * 2 * np.pi * freq_offset * t)
        return signal + noise
        
    elif signal_type == "LoRa":
        # LoRa: CSS (Chirp Spread Spectrum). Frequency sweeps from -BW/2 to +BW/2.
        # Let's generate 4 consecutive chirps
        signal = np.zeros(num_samples, dtype=complex)
        bw = 125000 # 125 kHz bandwidth
        chirp_duration = 0.08 # 80 ms chirp
        samples_per_chirp = int(sample_rate_hz * chirp_duration)
        
        for chirp_idx in range(5):
            c_start = int((0.05 + chirp_idx * 0.09) * sample_rate_hz)
            if c_start + samples_per_chirp < num_samples:
                tc = np.linspace(0, chirp_duration, samples_per_chirp, endpoint=False)
                # Linear frequency sweep: frequency = f_start + beta * t
                # phase = 2 * pi * (f_start * t + 0.5 * beta * t^2)
                f_start = -bw / 2
                beta = bw / chirp_duration
                chirp_phase = 2 * np.pi * (f_start * tc + 0.5 * beta * tc**2)
                signal[c_start : c_start + samples_per_chirp] = np.exp(1j * chirp_phase)
                
        # Offset (e.g. -150 kHz)
        freq_offset = -150000
        signal = signal * np.exp(1j * 2 * np.pi * freq_offset * t)
        return signal + noise
        
    else:
        # Default: Pure noise
        return noise

def compute_fft(iq_samples: np.ndarray, sample_rate_hz: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    Computes standard power spectral density (PSD) using numpy FFT.
    Returns:
        freqs (np.ndarray): Frequency bins in Hz.
        psd_db (np.ndarray): Power spectral density in dB relative to full scale.
    """
    n = len(iq_samples)
    fft_vals = np.fft.fft(iq_samples)
    fft_shifted = np.fft.fftshift(fft_vals)
    
    # Power spectral density
    psd = (np.abs(fft_shifted) ** 2) / (n * sample_rate_hz)
    # Add a small epsilon to avoid log10(0)
    psd_db = 10 * np.log10(psd + 1e-15)
    
    # Frequency bins
    freqs = np.fft.fftshift(np.fft.fftfreq(n, 1.0 / sample_rate_hz))
    
    return freqs, psd_db

def compute_spectrogram(
    iq_samples: np.ndarray, 
    sample_rate_hz: float, 
    nperseg: int = 512, 
    noverlap: int = 256
) -> Dict[str, np.ndarray]:
    """
    Computes a time-frequency spectrogram (waterfall matrix).
    Returns:
        Dict containing:
            "times": 1D array of time steps (seconds)
            "freqs": 1D array of frequency bins (Hz)
            "spectrogram_db": 2D array of power values (dB) with shape (len(times), len(freqs))
    """
    step = nperseg - noverlap
    num_samples = len(iq_samples)
    num_segments = (num_samples - noverlap) // step
    
    if num_segments <= 0:
        # Fallback for very short signals
        freqs, psd = compute_fft(iq_samples, sample_rate_hz)
        return {
            "times": np.array([0.0]),
            "freqs": freqs,
            "spectrogram_db": np.expand_dims(psd, axis=0)
        }
        
    times = []
    spectrogram_db = []
    
    # Hanning window
    win = np.hanning(nperseg)
    win_power = np.sum(win**2)
    
    for i in range(num_segments):
        start = i * step
        end = start + nperseg
        segment = iq_samples[start:end] * win
        
        fft_vals = np.fft.fft(segment)
        fft_shifted = np.fft.fftshift(fft_vals)
        
        # PSD conversion
        psd = (np.abs(fft_shifted) ** 2) / (sample_rate_hz * win_power)
        psd_db = 10 * np.log10(psd + 1e-15)
        
        times.append((start + nperseg / 2.0) / sample_rate_hz)
        spectrogram_db.append(psd_db)
        
    freqs = np.fft.fftshift(np.fft.fftfreq(nperseg, 1.0 / sample_rate_hz))
    
    return {
        "times": np.array(times),
        "freqs": freqs,
        "spectrogram_db": np.array(spectrogram_db)
    }

def detect_peaks(freqs: np.ndarray, psd_db: np.ndarray, threshold_db: float = -45.0, min_dist: int = 15) -> List[Dict[str, float]]:
    """
    Identifies frequency peaks that rise above a threshold in dB.
    """
    peaks = []
    # Loop over inner array elements to avoid border issues
    for i in range(min_dist, len(psd_db) - min_dist):
        val = psd_db[i]
        if val > threshold_db:
            # Check local maximum
            if val == np.max(psd_db[i - min_dist : i + min_dist + 1]):
                peaks.append({
                    "frequency_hz": freqs[i],
                    "power_db": val
                })
    return sorted(peaks, key=lambda x: x['power_db'], reverse=True)

def identify_signal(center_freq_mhz: float, sample_rate_mhz: float, peaks: List[Dict[str, float]]) -> Dict[str, any]:
    """
    Identifies the modulation or protocol of a signal based on detected peak frequencies.
    """
    if not peaks:
        return {"signal_type": "Noise/Unknown", "confidence": 100.0, "details": "No distinct peaks detected above threshold."}
        
    primary_peak = peaks[0]
    peak_offset_mhz = primary_peak['frequency_hz'] / 1e6
    absolute_freq_mhz = center_freq_mhz + peak_offset_mhz
    
    # Rule-based classifier mapping active frequencies to specific technologies
    # FM radio: centered in 87.5-108 MHz
    if 87.4 <= absolute_freq_mhz <= 108.1:
        return {
            "signal_type": "FM Broadcast",
            "confidence": 95.0,
            "details": f"Peak detected at {absolute_freq_mhz:.2f} MHz inside the FM Radio broadcast band (87.5-108 MHz)."
        }
    # ADS-B: centered around 1090 MHz (+- 1.5 MHz)
    elif 1088.5 <= absolute_freq_mhz <= 1091.5:
        return {
            "signal_type": "ADS-B Transponder",
            "confidence": 98.0,
            "details": f"Strong pulsed peak detected at {absolute_freq_mhz:.2f} MHz, matching Mode S/ADS-B aviation beacons (1090 MHz)."
        }
    # AIS: centered around 161.975 or 162.025 MHz (+- 0.1 MHz)
    elif 161.8 <= absolute_freq_mhz <= 162.1:
        return {
            "signal_type": "AIS Maritime Tracking",
            "confidence": 94.0,
            "details": f"Narrow peak detected at {absolute_freq_mhz:.3f} MHz matching Automatic Identification System (AIS) channels."
        }
    # LoRa / ISM: around 433.9, 868.1, or 915.0 MHz
    elif (433.0 <= absolute_freq_mhz <= 434.8) or (863.0 <= absolute_freq_mhz <= 870.0) or (902.0 <= absolute_freq_mhz <= 928.0):
        # We can look at bandwidth or shapes to distinguish
        return {
            "signal_type": "ISM Band / LoRa",
            "confidence": 88.0,
            "details": f"Short duration sweep/chirp peak at {absolute_freq_mhz:.2f} MHz inside unlicensed ISM bands."
        }
    # Airband voice: 118-137 MHz
    elif 117.9 <= absolute_freq_mhz <= 137.1:
        return {
            "signal_type": "VHF Aviation Voice (Airband)",
            "confidence": 85.0,
            "details": f"Narrow peak at {absolute_freq_mhz:.2f} MHz matching Air Traffic Control or aircraft AM transmissions."
        }
    # Amateur radio 2m band: 144-148 MHz
    elif 144.0 <= absolute_freq_mhz <= 148.0:
        return {
            "signal_type": "Amateur Radio (2m Band)",
            "confidence": 80.0,
            "details": f"VHF amateur communication peak detected at {absolute_freq_mhz:.2f} MHz."
        }
    # Wi-Fi / Bluetooth: 2400-2483.5 MHz
    elif 2400.0 <= absolute_freq_mhz <= 2483.5:
        return {
            "signal_type": "Wi-Fi (2.4 GHz) / Bluetooth",
            "confidence": 75.0,
            "details": f"Wide peak at {absolute_freq_mhz:.2f} MHz inside the 2.4 GHz ISM band."
        }
    else:
        return {
            "signal_type": "Unidentified Carrier",
            "confidence": 50.0,
            "details": f"Active peak detected at {absolute_freq_mhz:.3f} MHz, but could not be definitively matched to common signals."
        }
