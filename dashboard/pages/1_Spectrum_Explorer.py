import streamlit as st
import os
import sys
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.services.spectrum_service import query_allocations, load_allocations
from dashboard.components.ui import inject_custom_css, draw_status_bar

# Initialize settings
st.set_page_config(
    page_title="Spectrum Explorer - RF Spectrum Intelligence Platform",
    page_icon="🔍",
    layout="wide"
)

inject_custom_css()
draw_status_bar(sdr_active=False, db_status="LOADED")

st.title("🔍 Spectrum Explorer")
st.markdown("Browse, search, and filter the global frequency allocation registry (0 MHz - 6 GHz).")

# Load full DB for filter dropdowns
df_full = load_allocations()
services_list = sorted(df_full['service'].dropna().unique())
regions_list = sorted(df_full['region'].dropna().unique())
countries_list = sorted(df_full['country'].dropna().unique())

# Top Filters Container
st.subheader("Filter & Search Controls")

# Search and Range inputs
col1, col2 = st.columns([2, 3])

with col1:
    search_query = st.text_input(
        "Keyword Search", 
        placeholder="e.g. ADS-B, LoRa, Amateur, Airband...",
        help="Searches service, subservice, description, and common applications fields."
    )

with col2:
    freq_range = st.slider(
        "Frequency Range (MHz)",
        min_value=0.0,
        max_value=6000.0,
        value=(0.0, 6000.0),
        step=0.1,
        help="Select a range to find overlapping allocations."
    )

# Region & Country filters
col3, col4 = st.columns(2)

with col3:
    selected_regions = st.multiselect(
        "ITU Regions",
        options=regions_list,
        default=[],
        placeholder="All Regions"
    )

with col4:
    selected_countries = st.multiselect(
        "Countries",
        options=countries_list,
        default=[],
        placeholder="All Countries"
    )

# Run Query
filtered_df = query_allocations(
    query_str=search_query,
    min_freq=freq_range[0],
    max_freq=freq_range[1],
    regions=selected_regions,
    countries=selected_countries
)

# Display Results
st.markdown("---")
count = len(filtered_df)
st.subheader(f"Results ({count} bands found)")

if filtered_df.empty:
    st.info("No frequency bands matched the specified search criteria. Try broadening your filters.")
else:
    # Display results as nice custom engineering cards instead of a raw table
    cols = st.columns(1) # We can display in a vertical list, styled beautifully
    
    for _, row in filtered_df.iterrows():
        # Custom coloring for service types
        tag_color = "#00f0ff" # default blue/cyan
        s = str(row['service']).lower()
        if "amateur" in s:
            tag_color = "#b388ff" # purple
        elif "cellular" in s or "mobile" in s:
            tag_color = "#ff9100" # orange
        elif "navigation" in s or "aviation" in s:
            tag_color = "#00e676" # green
        elif "ism" in s:
            tag_color = "#f4ff81" # yellow
        elif "satellite" in s:
            tag_color = "#ff8a80" # light red
            
        freq_label = f"{row['start_mhz']:.3f} MHz - {row['end_mhz']:.3f} MHz" if row['start_mhz'] >= 1.0 else f"{row['start_mhz'] * 1000:.0f} kHz - {row['end_mhz'] * 1000:.0f} kHz"
        
        st.markdown(
            f"""
            <div style="background-color: #1E222B; border: 1px solid #2D3748; border-radius: 6px; padding: 18px; margin-bottom: 12px; transition: border-color 0.2s;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; flex-wrap: wrap;">
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 16px; font-weight: bold; color: #00f0ff;">
                        {freq_label}
                    </div>
                    <div style="background-color: {tag_color}22; border: 1px solid {tag_color}; border-radius: 4px; padding: 3px 8px; font-size: 11px; font-family: 'JetBrains Mono', monospace; color: {tag_color}; font-weight: bold; text-transform: uppercase;">
                        {row['service']}
                    </div>
                </div>
                <div style="font-size: 15px; font-weight: 600; color: #E2E8F0; margin-bottom: 6px;">
                    {row['subservice']} &nbsp;|&nbsp; 
                    <span style="color: #8A99AD; font-size: 13px; font-weight: normal;">Region: {row['region']} ({row['country']})</span>
                </div>
                <div style="font-size: 13px; color: #E2E8F0; line-height: 1.5; margin-bottom: 8px;">
                    {row['description']}
                </div>
                <div style="font-size: 12px; color: #8A99AD;">
                    <strong style="color: #E2E8F0;">Common Applications:</strong> {row['common_applications']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
