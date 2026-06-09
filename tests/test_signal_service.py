import sys
import os
import numpy as np
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.services.signal_service import (
    generate_synthetic_iq, 
    compute_fft, 
    compute_spectrogram, 
    detect_peaks, 
    identify_signal
)

def test_generate_synthetic_iq():
    """Test generating different mock IQ baseband signals."""
    sample_rate = 2e6
    duration = 0.1
    expected_len = int(sample_rate * duration)
    
    # Generate FM
    iq_fm = generate_synthetic_iq("FM Broadcast", 100e6, sample_rate, duration)
    assert isinstance(iq_fm, np.ndarray)
    assert iq_fm.dtype == np.complex128 or iq_fm.dtype == np.complex64
    assert len(iq_fm) == expected_len
    
    # Generate noise
    iq_noise = generate_synthetic_iq("Noise Only", 100e6, sample_rate, duration)
    assert len(iq_noise) == expected_len

def test_compute_fft():
    """Test FFT computation returns correct shapes and bounds."""
    sample_rate = 2e6
    iq = generate_synthetic_iq("FM Broadcast", 98.5e6, sample_rate, 0.1)
    
    freqs, psd = compute_fft(iq, sample_rate)
    
    assert len(freqs) == len(iq)
    assert len(psd) == len(iq)
    # Frequencies should range from -SR/2 to +SR/2
    assert np.allclose(freqs[0], -sample_rate / 2.0)
    assert np.allclose(freqs[-1], (sample_rate / 2.0) - (sample_rate / len(iq)))
    # Power levels should be in dBFS (negative values generally)
    assert (psd < 20).all()

def test_compute_spectrogram():
    """Test spectrogram (waterfall) matrix calculation."""
    sample_rate = 2e6
    iq = generate_synthetic_iq("FM Broadcast", 98.5e6, sample_rate, 0.2)
    
    res = compute_spectrogram(iq, sample_rate, nperseg=256, noverlap=128)
    
    assert "times" in res
    assert "freqs" in res
    assert "spectrogram_db" in res
    
    # Check shape of 2D matrix
    assert len(res["freqs"]) == 256
    assert res["spectrogram_db"].shape == (len(res["times"]), 256)

def test_detect_peaks():
    """Test peak detector detects simulated signals."""
    sample_rate = 2e6
    # Generate pure carrier (sine wave) offset by +400 kHz
    t = np.linspace(0, 0.1, int(sample_rate * 0.1), endpoint=False)
    iq = np.exp(1j * 2 * np.pi * 400000 * t) # Pure carrier, no noise
    
    freqs, psd = compute_fft(iq, sample_rate)
    peaks = detect_peaks(freqs, psd, threshold_db=-20.0, min_dist=5)
    
    assert len(peaks) > 0
    # Primary peak should be around 400 kHz
    primary_peak = peaks[0]
    assert np.abs(primary_peak["frequency_hz"] - 400000) < 5000 # within 5 kHz

def test_identify_signal():
    """Test signal identification classifier rules."""
    # Peak at 98.5 MHz offset 0 should match FM Broadcast
    peaks_fm = [{"frequency_hz": 0.0, "power_db": -10.0}]
    res_fm = identify_signal(98.5, 2.0, peaks_fm)
    assert res_fm["signal_type"] == "FM Broadcast"
    assert res_fm["confidence"] >= 90.0
    
    # Peak at 1090 MHz matching ADS-B
    peaks_adsb = [{"frequency_hz": 0.0, "power_db": -5.0}]
    res_adsb = identify_signal(1090.0, 2.0, peaks_adsb)
    assert res_adsb["signal_type"] == "ADS-B Transponder"
    
    # No peaks should return Noise/Unknown
    res_noise = identify_signal(100.0, 2.0, [])
    assert "Noise/Unknown" in res_noise["signal_type"]
