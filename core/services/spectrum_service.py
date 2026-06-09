import os
import pandas as pd
import numpy as np

# Path to the allocations database
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "processed",
    "spectrum_allocations.csv"
)

def load_allocations() -> pd.DataFrame:
    """
    Loads the spectrum allocations database.
    """
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Spectrum database not found at: {DB_PATH}")
    
    df = pd.read_csv(DB_PATH)
    # Ensure float conversions
    df['start_mhz'] = pd.to_numeric(df['start_mhz'], errors='coerce')
    df['end_mhz'] = pd.to_numeric(df['end_mhz'], errors='coerce')
    # Filter out rows with invalid frequencies
    df = df.dropna(subset=['start_mhz', 'end_mhz'])
    return df

def get_all_allocations() -> pd.DataFrame:
    """
    Returns the complete list of allocations.
    """
    return load_allocations()

def query_allocations(
    query_str: str = None, 
    min_freq: float = None, 
    max_freq: float = None, 
    regions: list = None,
    countries: list = None
) -> pd.DataFrame:
    """
    Queries allocations based on search string, frequency overlap, and region/country.
    """
    df = load_allocations()
    
    # Frequency overlap filtering
    # Overlap occurs when start_mhz <= max_freq and end_mhz >= min_freq
    if min_freq is not None:
        df = df[df['end_mhz'] >= min_freq]
    if max_freq is not None:
        df = df[df['start_mhz'] <= max_freq]
        
    # Region filtering
    if regions:
        # If 'Global' is in regions, keep rows that are 'Global' or the selected regions
        if 'Global' in regions:
            df = df[df['region'].isin(regions) | (df['region'] == 'Global')]
        else:
            df = df[df['region'].isin(regions)]
            
    # Country filtering
    if countries:
        if 'Global' in countries:
            df = df[df['country'].isin(countries) | (df['country'] == 'Global')]
        else:
            df = df[df['country'].isin(countries)]
            
    # Keyword query search
    if query_str and query_str.strip():
        q = query_str.strip().lower()
        mask = (
            df['service'].str.lower().str.contains(q, na=False) |
            df['subservice'].str.lower().str.contains(q, na=False) |
            df['description'].str.lower().str.contains(q, na=False) |
            df['common_applications'].str.lower().str.contains(q, na=False)
        )
        df = df[mask]
        
    return df

def lookup_frequency(freq_mhz: float) -> pd.DataFrame:
    """
    Looks up which bands overlap the specified frequency.
    """
    df = load_allocations()
    return df[(df['start_mhz'] <= freq_mhz) & (df['end_mhz'] >= freq_mhz)]

def lookup_service(service_name: str) -> pd.DataFrame:
    """
    Looks up bands that match a service name.
    """
    df = load_allocations()
    q = service_name.strip().lower()
    return df[df['service'].str.lower().str.contains(q, na=False)]

def get_statistics() -> dict:
    """
    Calculates statistics about the spectrum allocations database.
    """
    df = load_allocations()
    
    total_allocations = len(df)
    
    # Calculate bandwidth for each entry
    df['bandwidth'] = df['end_mhz'] - df['start_mhz']
    total_bandwidth = df['bandwidth'].sum()
    
    # Service distributions
    service_counts = df['service'].value_counts().to_dict()
    service_bandwidths = df.groupby('service')['bandwidth'].sum().to_dict()
    
    # Region distribution
    region_counts = df['region'].value_counts().to_dict()
    
    # Top 5 largest bands
    largest_bands = df.sort_values(by='bandwidth', ascending=False).head(5)[
        ['start_mhz', 'end_mhz', 'service', 'subservice', 'bandwidth']
    ].to_dict('records')
    
    return {
        "total_allocations": total_allocations,
        "total_bandwidth_mhz": total_bandwidth,
        "service_counts": service_counts,
        "service_bandwidths": service_bandwidths,
        "region_counts": region_counts,
        "largest_bands": largest_bands
    }
