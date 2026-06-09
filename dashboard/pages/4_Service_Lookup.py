import streamlit as st
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.services.spectrum_service import lookup_frequency, lookup_service
from dashboard.components.ui import inject_custom_css, draw_status_bar

# Initialize settings
st.set_page_config(
    page_title="Frequency & Service Lookup - RF Spectrum Intelligence Platform",
    page_icon="🔍",
    layout="wide"
)

inject_custom_css()
draw_status_bar(sdr_active=False, db_status="LOADED")

st.title("🔍 Frequency & Service Lookup Tool")
st.markdown("Instantly resolve frequencies to active RF services, or find what bands are allocated to specific technologies.")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📶 Frequency-to-Service Lookup")
    st.markdown("Identify what services are licensed to operate at a specific frequency.")
    
    # Inputs for frequency lookup
    freq_input = st.number_input(
        "Enter Frequency Value",
        min_value=0.0,
        max_value=100000.0,
        value=433.920,
        step=0.001,
        format="%.3f"
    )
    
    unit_input = st.selectbox(
        "Frequency Unit",
        options=["Hz", "kHz", "MHz", "GHz"],
        index=2 # Default to MHz
    )
    
    # Convert input to MHz
    freq_mhz = freq_input
    if unit_input == "Hz":
        freq_mhz = freq_input / 1e6
    elif unit_input == "kHz":
        freq_mhz = freq_input / 1e3
    elif unit_input == "GHz":
        freq_mhz = freq_input * 1e3
        
    st.markdown(f"**Query frequency:** `{freq_mhz:.6f} MHz` ({freq_input} {unit_input})")
    
    # Run lookup
    matches = lookup_frequency(freq_mhz)
    
    if matches.empty:
        st.warning(f"No specific services found in database overlapping {freq_mhz:.3f} MHz.")
    else:
        for _, row in matches.iterrows():
            st.markdown(
                f"""
                <div style="background-color: #1A1D24; border: 1px solid #00f0ff; border-radius: 6px; padding: 16px; margin-bottom: 12px; box-shadow: 0 0 10px rgba(0, 240, 255, 0.15);">
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #00f0ff; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 1px;">
                        Active Allocation Range: {row['start_mhz']:.3f} - {row['end_mhz']:.3f} MHz
                    </div>
                    <div style="font-size: 20px; font-weight: bold; color: #E2E8F0; margin-bottom: 8px;">
                        {row['service']}
                    </div>
                    <div style="font-size: 14px; font-weight: bold; color: #ff9100; margin-bottom: 6px;">
                        Subservice / Classification: {row['subservice']}
                    </div>
                    <p style="font-size: 13px; color: #E2E8F0; line-height: 1.5; margin-bottom: 10px;">
                        {row['description']}
                    </p>
                    <div style="font-size: 12px; color: #8A99AD; border-top: 1px solid #2D3748; padding-top: 8px; margin-top: 8px;">
                        <strong>Common Uses / Tech:</strong> {row['common_applications']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

with col_right:
    st.subheader("📡 Service-to-Frequency Lookup")
    st.markdown("Search for frequency bands allocated to specific services (e.g. Amateur, Airband, GSM, Wi-Fi).")
    
    service_query = st.text_input(
        "Enter Service Name or Keyword",
        value="Aviation",
        placeholder="e.g. Amateur, Satellite, Maritime, LoRa, LTE..."
    )
    
    if service_query.strip():
        # Run lookup
        matches_srv = lookup_service(service_query)
        
        if matches_srv.empty:
            st.warning(f"No frequency allocations matched the keyword '{service_query}'.")
        else:
            st.success(f"Found {len(matches_srv)} allocated bands matching '{service_query}'.")
            
            for _, row in matches_srv.iterrows():
                freq_label = f"{row['start_mhz']:.3f} MHz - {row['end_mhz']:.3f} MHz" if row['start_mhz'] >= 1.0 else f"{row['start_mhz'] * 1000:.0f} kHz - {row['end_mhz'] * 1000:.0f} kHz"
                
                st.markdown(
                    f"""
                    <div style="background-color: #1E222B; border: 1px solid #2D3748; border-radius: 6px; padding: 14px; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span style="font-size: 14px; font-weight: bold; color: #ff9100;">{row['service']}</span>
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: bold; color: #00e676;">{freq_label}</span>
                        </div>
                        <div style="font-size: 12px; color: #8A99AD; margin-bottom: 4px;">
                            <strong>Subservice:</strong> {row['subservice']} &middot; <strong>Region:</strong> {row['region']}
                        </div>
                        <div style="font-size: 13px; color: #E2E8F0; line-height: 1.4;">
                            {row['description']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
