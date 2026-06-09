# 📡 RF Spectrum Intelligence Platform

A professional-grade RF Spectrum Intelligence Platform designed for RF engineers, SDR hobbyists, telecommunications analysts, and researchers to explore, analyze, and visualize radio frequency spectrum usage.

The platform is designed around a modular data architecture to support progressive datasets, beginning with structured frequency allocation registries and offline complex I/Q signal processing, leading into future live RTL-SDR hardware integration and machine learning classifiers.

---

## 🛠️ Project Architecture

The codebase follows a modular structure decoupling core DSP algorithms and data management services from the Streamlit frontend pages:

```
rf-spectrum-intelligence/
├── data/
│   ├── raw/
│   └── processed/
│       ├── spectrum_allocations.csv       # Dataset Layer 1 (Primary Database)
│       └── rf_occupancy_simulated.csv     # Dataset Layer 3 (Telemetry logs)
├── core/
│   ├── services/
│   │   ├── spectrum_service.py            # Layer 1 search, lookup, and filtering
│   │   ├── signal_service.py              # Layer 2 IQ processing (FFT, Spectrogram)
│   │   └── occupancy_service.py           # Layer 3 telemetry, time-frequency analysis
│   └── models/
├── dashboard/
│   ├── app.py                             # Main Dashboard Portal (Landing)
│   ├── components/
│   │   └── ui.py                          # Styles, CSS overrides, and Plotly templates
│   └── pages/
│       ├── 1_Spectrum_Explorer.py        # Keyword Search & Range Filters
│       ├── 2_Interactive_Timeline.py      # 0-6 GHz zoomable Plotly allocations gantt
│       ├── 3_Spectrum_Statistics.py       # Metrics, Treemaps, and Bar Charts
│       ├── 4_Service_Lookup.py           # Combined Frequency & Service resolver
│       ├── 5_Signal_Analyzer.py           # WAV IQ uploads, synthetic generators, FFT, waterfalls
│       ├── 6_Geographic_View.py           # Regional (ITU Region 1/2/3) regulation maps
│       └── 7_RF_Knowledge_Base.py         # Educational handbook & mock waterfall
├── tests/
│   ├── test_spectrum_service.py
│   └── test_signal_service.py
└── requirements.txt                       # App dependencies
```

---

## 💾 Data Architecture Strategy

The platform is built on progressively richer data tiers:
1. **Dataset Layer 1: Spectrum Allocation Database**: Structured CSV maps frequency slices to ITU services, sub-services, and regions from 0 MHz to 6 GHz.
2. **Dataset Layer 2: Signal Recording Repository**: Complex I/Q recordings (and high-fidelity synthetic IQ waveforms) representing FM Broadcasts, ADS-B transponders, AIS maritime beacons, and LoRa CSS sweeps.
3. **Dataset Layer 3: RF Measurement Dataset**: Time-series log containing power measurements (dBm) across critical channels, used to plot temporal waterfall occupancy heatmaps.
4. **Dataset Layer 4: Live SDR Data (Future)**: Real-time complex samples piped from physical RTL-SDR receivers.

---

## ⚙️ Quick Start

### 1. Requirements
* Python 3.10+
* Virtual Environment (configured via `venv`)

### 2. Setup and Installation
Initialize the virtual environment and install the required libraries:
```powershell
# Create venv
python -m venv venv

# Upgrade pip and install packages
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\pip.exe install -r requirements.txt
```

### 3. Running the Dashboard
Start the Streamlit application:
```powershell
.\venv\Scripts\streamlit.exe run dashboard/app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🧪 Testing and Verification
Unit tests are written using `pytest` to verify query filters, lookup indexing, FFT power levels, and peak classifier rules:
```powershell
.\venv\Scripts\pytest.exe tests/
```
