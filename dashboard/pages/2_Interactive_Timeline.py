import streamlit as st
import os
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.services.spectrum_service import load_allocations
from dashboard.components.ui import inject_custom_css, draw_status_bar, setup_plotly_theme

# Initialize settings
st.set_page_config(
    page_title="Spectrum Timeline - RF Spectrum Intelligence Platform",
    page_icon="📊",
    layout="wide"
)

inject_custom_css()
draw_status_bar(sdr_active=False, db_status="LOADED")
setup_plotly_theme()

st.title("📊 Interactive Spectrum Timeline")
st.markdown("Visualize the entire radio frequency allocations grid from 0 MHz to 6 GHz. Hover to inspect bands and zoom in/out to examine specific frequencies.")

# Load database
df = load_allocations()

# Add frequency presets
st.subheader("Frequency Preset Scales")
col1, col2, col3, col4, col5 = st.columns(5)

# Initialize session state for bounds
if 'timeline_min' not in st.session_state:
    st.session_state.timeline_min = 0.0
if 'timeline_max' not in st.session_state:
    st.session_state.timeline_max = 3000.0

with col1:
    if st.button("🌐 Full (0 MHz - 6 GHz)"):
        st.session_state.timeline_min = 0.0
        st.session_state.timeline_max = 6000.0
with col2:
    if st.button("📻 HF Band (1.8 - 30 MHz)"):
        st.session_state.timeline_min = 1.8
        st.session_state.timeline_max = 30.0
with col3:
    if st.button("✈️ VHF Band (30 - 300 MHz)"):
        st.session_state.timeline_min = 30.0
        st.session_state.timeline_max = 300.0
with col4:
    if st.button("📡 UHF Band (300 - 3000 MHz)"):
        st.session_state.timeline_min = 300.0
        st.session_state.timeline_max = 3000.0
with col5:
    if st.button("⚡ SHF Band (3 - 6 GHz)"):
        st.session_state.timeline_min = 3000.0
        st.session_state.timeline_max = 6000.0

# Dynamic sliders for custom bounds
cust_min, cust_max = st.slider(
    "Fine-tune Frequency Range (MHz)",
    min_value=0.0,
    max_value=6000.0,
    value=(st.session_state.timeline_min, st.session_state.timeline_max),
    step=0.1
)

# Apply filters
df_filtered = df[
    (df['end_mhz'] >= cust_min) & 
    (df['start_mhz'] <= cust_max)
].copy()

# Add a bandwidth column
df_filtered['bandwidth_mhz'] = df_filtered['end_mhz'] - df_filtered['start_mhz']

st.markdown("---")

if df_filtered.empty:
    st.warning("No allocations match the selected range bounds. Please widen the frequency sliders.")
else:
    # Build timeline Gantt chart using Plotly bar charts.
    # To represent a timeline, we use horizontal bars.
    # The x-axis is frequency, and the base (start) of each bar is `start_mhz`, width is `bandwidth_mhz`.
    
    # We group by Service on the Y axis to keep it readable, and color code by Service.
    fig = go.Figure()
    
    # Generate unique color mappings for services
    unique_services = df_filtered['service'].unique()
    colors = px.colors.qualitative.Alphabet
    color_map = {srv: colors[i % len(colors)] for i, srv in enumerate(unique_services)}
    
    for _, row in df_filtered.iterrows():
        srv = row['service']
        bandwidth = row['bandwidth_mhz']
        start = row['start_mhz']
        
        # Hover info template
        hover_html = (
            f"<b>{row['service']}</b><br>"
            f"Subservice: {row['subservice']}<br>"
            f"Range: {start:.3f} - {row['end_mhz']:.3f} MHz<br>"
            f"Bandwidth: {bandwidth:.3f} MHz<br>"
            f"Region: {row['region']} ({row['country']})<br>"
            f"Description: {row['description']}<br>"
            f"Applications: {row['common_applications']}"
        )
        
        fig.add_trace(go.Bar(
            y=[srv],
            x=[bandwidth],
            base=[start],
            orientation='h',
            marker=dict(
                color=color_map[srv],
                line=dict(color='#2D3748', width=1)
            ),
            hovertext=hover_html,
            hoverinfo="text",
            showlegend=False
        ))
        
    fig.update_layout(
        title=f"Radio Spectrum Allocation Grid ({cust_min:.2f} MHz - {cust_max:.2f} MHz)",
        xaxis_title="Frequency (MHz)",
        yaxis_title="Service Category",
        xaxis=dict(
            range=[cust_min, cust_max],
            side="top",
            gridcolor="#2D3748"
        ),
        yaxis=dict(
            categoryorder="category ascending",
            gridcolor="#2D3748"
        ),
        barmode='overlay',
        height=600,
        margin=dict(t=80, b=40, l=150, r=40)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("💡 Pro-Tip: You can zoom into specific sections directly on the chart by clicking and dragging your mouse over the spectrum bar.")
