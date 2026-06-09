import streamlit as st
import os
import sys
import numpy as np
import pandas as pd
import wave
import plotly.graph_objects as go
import plotly.express as px

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.services.signal_service import (
    generate_synthetic_iq, 
    compute_fft, 
    compute_spectrogram, 
    detect_peaks, 
    identify_signal
)
from dashboard.components.ui import inject_custom_css, draw_status_bar, setup_plotly_theme

# Initialize settings
st.set_page_config(
    page_title="Signal Analyzer - RF Spectrum Intelligence Platform",
    page_icon="📡",
    layout="wide"
)

inject_custom_css()
# Set active status bar to True if analyzing synthetic/real data
draw_status_bar(sdr_active=True, db_status="LOADED")
setup_plotly_theme()

st.title("📡 Signal Analyzer & Spectrogram Waterfall")
st.markdown("Analyze raw baseband IQ captures. Upload your own file or run the SDR Simulation Generator to examine synthetic signal models.")

# Main Layout
col_ctrl, col_viz = st.columns([1, 2])

# Initialize variables
iq_samples = None
sample_rate_hz = 2.0e6
center_freq_mhz = 100.0

with col_ctrl:
    st.subheader("🛠️ Signal Acquisition Source")
    
    source_type = st.radio(
        "Select Data Source",
        options=["SDR Signal Generator (Simulation)", "Upload Baseband IQ File (.wav)"],
        index=0
    )
    
    if source_type == "SDR Signal Generator (Simulation)":
        st.markdown("**Configure Simulated SDR Scan:**")
        signal_profile = st.selectbox(
            "Signal Waveform Profile",
            options=["FM Broadcast", "ADS-B", "AIS Maritime", "LoRa", "Noise Only"],
            index=0
        )
        
        # Adjust default frequencies based on profile
        default_freq = 98.5
        if signal_profile == "ADS-B":
            default_freq = 1090.0
        elif signal_profile == "AIS Maritime":
            default_freq = 162.0
        elif signal_profile == "LoRa":
            default_freq = 433.92
        elif signal_profile == "Noise Only":
            default_freq = 500.0
            
        center_freq_mhz = st.number_input(
            "SDR Center Frequency (MHz)",
            min_value=1.0,
            max_value=6000.0,
            value=default_freq,
            step=0.1,
            format="%.2f"
        )
        
        sample_rate_msps = st.slider(
            "SDR Sample Rate (MSPS)",
            min_value=0.5,
            max_value=10.0,
            value=2.0,
            step=0.5,
            help="Mega samples per second. Controls capture bandwidth."
        )
        sample_rate_hz = sample_rate_msps * 1e6
        
        duration_s = st.slider(
            "Capture Duration (seconds)",
            min_value=0.1,
            max_value=2.0,
            value=0.5,
            step=0.1
        )
        
        if st.button("🛰️ Capture and Synthesize Signal"):
            with st.spinner("Generating baseband samples..."):
                iq_samples = generate_synthetic_iq(
                    signal_type=signal_profile,
                    center_freq_hz=center_freq_mhz * 1e6,
                    sample_rate_hz=sample_rate_hz,
                    duration_s=duration_s
                )
                st.success("Successfully generated synthetic IQ baseband signal!")
                
    else:
        st.markdown("**Upload a 2-channel WAV file (Left = I, Right = Q):**")
        uploaded_file = st.file_uploader(
            "Choose a WAV file",
            type=["wav"],
            help="Should be a complex IQ WAV recording (Stereo WAV containing real and imaginary components)."
        )
        
        uploaded_center_freq = st.number_input(
            "Recording Center Frequency (MHz)",
            min_value=1.0,
            max_value=6000.0,
            value=100.0,
            step=0.1
        )
        center_freq_mhz = uploaded_center_freq
        
        if uploaded_file is not None:
            try:
                with st.spinner("Parsing WAV file..."):
                    # Parse WAV using wave module
                    wav_rd = wave.open(uploaded_file, 'rb')
                    n_channels = wav_rd.getnchannels()
                    sample_width = wav_rd.getsampwidth()
                    sample_rate_hz = wav_rd.getframerate()
                    n_frames = wav_rd.getnframes()
                    
                    if n_channels != 2:
                        st.error("WAV file must be stereo (left channel = I, right channel = Q).")
                    else:
                        raw_data = wav_rd.readframes(n_frames)
                        wav_rd.close()
                        
                        # Convert raw byte frames to numpy
                        if sample_width == 2:
                            dtype = np.int16
                            div = 32767.0
                        elif sample_width == 1:
                            dtype = np.int8
                            div = 127.0
                        else:
                            dtype = np.int32
                            div = 2147483647.0
                            
                        data_arr = np.frombuffer(raw_data, dtype=dtype)
                        # Stereo is interleaved: L, R, L, R...
                        i_samples = data_arr[0::2] / div
                        q_samples = data_arr[1::2] / div
                        
                        # Pad shorter array if lengths mismatch
                        min_len = min(len(i_samples), len(q_samples))
                        iq_samples = i_samples[:min_len] + 1j * q_samples[:min_len]
                        
                        st.success(f"Loaded {len(iq_samples)} frames at {sample_rate_hz/1e6:.2f} MSPS.")
            except Exception as e:
                st.error(f"Error parsing WAV file: {e}")

    st.markdown("---")
    st.subheader("🔍 Peak Detection Settings")
    threshold_db = st.slider(
        "Peak Threshold (dBFS)",
        min_value=-90,
        max_value=-10,
        value=-50,
        step=1,
        help="Signals higher than this value will trigger peak detection."
    )

