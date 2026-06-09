import sys
import os
import pandas as pd
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.services.spectrum_service import load_allocations, query_allocations, lookup_frequency, get_statistics

def test_load_allocations():
    """Test that allocations CSV loads successfully and has valid columns."""
    df = load_allocations()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'start_mhz' in df.columns
    assert 'end_mhz' in df.columns
    assert 'service' in df.columns
    
    # Check that all start_mhz <= end_mhz
    assert (df['start_mhz'] <= df['end_mhz']).all()

def test_query_allocations():
    """Test filtering allocations by keyword and frequency range."""
    # Keyword search for FM
    res_fm = query_allocations(query_str="FM Broadcast")
    assert not res_fm.empty
    assert any(res_fm['service'].str.contains("FM", case=False))
    
    # Frequency range overlap
    res_range = query_allocations(min_freq=100.0, max_freq=120.0)
    assert not res_range.empty
    # At least one band should overlap 100-120 MHz (e.g., FM ends at 108, Airband starts at 118)
    assert any((res_range['start_mhz'] <= 120.0) & (res_range['end_mhz'] >= 100.0))

def test_lookup_frequency():
    """Test lookup of a single frequency matches expected services."""
    # 98.5 MHz should overlap the FM Broadcast band (87.5 - 108.0 MHz)
    res = lookup_frequency(98.5)
    assert not res.empty
    assert any(res['service'] == "FM Broadcast")
    
    # 1090 MHz should overlap the ADS-B band
    res_adsb = lookup_frequency(1090.0)
    assert not res_adsb.empty
    assert any("DME/TACAN/ADS-B" in str(row['subservice']) or "ADS-B" in str(row['service']) for _, row in res_adsb.iterrows())

def test_get_statistics():
    """Test calculation of database statistics."""
    stats = get_statistics()
    assert "total_allocations" in stats
    assert "total_bandwidth_mhz" in stats
    assert "service_counts" in stats
    assert "largest_bands" in stats
    
    assert stats["total_allocations"] > 0
    assert stats["total_bandwidth_mhz"] > 0
    assert len(stats["largest_bands"]) == 5
