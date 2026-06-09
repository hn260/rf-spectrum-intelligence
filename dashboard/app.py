import streamlit as st
import os
import sys
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Add root folder to python path so we can import core services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.services.spectrum_service import get_statistics
from core.services.occupancy_service import get_occupancy_stats, get_activity_heatmap_data
from dashboard.components.ui import inject_custom_css, draw_status_bar, setup_plotly_theme, card_metric

# Set page config
st.set_page_config(
    page_title="RF Spectrum Intelligence Platform",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize layouts and styles
inject_custom_css()
draw_status_bar(sdr_active=False, db_status="LOADED", active_signals=6)
setup_plotly_theme()

# Title Header
st.title("📡 RF Spectrum Intelligence Platform")
st.caption("Professional-grade spectrum database analytics and signal intelligence dashboard")

# Retrieve stats
stats = get_statistics()
occupancy_df = get_occupancy_stats()

# Main Layout: 4 KPI Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    card_metric(
        title="Total Registered Bands",
        value=f"{stats['total_allocations']}",
        desc="0 MHz - 6 GHz allocation registry"
    )

with col2:
    card_metric(
        title="Allocated Bandwidth",
        value=f"{stats['total_bandwidth_mhz']:.1f} MHz",
        desc="Sum of all allocated spectrum slices"
    )

with col3:
    card_metric(
        title="Monitored Channels",
        value="6 Active",
        desc="Active simulated receiver nodes"
    )

with col4:
    # Average occupancy pct across monitored channels
    avg_occ = occupancy_df['occupancy_pct'].mean()
    card_metric(
        title="Avg Channel Occupancy",
        value=f"{avg_occ:.1f}%",
        desc="Telemetry utilization (24h period)",
        is_green=True
    )

st.markdown("---")

# Main Content Grid
main_left, main_right = st.columns([2, 1])

with main_left:
    st.subheader("📊 Monitored Channel Occupancy (Past 24 Hours)")
    st.markdown(
        "Real-time telemetry showing average, maximum, and minimum power levels (in dBm) across critical frequency bands."
    )
    
    # Render Occupancy bar chart
    fig_occ = px.bar(
        occupancy_df,
        x="service",
        y="occupancy_pct",
        color="frequency_mhz",
        labels={"service": "Service / Band", "occupancy_pct": "Time Active (%)", "frequency_mhz": "Frequency (MHz)"},
        color_continuous_scale="Viridis",
        title="Channel Occupancy Percentage (> -75 dBm)"
    )
    fig_occ.update_layout(height=350, margin=dict(t=40, b=40, l=40, r=40))
    st.plotly_chart(fig_occ, use_container_width=True)
    
    st.subheader("🌡️ Time-Frequency Channel Activity Heatmap")
    st.markdown(
        "Monitored SDR spectrum scans showing temporal power density distributions. Light colors represent high activity peaks (burst transmissions)."
    )
    
    # Load heatmap data
    time_labels, freqs, power_mat = get_activity_heatmap_data()
    
    # Render Heatmap
    fig_heat = go.Figure(data=go.Heatmap(
        z=power_mat,
        x=time_labels,
        y=[f"{f} MHz" for f in freqs],
        colorscale="Inferno",
        colorbar=dict(title="Power (dBm)")
    ))
    fig_heat.update_layout(
        title="24-Hour Spectrum Density Waterfall",
        xaxis_title="Time of Day (15m Intervals)",
        yaxis_title="Channel Frequencies",
        height=320,
        margin=dict(t=40, b=40, l=40, r=40)
    )
    st.plotly_chart(fig_heat, use_container_width=True)

with main_right:
    st.subheader("🔔 Live Activity Monitor")
    
    # Activity list
    alerts = [
        {"time": "13:54:12", "type": "ADS-B", "msg": "Squitter pulse detected from AirIndia Flight AI101 at 1090.0 MHz (Signal Peak: -52.4 dBm)", "status": "info"},
        {"time": "13:52:05", "type": "LoRa", "msg": "IoT uplink chirp burst detected at 433.92 MHz. RSSI: -71.2 dBm", "status": "success"},
        {"time": "13:48:30", "type": "AIS", "msg": "Maritime AIS transponder packet decoded at 162.025 MHz (MMSI: 232003840)", "status": "info"},
        {"time": "13:40:15", "type": "Cellular", "msg": "High downstream packet throughput spike on GSM-900 (935.2 MHz)", "status": "warning"},
        {"time": "13:28:54", "type": "Aviation", "msg": "ATC voice carrier detected on Airband (121.5 MHz guard frequency)", "status": "success"}
    ]
    
    for alert in alerts:
        color = "#00f0ff" if alert['status'] == "info" else ("#00e676" if alert['status'] == "success" else "#ff9100")
        st.markdown(
            f"""
            <div style="background-color: #1A1D24; padding: 12px; border-left: 4px solid {color}; border-radius: 4px; margin-bottom: 12px; font-size: 13px;">
                <div style="display: flex; justify-content: space-between; font-weight: bold; margin-bottom: 4px;">
                    <span style="color: {color};">{alert['type']} Detection</span>
                    <span style="color: #8A99AD; font-family: 'JetBrains Mono', monospace; font-size: 11px;">{alert['time']}</span>
                </div>
                <div style="color: #E2E8F0; line-height: 1.4;">{alert['msg']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    st.subheader("🗺️ System Information")
    st.markdown(
        """
        The **RF Spectrum Intelligence Platform** is structured as an extensible analytics suite:
        
        * **Phase 1: Spectrum Explorer** - Search and cross-examine frequency bands across ITU regions.
        * **Phase 2: Signal Analysis** - Upload and analyze complex I/Q recordings.
        * **Phase 3: Machine Learning** - Classify modulations and detect anomalies.
        * **Phase 4: Hardware Integration** - Interface RTL-SDR receivers for live coverage.
        
        Use the sidebar navigation to explore the respective pages.
        """
    )
