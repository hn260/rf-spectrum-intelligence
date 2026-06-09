import streamlit as st
import os
import sys
import pandas as pd
import plotly.express as px

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.services.spectrum_service import get_statistics, load_allocations
from dashboard.components.ui import inject_custom_css, draw_status_bar, setup_plotly_theme

# Initialize settings
st.set_page_config(
    page_title="Spectrum Statistics - RF Spectrum Intelligence Platform",
    page_icon="📊",
    layout="wide"
)

inject_custom_css()
draw_status_bar(sdr_active=False, db_status="LOADED")
setup_plotly_theme()

st.title("📊 Spectrum Statistics & Analytics")
st.markdown("Quantitative distribution analysis of registered frequency bands and bandwidth utilization.")

# Fetch statistics
stats = get_statistics()
df = load_allocations()
df['bandwidth_mhz'] = df['end_mhz'] - df['start_mhz']

# Section 1: Chart Grid
col1, col2 = st.columns(2)

with col1:
    st.subheader("🥧 Allocation Count by Service Type")
    # Convert service counts dictionary to dataframe
    df_counts = pd.DataFrame(
        list(stats['service_counts'].items()), 
        columns=['Service', 'Count']
    )
    
    fig_pie = px.pie(
        df_counts,
        values='Count',
        names='Service',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_pie.update_layout(height=400, margin=dict(t=40, b=40, l=40, r=40))
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("📶 Allocated Bandwidth by Service Type (MHz)")
    df_bw = pd.DataFrame(
        list(stats['service_bandwidths'].items()), 
        columns=['Service', 'Total Bandwidth (MHz)']
    ).sort_values(by='Total Bandwidth (MHz)', ascending=False)
    
    fig_bar = px.bar(
        df_bw,
        x='Total Bandwidth (MHz)',
        y='Service',
        orientation='h',
        color='Total Bandwidth (MHz)',
        color_continuous_scale='Turbo'
    )
    fig_bar.update_layout(height=400, margin=dict(t=40, b=40, l=40, r=40))
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# Section 2: Treemap & Largest Bands
col3, col4 = st.columns([3, 2])

with col3:
    st.subheader("🌳 Hierarchy of Spectrum Allocations")
    st.markdown("Nested view of allocations grouped by Service and Subservice category. Larger boxes represent wider total frequency blocks.")
    
    fig_tree = px.treemap(
        df,
        path=['service', 'subservice'],
        values='bandwidth_mhz',
        color='bandwidth_mhz',
        color_continuous_scale='Viridis',
        labels={'bandwidth_mhz': 'Total Bandwidth (MHz)'}
    )
    fig_tree.update_layout(height=450, margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig_tree, use_container_width=True)

with col4:
    st.subheader("🏔️ Largest Contiguous Frequency Bands")
    st.markdown("The 5 single largest uninterrupted spectrum allocations inside the database registry.")
    
    for idx, band in enumerate(stats['largest_bands']):
        st.markdown(
            f"""
            <div style="background-color: #1A1D24; border: 1px solid #2D3748; border-radius: 6px; padding: 14px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; font-weight: bold; margin-bottom: 5px;">
                    <span style="color: #00f0ff; font-family: 'JetBrains Mono', monospace; font-size: 15px;">
                        #{idx+1} &nbsp;{band['start_mhz']:.1f} - {band['end_mhz']:.1f} MHz
                    </span>
                    <span style="color: #ff9100; font-family: 'JetBrains Mono', monospace; font-size: 14px;">
                        {band['bandwidth']:.1f} MHz
                    </span>
                </div>
                <div style="font-size: 13px; color: #E2E8F0; font-weight: 600;">
                    {band['service']} &middot; <span style="font-weight: normal; color: #8A99AD;">{band['subservice']}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
