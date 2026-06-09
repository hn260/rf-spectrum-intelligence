import streamlit as st
import os
import sys
import pandas as pd
import plotly.express as px

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.services.spectrum_service import load_allocations
from dashboard.components.ui import inject_custom_css, draw_status_bar, setup_plotly_theme

# Initialize settings
st.set_page_config(
    page_title="Geographic Spectrum View - RF Spectrum Intelligence Platform",
    page_icon="🗺️",
    layout="wide"
)

inject_custom_css()
draw_status_bar(sdr_active=False, db_status="LOADED")
setup_plotly_theme()

st.title("🗺️ Geographic Spectrum & Regulatory View")
st.markdown("Examine international spectrum partitions. The International Telecommunication Union (ITU) divides the world into three regulatory regions.")

# Section 1: ITU Regions Map Representation
col_map, col_details = st.columns([3, 2])

with col_map:
    st.subheader("🗺️ Global ITU Regions Reference")
    
    # We can render a mock map using a scatter mapbox or a choropleth, or simple region indicator.
    # A choropleth map of regions looks extremely clean and professional!
    # Let's map countries to ITU Regions
    itu_data = pd.DataFrame([
        {"country_code": "USA", "country_name": "United States", "itu_region": "ITU Region 2", "color_val": 2},
        {"country_code": "CAN", "country_name": "Canada", "itu_region": "ITU Region 2", "color_val": 2},
        {"country_code": "BRA", "country_name": "Brazil", "itu_region": "ITU Region 2", "color_val": 2},
        {"country_code": "FRA", "country_name": "France", "itu_region": "ITU Region 1", "color_val": 1},
        {"country_code": "DEU", "country_name": "Germany", "itu_region": "ITU Region 1", "color_val": 1},
        {"country_code": "GBR", "country_name": "United Kingdom", "itu_region": "ITU Region 1", "color_val": 1},
        {"country_code": "ZAF", "country_name": "South Africa", "itu_region": "ITU Region 1", "color_val": 1},
        {"country_code": "RUS", "country_name": "Russia", "itu_region": "ITU Region 1", "color_val": 1},
        {"country_code": "IND", "country_name": "India", "itu_region": "ITU Region 3", "color_val": 3},
        {"country_code": "CHN", "country_name": "China", "itu_region": "ITU Region 3", "color_val": 3},
        {"country_code": "AUS", "country_name": "Australia", "itu_region": "ITU Region 3", "color_val": 3},
        {"country_code": "JPN", "country_name": "Japan", "itu_region": "ITU Region 3", "color_val": 3}
    ])
    
    fig_map = px.choropleth(
        itu_data,
        locations="country_code",
        color="itu_region",
        hover_name="country_name",
        color_discrete_map={
            "ITU Region 1": "#b388ff",
            "ITU Region 2": "#00f0ff",
            "ITU Region 3": "#00e676"
        },
        title="Sample Regulatory Divisions (Region 1, 2, and 3)"
    )
    fig_map.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular',
            bgcolor="#0E1117"
        ),
        height=320,
        margin=dict(t=30, b=0, l=0, r=0)
    )
    st.plotly_chart(fig_map, use_container_width=True)

with col_details:
    st.subheader("📚 Regional Glossary")
    st.markdown(
        """
        * **ITU Region 1**: Includes Europe, Africa, the Middle East, Northern Asia, and the former Soviet Union states.
        * **ITU Region 2**: Comprises the Americas (North and South America), Greenland, and some Pacific islands.
        * **ITU Region 3**: Spans Southern Asia (including India), China, Japan, Australia, New Zealand, and the remaining Pacific territories.
        
        **Note:** Frequencies allocated to services can differ between regions to prevent interference and support local infrastructure standards.
        """
    )

st.markdown("---")

# Section 2: Interactive Allocation Differences Selector
st.subheader("🔍 Regional Frequency Comparison Matrix")
st.markdown("Compare how a single service or protocol (like LoRa IoT, Cellular, or Amateur radio) is configured across geographical zones.")

service_selection = st.selectbox(
    "Select Service Category to Compare",
    options=["ISM / Short Range (LoRa / RFID)", "Mobile Cellular Networks", "Amateur Radio Bands"]
)

df = load_allocations()

if "ISM" in service_selection:
    st.markdown("##### 📶 Short Range Device (SRD) / LoRa Comparison")
    st.markdown(
        "Short-range devices operate in license-exempt bands. However, the exact frequencies allowed vary heavily to fit within local military and public safety spectrums:"
    )
    
    # Filter bands representing ISM short range
    srd_df = df[df['service'].str.contains("ISM / Short Range", na=False)]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
            <div style="background-color: #1A1D24; padding: 15px; border-top: 4px solid #b388ff; border-radius: 4px; height: 180px;">
                <strong style="color: #b388ff;">Europe & Middle East (Region 1)</strong><br>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 18px; color: #E2E8F0;">863 - 870 MHz</span><br>
                <span style="font-size: 12px; color: #8A99AD;">(LoRa Band: EU868)</span><br><br>
                <p style="font-size: 12px; margin: 0; line-height: 1.4;">Used for smart utility grids, home automation, and RFID trackers. Duty cycle limits apply.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            """
            <div style="background-color: #1A1D24; padding: 15px; border-top: 4px solid #00f0ff; border-radius: 4px; height: 180px;">
                <strong style="color: #00f0ff;">The Americas (Region 2)</strong><br>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 18px; color: #E2E8F0;">902 - 928 MHz</span><br>
                <span style="font-size: 12px; color: #8A99AD;">(LoRa Band: US915)</span><br><br>
                <p style="font-size: 12px; margin: 0; line-height: 1.4;">Wider bandwidth (26 MHz). Allows higher transmit power levels compared to European allocations.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            """
            <div style="background-color: #1A1D24; padding: 15px; border-top: 4px solid #00e676; border-radius: 4px; height: 180px;">
                <strong style="color: #00e676;">India (Region 3 subset)</strong><br>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 18px; color: #E2E8F0;">865 - 867 MHz</span><br>
                <span style="font-size: 12px; color: #8A99AD;">(LoRa Band: IN865)</span><br><br>
                <p style="font-size: 12px; margin: 0; line-height: 1.4;">De-licensed band by WPC for short-range wireless devices, fitting between cellular GSM blocks.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    st.markdown("#### Database Registry Details:")
    st.dataframe(srd_df[['start_mhz', 'end_mhz', 'subservice', 'region', 'country', 'common_applications']], hide_index=True, use_container_width=True)

elif "Cellular" in service_selection:
    st.markdown("##### 📱 Mobile Broadband and Cellular Downlinks/Uplinks")
    st.markdown(
        "Commercial cellular networks rely on specific LTE/5G bands. These bands are split into uplinks (handset to tower) and downlinks (tower to handset):"
    )
    
    cell_df = df[df['service'].str.contains("Cellular|Mobile", na=False)]
    st.dataframe(cell_df[['start_mhz', 'end_mhz', 'service', 'subservice', 'region', 'country', 'description']], hide_index=True, use_container_width=True)

else:
    st.markdown("##### 📻 Amateur Radio Allocations")
    st.markdown(
        "Amateur Radio Operators (Hams) are allocated specific bands throughout the spectrum. While HF bands are mostly global, VHF/UHF amateur frequencies vary:"
    )
    
    ham_df = df[df['service'].str.contains("Amateur", na=False)]
    st.dataframe(ham_df[['start_mhz', 'end_mhz', 'subservice', 'region', 'country', 'allocation_type', 'common_applications']], hide_index=True, use_container_width=True)
