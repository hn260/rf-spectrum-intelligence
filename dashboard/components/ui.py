import streamlit as st
import plotly.io as pio
import plotly.graph_objects as go

# Define custom neon/engineering color scheme
THEME_COLORS = {
    "bg_dark": "#0E1117",
    "bg_card": "#1E222B",
    "accent_blue": "#00f0ff", # Cyan
    "accent_green": "#00e676", # Emerald
    "accent_orange": "#ff9100", # Amber
    "accent_purple": "#b388ff", # Neon Purple
    "text_main": "#E2E8F0",
    "text_muted": "#8A99AD",
    "grid_color": "#2D3748"
}

def inject_custom_css():
    """
    Injects custom CSS to style the Streamlit application with a premium,
    modern dark-themed engineering dashboard appearance.
    """
    st.markdown(
        """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
        
        <style>
        /* Base styles */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: #E2E8F0;
        }
        
        /* Monospace for numbers/code */
        .mono-text {
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
        }
        
        /* Custom card styling */
        .rf-card {
            background-color: #1E222B;
            border: 1px solid #2D3748;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
            transition: transform 0.2s, border-color 0.2s;
        }
        .rf-card:hover {
            border-color: #00f0ff;
            transform: translateY(-2px);
        }
        
        /* Metric styling */
        .rf-metric-title {
            font-size: 13px;
            color: #8A99AD;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }
        .rf-metric-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 28px;
            font-weight: 700;
            color: #00f0ff;
            text-shadow: 0 0 8px rgba(0, 240, 255, 0.2);
        }
        .rf-metric-value-green {
            font-family: 'JetBrains Mono', monospace;
            font-size: 28px;
            font-weight: 700;
            color: #00e676;
            text-shadow: 0 0 8px rgba(0, 230, 118, 0.2);
        }
        .rf-metric-desc {
            font-size: 11px;
            color: #8A99AD;
            margin-top: 5px;
        }
        
        /* Custom headers */
        h1, h2, h3 {
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        
        /* Status bar */
        .status-container {
            background-color: #161A22;
            border-bottom: 1px solid #2D3748;
            padding: 8px 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: #8A99AD;
            margin-top: -60px;
            margin-bottom: 25px;
        }
        .status-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 6px;
        }
        .status-active {
            background-color: #00e676;
            box-shadow: 0 0 6px #00e676;
        }
        .status-simulated {
            background-color: #ff9100;
            box-shadow: 0 0 6px #ff9100;
        }
        
        /* Hide default Streamlit decoration */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Adjust page margins for fuller width */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def draw_status_bar(sdr_active: bool = False, db_status: str = "LOADED", active_signals: int = 4):
    """
    Renders an engineering status bar at the top of the dashboard.
    """
    indicator_class = "status-active" if sdr_active else "status-simulated"
    sdr_text = "LIVE RTL-SDR (CONNECTED)" if sdr_active else "SIMULATED SDR RECEIVER"
    
    st.markdown(
        f"""
        <div class="status-container">
            <div>
                <span class="status-indicator {indicator_class}"></span>
                SYSTEM: {sdr_text}
            </div>
            <div>
                DB REGISTRY: <span style="color: #00e676; font-weight: bold;">{db_status}</span> &nbsp;|&nbsp;
                MONITORED CHANNELS: <span style="color: #00f0ff; font-weight: bold;">{active_signals}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def setup_plotly_theme():
    """
    Configures default Plotly theme matching our dark design palette.
    """
    dark_layout = go.Layout(
        paper_bgcolor=THEME_COLORS["bg_dark"],
        plot_bgcolor=THEME_COLORS["bg_dark"],
        font=dict(color=THEME_COLORS["text_main"], family="Inter, sans-serif"),
        xaxis=dict(
            gridcolor=THEME_COLORS["grid_color"],
            linecolor=THEME_COLORS["grid_color"],
            zerolinecolor=THEME_COLORS["grid_color"],
            tickfont=dict(family="JetBrains Mono, monospace")
        ),
        yaxis=dict(
            gridcolor=THEME_COLORS["grid_color"],
            linecolor=THEME_COLORS["grid_color"],
            zerolinecolor=THEME_COLORS["grid_color"],
            tickfont=dict(family="JetBrains Mono, monospace")
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor=THEME_COLORS["grid_color"]
        ),
        margin=dict(t=50, b=50, l=60, r=30)
    )
    pio.templates["rf_dark"] = go.layout.Template(layout=dark_layout)
    pio.templates.default = "rf_dark"

def card_metric(title: str, value: str, desc: str = "", is_green: bool = False):
    """
    Renders a custom HTML/CSS KPI card in Streamlit.
    """
    val_class = "rf-metric-value-green" if is_green else "rf-metric-value"
    st.markdown(
        f"""
        <div class="rf-card">
            <div class="rf-metric-title">{title}</div>
            <div class="{val_class}">{value}</div>
            <div class="rf-metric-desc">{desc}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