with col_viz:
    if iq_samples is None:
        # Generate default noise if nothing captured yet to avoid empty landing
        iq_samples = generate_synthetic_iq("Noise Only", center_freq_mhz * 1e6, sample_rate_hz, 0.2)
        
    st.subheader("📊 Spectrum Analysis Visualizations")
    
    # Compute FFT
    freqs, psd = compute_fft(iq_samples, sample_rate_hz)
    # Convert bins to MHz offsets
    freqs_mhz = freqs / 1e6
    absolute_freqs = center_freq_mhz + freqs_mhz
    
    # Detect peaks
    peaks = detect_peaks(freqs, psd, threshold_db=threshold_db)
    
    # Create Tabs
    tab_fft, tab_waterfall, tab_peaks = st.tabs([
        "📊 Power Spectral Density (FFT)", 
        "🌡️ Spectrogram (Waterfall)", 
        "📝 Peak Detection & Classification"
    ])
    
    with tab_fft:
        # Plot FFT
        fig_fft = go.Figure()
        # Active trace
        fig_fft.add_trace(go.Scatter(
            x=absolute_freqs,
            y=psd,
            mode='lines',
            name='PSD',
            line=dict(color='#00f0ff', width=1.5)
        ))
        # Peak indicators
        if peaks:
            peak_x = [center_freq_mhz + (p['frequency_hz'] / 1e6) for p in peaks]
            peak_y = [p['power_db'] for p in peaks]
            fig_fft.add_trace(go.Scatter(
                x=peak_x,
                y=peak_y,
                mode='markers',
                name='Detected Peaks',
                marker=dict(color='#ff9100', size=8, symbol='triangle-down')
            ))
            
        # Threshold line
        fig_fft.add_shape(
            type="line",
            x0=absolute_freqs[0],
            x1=absolute_freqs[-1],
            y0=threshold_db,
            y1=threshold_db,
            line=dict(color="red", width=1, dash="dash")
        )
        
        fig_fft.update_layout(
            title="SDR Spectrum Analyzer (Power Spectral Density)",
            xaxis_title="Absolute Frequency (MHz)",
            yaxis_title="Power Level (dBFS)",
            xaxis=dict(gridcolor="#2D3748"),
            yaxis=dict(gridcolor="#2D3748", range=[-95, -10]),
            height=420,
            margin=dict(t=50, b=40, l=60, r=30)
        )
        st.plotly_chart(fig_fft, use_container_width=True)
        
    with tab_waterfall:
        # Compute Spectrogram
        spec_data = compute_spectrogram(iq_samples, sample_rate_hz)
        spec_mhz = spec_data['freqs'] / 1e6
        abs_spec_mhz = center_freq_mhz + spec_mhz
        
        # Limit size of waterfall to render fast
        max_rows = 150
        if len(spec_data['times']) > max_rows:
            times = spec_data['times'][:max_rows]
            spec_matrix = spec_data['spectrogram_db'][:max_rows]
        else:
            times = spec_data['times']
            spec_matrix = spec_data['spectrogram_db']
            
        fig_water = go.Figure(data=go.Heatmap(
            z=spec_matrix,
            x=abs_spec_mhz,
            y=times,
            colorscale='Viridis',
            zmin=-90,
            zmax=-20,
            colorbar=dict(title="dBFS")
        ))
        fig_water.update_layout(
            title="Waterfall Display (Spectrogram)",
            xaxis_title="Absolute Frequency (MHz)",
            yaxis_title="Time Elapsed (seconds)",
            height=420,
            margin=dict(t=50, b=40, l=60, r=30)
        )
        st.plotly_chart(fig_water, use_container_width=True)
        
    with tab_peaks:
        st.subheader("🤖 Signal Classifier & Peak Report")
        
        # Classification report
        classification = identify_signal(center_freq_mhz, sample_rate_hz / 1e6, peaks)
        
        # Display classification card
        color = "#00e676" if classification['confidence'] >= 80.0 else "#ff9100"
        st.markdown(
            f"""
            <div style="background-color: #1E222B; border: 2px solid {color}; border-radius: 6px; padding: 20px; margin-bottom: 20px;">
                <h4 style="margin-top:0; color:{color};">Classification Result: {classification['signal_type']}</h4>
                <div style="font-size: 24px; font-weight: bold; font-family: 'JetBrains Mono', monospace; color: #E2E8F0; margin-bottom: 8px;">
                    Confidence Score: {classification['confidence']:.1f}%
                </div>
                <div style="font-size: 14px; color: #8A99AD; line-height: 1.5;">
                    <strong>Details:</strong> {classification['details']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Peak list table
        if not peaks:
            st.info("No active carrier signals detected above the threshold. Lower the Peak Threshold slider to detect weaker signals.")
        else:
            st.markdown("##### Peak Analysis Grid")
            peak_data = []
            for idx, p in enumerate(peaks):
                peak_offset = p['frequency_hz'] / 1e6
                peak_data.append({
                    "Index": idx + 1,
                    "Frequency Offset (MHz)": f"{peak_offset:+.4f} MHz",
                    "Absolute Frequency (MHz)": f"{(center_freq_mhz + peak_offset):.4f} MHz",
                    "Power Level (dBFS)": f"{p['power_db']:.1f} dBFS"
                })
            st.table(pd.DataFrame(peak_data).set_index("Index"))
