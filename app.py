import streamlit as st
import pandas as pd
import json
import html

from src.orchestrator import SecureOperationsOrchestrator
from src.tools import get_airport_metrics
from src.config import BASE_DIR


# ============================================================
# CONFIGURATION
# ============================================================

AUDIT_LOG_PATH = BASE_DIR / "output" / "distilled_training_data.jsonl"

st.set_page_config(
    page_title="Uber SkyOps — AI Command Center",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# STREAMLIT VERSION CHECK
# ============================================================

if not hasattr(st, "html"):
    st.error(
        "Your Streamlit version does not support st.html(). "
        "Please upgrade Streamlit using: pip install -U streamlit"
    )
    st.stop()


# ============================================================
# HELPER
# ============================================================

def ui_html(content):
    """
    Render custom HTML directly using Streamlit's HTML renderer.

    IMPORTANT:
    Do not replace this with st.markdown().
    """

    st.html(content)


# ============================================================
# GLOBAL CSS
# ============================================================

ui_html("""
<style>

@import url(
    'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800'
    '&family=JetBrains+Mono:wght@400;500&display=swap'
);


/* ==========================================================
   GLOBAL
   ========================================================== */

html,
body,
[class*="css"] {

    font-family: 'Inter', sans-serif !important;

}

.stApp {

    background: #000000 !important;

    color: #FFFFFF !important;

}

.main {

    background: #000000 !important;

}

.block-container {

    max-width: 1700px !important;

    padding-top: 1.5rem !important;
    padding-bottom: 4rem !important;

    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;

}


/* ==========================================================
   HIDE DEFAULT STREAMLIT CHROME & PREVENT COLLAPSE TOGGLE
   ========================================================== */

#MainMenu {

    visibility: hidden;

}

header {

    visibility: hidden;

}

footer {

    visibility: hidden;

}

/* Hide collapse sidebar button */
button[kind="header"] {
    display: none !important;
}

[data-testid="stSidebarCollapseButton"] {
    display: none !important;
}

[data-testid="stSidebarUserContent"] {
    padding-top: 0rem !important;
}


/* ==========================================================
   SIDEBAR (PERMANENTLY VISIBLE & FIXED WIDTH)
   ========================================================== */

section[data-testid="stSidebar"] {

    background: #050505 !important;

    border-right: 1px solid #202020 !important;

    transform: none !important;

    width: 320px !important;

    min-width: 320px !important;

    visibility: visible !important;

}

section[data-testid="stSidebar"] > div {

    padding-top: 0rem !important;

    padding-left: 1.25rem !important;

    padding-right: 1.25rem !important;

    padding-bottom: 1.5rem !important;

}


/* Sidebar labels */

section[data-testid="stSidebar"] label {

    color: #777777 !important;

    font-size: 10px !important;

    font-weight: 600 !important;

    text-transform: uppercase !important;

    letter-spacing: 0.12em !important;

}


/* Sidebar select */

div[data-baseweb="select"] > div {

    background: #0A0A0A !important;

    border: 1px solid #292929 !important;

    border-radius: 6px !important;

    color: #FFFFFF !important;

}

div[data-baseweb="select"] span {

    color: #FFFFFF !important;

}


/* Dropdown menu */

div[data-baseweb="popover"] {

    background: #0A0A0A !important;

}

div[data-baseweb="menu"] {

    background: #0A0A0A !important;

}

div[data-baseweb="menu"] li {

    background: #0A0A0A !important;

    color: #FFFFFF !important;

}

div[data-baseweb="menu"] li:hover {

    background: #1A1A1A !important;

}


/* ==========================================================
   SIDEBAR SLIDER
   ========================================================== */

div[data-testid="stSlider"] {

    padding-top: 5px;

}

div[data-testid="stSlider"] [data-baseweb="slider"] {

    color: #FFFFFF !important;

}

div[data-testid="stSlider"] [role="slider"] {

    background: #FFFFFF !important;

    border-color: #FFFFFF !important;

}


/* ==========================================================
   SIDEBAR RADIO
   ========================================================== */

div[data-testid="stRadio"] label {

    text-transform: none !important;

    letter-spacing: 0 !important;

    font-size: 12px !important;

    color: #C4C4C4 !important;

}


/* Radio circle */

div[data-testid="stRadio"] div[role="radiogroup"] label
div {

    color: #FFFFFF !important;

}


/* ==========================================================
   BRAND (FLUSH TOP ALIGNED)
   ========================================================== */

.brand-wrapper {

    margin-top: -2.5rem !important;

    padding-top: 0.5rem !important;

    margin-bottom: 24px !important;

}

.brand {

    display: flex;

    align-items: center;

    gap: 12px;

}

.brand-icon {

    width: 38px;

    height: 38px;

    display: flex;

    align-items: center;

    justify-content: center;

    background: #FFFFFF;

    color: #000000;

    border-radius: 7px;

    font-size: 19px;

}

.brand-name {

    color: #FFFFFF;

    font-size: 14px;

    font-weight: 800;

    letter-spacing: 0.05em;

    line-height: 1.1;

}

.brand-subtitle {

    color: #666666;

    font-size: 9px;

    text-transform: uppercase;

    letter-spacing: 0.14em;

    margin-top: 2px;

}


/* ==========================================================
   SIDEBAR SECTIONS
   ========================================================== */

.sidebar-section-title {

    color: #FFFFFF;

    font-size: 12px;

    font-weight: 600;

    margin-bottom: 16px;

}

.sidebar-divider {

    height: 1px;

    background: #202020;

    margin-top: 20px;

    margin-bottom: 22px;

}

.sidebar-caption {

    color: #666666;

    font-size: 9px;

    font-weight: 600;

    text-transform: uppercase;

    letter-spacing: 0.13em;

    margin-bottom: 12px;

}


/* ==========================================================
   SIDEBAR SYSTEM STATUS
   ========================================================== */

.system-status {

    position: fixed;

    bottom: 22px;

    left: 25px;

    font-family: 'JetBrains Mono', monospace;

    font-size: 9px;

    color: #555555;

    line-height: 1.8;

}

.system-dot {

    color: #FFFFFF;

}


/* ==========================================================
   TOP HEADER
   ========================================================== */

.top-header {

    display: flex;

    justify-content: space-between;

    align-items: flex-start;

    padding-bottom: 28px;

    margin-bottom: 28px;

    border-bottom: 1px solid #202020;

}

.page-kicker {

    color: #666666;

    font-size: 9px;

    font-weight: 600;

    text-transform: uppercase;

    letter-spacing: 0.18em;

    margin-bottom: 9px;

}

.page-title {

    color: #FFFFFF;

    font-size: 38px;

    font-weight: 700;

    letter-spacing: -1.7px;

    line-height: 1;

}

.page-description {

    color: #777777;

    font-size: 11px;

    margin-top: 10px;

}

.airport-status {

    text-align: right;

}

.airport-code {

    color: #FFFFFF;

    font-size: 25px;

    font-weight: 700;

}

.airport-name {

    color: #666666;

    font-size: 10px;

    margin-top: 2px;

}

.live-status {

    display: inline-flex;

    align-items: center;

    gap: 6px;

    margin-top: 9px;

    padding: 5px 9px;

    border: 1px solid #292929;

    border-radius: 20px;

    color: #888888;

    font-size: 8px;

    font-weight: 600;

    letter-spacing: 0.08em;

}

.live-dot {

    width: 6px;

    height: 6px;

    background: #FFFFFF;

    border-radius: 50%;

}


/* ==========================================================
   SECTION HEADER
   ========================================================== */

.section-header {

    display: flex;

    align-items: center;

    gap: 10px;

    margin-bottom: 13px;

}

.section-title {

    color: #E5E5E5;

    font-size: 13px;

    font-weight: 600;

}

.section-line {

    height: 1px;

    background: #202020;

    flex: 1;

}

.section-meta {

    color: #555555;

    font-family: 'JetBrains Mono', monospace;

    font-size: 8px;

}


/* ==========================================================
   METRIC CARDS
   ========================================================== */

.metric-card {

    background: #080808;

    border: 1px solid #242424;

    border-radius: 8px;

    padding: 18px;

    min-height: 130px;

    transition: all 0.2s ease;

}

.metric-card:hover {

    background: #0C0C0C;

    border-color: #444444;

    transform: translateY(-2px);

}

.metric-top {

    display: flex;

    align-items: center;

    justify-content: space-between;

}

.metric-label {

    color: #686868;

    font-size: 9px;

    font-weight: 600;

    text-transform: uppercase;

    letter-spacing: 0.1em;

}

.metric-icon {

    color: #555555;

    font-size: 15px;

}

.metric-value {

    color: #F5F5F5;

    font-size: 29px;

    font-weight: 700;

    letter-spacing: -1px;

    margin-top: 16px;

}

.metric-unit {

    color: #666666;

    font-size: 12px;

    font-weight: 500;

}

.metric-footer {

    color: #777777;

    font-size: 9px;

    margin-top: 7px;

}

.normal {

    color: #AFAFAF;

}

.alert {

    color: #FFFFFF;

    font-weight: 700;

}

.warning {

    color: #999999;

}


/* ==========================================================
   PANELS
   ========================================================== */

.panel {

    background: #070707;

    border: 1px solid #242424;

    border-radius: 8px;

    padding: 20px;

}

.panel-title {

    color: #D4D4D4;

    font-size: 11px;

    font-weight: 600;

    letter-spacing: 0.04em;

    padding-bottom: 15px;

    margin-bottom: 20px;

    border-bottom: 1px solid #202020;

}


/* ==========================================================
   COMMAND AREA
   ========================================================== */

.command-heading {

    color: #FFFFFF;

    font-size: 17px;

    font-weight: 600;

    margin-bottom: 5px;

}

.command-description {

    color: #666666;

    font-size: 10px;

    line-height: 1.6;

    margin-bottom: 13px;

}


/* ==========================================================
   TEXT INPUT
   ========================================================== */

div[data-testid="stTextInput"] input {

    background: #080808 !important;

    color: #FFFFFF !important;

    border: 1px solid #303030 !important;

    border-radius: 6px !important;

    height: 44px !important;

    font-family: 'Inter', sans-serif !important;

    font-size: 11px !important;

}

div[data-testid="stTextInput"] input::placeholder {

    color: #555555 !important;

}

div[data-testid="stTextInput"] input:focus {

    border-color: #777777 !important;

    box-shadow: none !important;

}


/* ==========================================================
   BUTTONS
   ========================================================== */

.stButton > button {

    background: #FFFFFF !important;

    color: #000000 !important;

    border: none !important;

    border-radius: 6px !important;

    height: 44px !important;

    font-size: 10px !important;

    font-weight: 700 !important;

    letter-spacing: 0.04em !important;

}

.stButton > button:hover {

    background: #D4D4D4 !important;

    color: #000000 !important;

}

.stButton > button:active {

    transform: scale(0.985);

}


/* ==========================================================
   PIPELINE
   ========================================================== */

.pipeline {

    display: flex;

    align-items: stretch;

    margin-top: 20px;

    margin-bottom: 24px;

}

.agent {

    flex: 1;

    background: #090909;

    border: 1px solid #242424;

    border-radius: 6px;

    padding: 13px;

}

.agent-number {

    width: 23px;

    height: 23px;

    display: flex;

    align-items: center;

    justify-content: center;

    background: #FFFFFF;

    color: #000000;

    border-radius: 50%;

    font-size: 9px;

    font-weight: 700;

}

.agent-name {

    color: #D4D4D4;

    font-size: 10px;

    font-weight: 600;

    margin-top: 9px;

}

.agent-description {

    color: #5F5F5F;

    font-size: 8px;

    line-height: 1.5;

    margin-top: 4px;

}

.pipeline-arrow {

    display: flex;

    align-items: center;

    justify-content: center;

    width: 32px;

    color: #444444;

    font-size: 15px;

}


/* ==========================================================
   GOVERNANCE
   ========================================================== */

.governance-grid {

    display: grid;

    grid-template-columns: 1fr 1fr;

    gap: 8px;

    margin-bottom: 22px;

}

.gov-item {

    background: #090909;

    border: 1px solid #202020;

    border-radius: 6px;

    padding: 13px;

}

.gov-label {

    color: #5F5F5F;

    font-size: 8px;

    text-transform: uppercase;

    letter-spacing: 0.1em;

}

.gov-value {

    color: #D4D4D4;

    font-family: 'JetBrains Mono', monospace;

    font-size: 10px;

    margin-top: 7px;

}


/* ==========================================================
   BADGES
   ========================================================== */

.badge {

    display: inline-block;

    padding: 4px 8px;

    border-radius: 4px;

    font-family: 'JetBrains Mono', monospace;

    font-size: 8px;

}

.badge-green {

    color: #E5E5E5;

    background: #111111;

    border: 1px solid #444444;

}

.badge-red {

    color: #FFFFFF;

    background: #1A1A1A;

    border: 1px solid #666666;

}

.badge-yellow {

    color: #BDBDBD;

    background: #0F0F0F;

    border: 1px solid #333333;

}


/* ==========================================================
   EXPANDERS
   ========================================================== */

div[data-testid="stExpander"] {

    background: #090909 !important;

    border: 1px solid #222222 !important;

    border-radius: 6px !important;

    margin-bottom: 7px !important;

}

div[data-testid="stExpander"] summary {

    color: #D4D4D4 !important;

    font-size: 10px !important;

}

div[data-testid="stExpander"] summary:hover {

    color: #FFFFFF !important;

}


/* Expander content */

div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {

    background: #050505 !important;

}


/* ==========================================================
   JSON / CODE
   ========================================================== */

.json-box {

    background: #030303;

    border: 1px solid #242424;

    border-radius: 6px;

    padding: 14px;

    overflow-x: auto;

}

.json-box pre {

    color: #999999;

    font-family: 'JetBrains Mono', monospace;

    font-size: 8px;

    line-height: 1.7;

    margin: 0;

    white-space: pre-wrap;

    word-break: break-word;

}


/* ==========================================================
   AUDIT TABLE
   ========================================================== */

.audit-table {

    width: 100%;

    border-collapse: collapse;

    font-size: 9px;

}

.audit-table th {

    color: #555555;

    text-align: left;

    padding: 9px;

    border-bottom: 1px solid #292929;

    text-transform: uppercase;

    letter-spacing: 0.07em;

}

.audit-table td {

    color: #999999;

    padding: 10px 9px;

    border-bottom: 1px solid #181818;

}

.audit-table tr:hover td {

    background: #0D0D0D;

}


/* ==========================================================
   ERROR / INFO
   ========================================================== */

div[data-testid="stAlert"] {

    background: #090909 !important;

    border: 1px solid #292929 !important;

    color: #BBBBBB !important;

}


/* ==========================================================
   MARKDOWN TEXT
   ========================================================== */

.stMarkdown {

    color: #BBBBBB !important;

}

.stMarkdown p {

    color: #BBBBBB !important;

    font-size: 10px !important;

}


/* ==========================================================
   MOBILE
   ========================================================== */

@media(max-width: 900px) {

    .block-container {

        padding-left: 1rem !important;

        padding-right: 1rem !important;

    }

    .top-header {

        flex-direction: column;

        gap: 20px;

    }

    .airport-status {

        text-align: left;

    }

    .page-title {

        font-size: 28px;

    }

    .pipeline {

        flex-direction: column;

    }

    .pipeline-arrow {

        width: 100%;

        height: 25px;

        transform: rotate(90deg);

    }

    .governance-grid {

        grid-template-columns: 1fr;

    }

}

</style>
""")


# ============================================================
# SESSION STATE
# ============================================================

if "orchestrator" not in st.session_state:

    st.session_state.orchestrator = (
        SecureOperationsOrchestrator()
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # BRAND
    # --------------------------------------------------------

    ui_html("""
    <div class="brand-wrapper">

        <div class="brand">

            <div class="brand-icon">
                ✈
            </div>

            <div>

                <div class="brand-name">
                    UBER SKYOPS
                </div>

                <div class="brand-subtitle">
                    AI Operations
                </div>

            </div>

        </div>

    </div>
    """)


    # --------------------------------------------------------
    # OPERATIONS CONTROL
    # --------------------------------------------------------

    ui_html("""
    <div class="sidebar-section-title">
        Operations Control
    </div>
    """)


    selected_airport = st.selectbox(
        "Target Airport",
        [
            "SFO",
            "LAX",
            "JFK"
        ]
    )


    proposed_surge = st.slider(
        "Surge Target",
        1.0,
        2.5,
        1.4,
        0.1
    )


    # --------------------------------------------------------
    # HUMAN-IN-THE-LOOP
    # --------------------------------------------------------

    ui_html("""
    <div class="sidebar-divider"></div>

    <div class="sidebar-caption">
        Human-in-the-Loop
    </div>
    """)


    human_approval = st.radio(
        "Manager Authorization",
        [
            "Authorize High-Risk Actions",
            "Reject High-Risk Actions"
        ],
        label_visibility="visible"
    )


    is_approved = (
        "Authorize" in human_approval
    )


    # --------------------------------------------------------
    # SYSTEM STATUS
    # --------------------------------------------------------

    ui_html("""
    <div class="system-status">

        <span class="system-dot">●</span>
        SYSTEM ONLINE

        <br>

        LAST SYNC: LIVE

    </div>
    """)


# ============================================================
# AIRPORT NAMES
# ============================================================

airport_names = {

    "SFO":
        "San Francisco International",

    "LAX":
        "Los Angeles International",

    "JFK":
        "John F. Kennedy International"

}


# ============================================================
# SAFE DYNAMIC VALUES
# ============================================================

safe_airport = html.escape(
    str(selected_airport)
)

safe_airport_name = html.escape(
    airport_names[selected_airport]
)


# ============================================================
# TOP HEADER
# ============================================================

ui_html(f"""
<div class="top-header">

    <div>

        <div class="page-kicker">
            Airport Operations / Autonomous Control
        </div>

        <div class="page-title">
            AI Command Center
        </div>

        <div class="page-description">
            Multi-Agent Investigation
            &nbsp;&nbsp;·&nbsp;&nbsp;
            RAG Governance
            &nbsp;&nbsp;·&nbsp;&nbsp;
            Safety Guardrails
        </div>

    </div>


    <div class="airport-status">

        <div class="airport-code">
            {safe_airport}
        </div>

        <div class="airport-name">
            {safe_airport_name}
        </div>

        <div class="live-status">

            <span class="live-dot"></span>

            LIVE TELEMETRY

        </div>

    </div>

</div>
""")


# ============================================================
# GET TELEMETRY
# ============================================================

metrics = get_airport_metrics(
    selected_airport
)


# ============================================================
# TELEMETRY HEADER
# ============================================================

ui_html("""
<div class="section-header">

    <div class="section-title">
        Real-Time Operational Telemetry
    </div>

    <div class="section-line"></div>

    <div class="section-meta">
        LIVE DATA
    </div>

</div>
""")


# ============================================================
# TELEMETRY CARDS
# ============================================================

if "error" not in metrics:

    comp_rate = (
        metrics.get(
            "completion_rate",
            0
        ) * 100
    )

    canc_rate = (
        metrics.get(
            "driver_cancellation_rate",
            0
        ) * 100
    )


    # --------------------------------------------------------
    # Completion status
    # --------------------------------------------------------

    if comp_rate < 85:

        comp_class = "alert"
        comp_text = "↓ BELOW THRESHOLD"

    else:

        comp_class = "normal"
        comp_text = "↑ TARGET MET"


    # --------------------------------------------------------
    # Cancellation status
    # --------------------------------------------------------

    if canc_rate > 15:

        canc_class = "alert"
        canc_text = "↑ ELEVATED LEVEL"

    else:

        canc_class = "normal"
        canc_text = "↓ NORMAL LEVEL"


    c1, c2, c3, c4 = st.columns(4)


    # ========================================================
    # COMPLETION
    # ========================================================

    with c1:

        ui_html(f"""
        <div class="metric-card">

            <div class="metric-top">

                <div class="metric-label">
                    Completion Rate
                </div>

                <div class="metric-icon">
                    ◉
                </div>

            </div>

            <div class="metric-value">
                {comp_rate:.1f}%
            </div>

            <div class="metric-footer {comp_class}">
                {comp_text}
            </div>

        </div>
        """)


    # ========================================================
    # CANCELLATION
    # ========================================================

    with c2:

        ui_html(f"""
        <div class="metric-card">

            <div class="metric-top">

                <div class="metric-label">
                    Driver Cancellation
                </div>

                <div class="metric-icon">
                    ◉
                </div>

            </div>

            <div class="metric-value">
                {canc_rate:.1f}%
            </div>

            <div class="metric-footer {canc_class}">
                {canc_text}
            </div>

        </div>
        """)


    # ========================================================
    # ETA
    # ========================================================

    with c3:

        average_eta = html.escape(
            str(
                metrics.get(
                    "average_eta",
                    "N/A"
                )
            )
        )

        ui_html(f"""
        <div class="metric-card">

            <div class="metric-top">

                <div class="metric-label">
                    Average ETA
                </div>

                <div class="metric-icon">
                    ◷
                </div>

            </div>

            <div class="metric-value">

                {average_eta}

                <span class="metric-unit">
                    min
                </span>

            </div>

            <div class="metric-footer normal">
                ● STAGING QUEUE ACTIVE
            </div>

        </div>
        """)


    # ========================================================
    # SURGE
    # ========================================================

    with c4:

        surge_multiplier = html.escape(
            str(
                metrics.get(
                    "surge_multiplier",
                    "N/A"
                )
            )
        )

        queue_size = html.escape(
            str(
                metrics.get(
                    "queue_size",
                    "N/A"
                )
            )
        )

        ui_html(f"""
        <div class="metric-card">

            <div class="metric-top">

                <div class="metric-label">
                    Surge / Queue Volume
                </div>

                <div class="metric-icon">
                    ▣
                </div>

            </div>

            <div class="metric-value">

                {surge_multiplier}x

            </div>

            <div class="metric-footer normal">

                ● {queue_size} VEHICLES STAGED

            </div>

        </div>
        """)

else:

    st.error(
        metrics["error"]
    )


# ============================================================
# SPACING
# ============================================================

ui_html("""
<div style="height:30px;"></div>
""")


# ============================================================
# MAIN TWO-COLUMN LAYOUT
# ============================================================

left_column, right_column = st.columns(
    [1.65, 1],
    gap="large"
)


# ============================================================
# LEFT — COPILOT
# ============================================================

with left_column:

    # --------------------------------------------------------
    # COPILOT HEADER
    # --------------------------------------------------------

    ui_html("""
    <div class="panel">

        <div class="panel-title">
            ◈ &nbsp; MULTI-AGENT EXECUTION PIPELINE
        </div>

        <div class="command-heading">
            Execute Copilot Workflow
        </div>

        <div class="command-description">
            Investigate operational state, retrieve policy context,
            evaluate risk, and generate a controlled resolution.
        </div>

    </div>
    """)


    # --------------------------------------------------------
    # QUERY
    # --------------------------------------------------------

    user_query = st.text_input(
        "Operational Query",
        value=(
            f"Investigate operational status "
            f"and surge rules for {selected_airport}."
        ),
        label_visibility="collapsed"
    )


    # --------------------------------------------------------
    # EXECUTE
    # --------------------------------------------------------

    if st.button(
        "RUN MULTI-AGENT COPILOT   →",
        type="primary",
        use_container_width=True
    ):

        with st.spinner(
            "Executing agent pipeline..."
        ):

            result = (
                st.session_state
                .orchestrator
                .process_query_with_safety(
                    user_query=user_query,
                    target_proposed_surge=proposed_surge,
                    human_decision=is_approved
                )
            )


        # ====================================================
        # BLOCKED
        # ====================================================

        if "error" in result:

            safe_error = html.escape(
                str(
                    result["error"]
                )
            )

            ui_html(f"""
            <div style="
                margin-top:16px;
                padding:16px;
                border:1px solid #666666;
                background:#0A0A0A;
                border-radius:6px;
                color:#FFFFFF;
                font-family:'JetBrains Mono',monospace;
                font-size:9px;
            ">

                POLICY GUARDRAIL BLOCKED

                <br><br>

                {safe_error}

            </div>
            """)


        # ====================================================
        # SUCCESS
        # ====================================================

        else:

            # ------------------------------------------------
            # GOVERNANCE HEADER
            # ------------------------------------------------

            ui_html("""
            <div style="height:24px;"></div>

            <div class="section-header">

                <div class="section-title">
                    Governance & Approval
                </div>

                <div class="section-line"></div>

            </div>
            """)


            # ------------------------------------------------
            # STATUS
            # ------------------------------------------------

            status = (
                result[
                    "hitl_approval"
                ][
                    "status"
                ]
            )


            if (
                "APPROVED" in status
                or
                "AUTO" in status
            ):

                status_class = "badge-green"

            else:

                status_class = "badge-red"


            # ------------------------------------------------
            # SAFE VALUES
            # ------------------------------------------------

            safe_risk = html.escape(
                str(
                    result.get(
                        "risk_level",
                        "UNKNOWN"
                    )
                )
            )

            safe_guardrail = html.escape(
                str(
                    result.get(
                        "policy_guardrail",
                        "UNKNOWN"
                    )
                )
            )

            safe_status = html.escape(
                str(status)
            )


            # ------------------------------------------------
            # GOVERNANCE GRID
            # ------------------------------------------------

            ui_html(f"""
            <div class="governance-grid">

                <div class="gov-item">

                    <div class="gov-label">
                        Risk Classification
                    </div>

                    <div class="gov-value">
                        {safe_risk}
                    </div>

                </div>


                <div class="gov-item">

                    <div class="gov-label">
                        Guardrail Verification
                    </div>

                    <div class="gov-value">
                        {safe_guardrail}
                    </div>

                </div>


                <div class="gov-item">

                    <div class="gov-label">
                        Human Approval Gate
                    </div>

                    <div class="gov-value">

                        <span class="badge {status_class}">
                            {safe_status}
                        </span>

                    </div>

                </div>


                <div class="gov-item">

                    <div class="gov-label">
                        Proposed Surge
                    </div>

                    <div class="gov-value">
                        {proposed_surge:.1f}x
                    </div>

                </div>

            </div>
            """)


            # =================================================
            # AGENT PIPELINE
            # =================================================

            ui_html("""
            <div class="pipeline">

                <div class="agent">

                    <div class="agent-number">
                        1
                    </div>

                    <div class="agent-name">
                        Investigator
                    </div>

                    <div class="agent-description">
                        Analyze telemetry and identify
                        operational issues.
                    </div>

                </div>


                <div class="pipeline-arrow">
                    →
                </div>


                <div class="agent">

                    <div class="agent-number">
                        2
                    </div>

                    <div class="agent-name">
                        Policy & Compliance
                    </div>

                    <div class="agent-description">
                        Retrieve RAG context and
                        evaluate policy.
                    </div>

                </div>


                <div class="pipeline-arrow">
                    →
                </div>


                <div class="agent">

                    <div class="agent-number">
                        3
                    </div>

                    <div class="agent-name">
                        Resolution
                    </div>

                    <div class="agent-description">
                        Generate controlled
                        operational action.
                    </div>

                </div>

            </div>
            """)


            # =================================================
            # TRACE HEADER
            # =================================================

            ui_html("""
            <div class="section-header">

                <div class="section-title">
                    Agent Execution Trace
                </div>

                <div class="section-line"></div>

            </div>
            """)


            # =================================================
            # INVESTIGATOR
            # =================================================

            with st.expander(
                "STEP 01   ·   OPERATIONS INVESTIGATOR AGENT",
                expanded=True
            ):

                st.json(
                    result["investigation"]
                )


            # =================================================
            # POLICY
            # =================================================

            with st.expander(
                "STEP 02   ·   POLICY & COMPLIANCE AGENT",
                expanded=False
            ):

                st.write(
                    "**Retrieved Sources:**",
                    result[
                        "policy_evaluation"
                    ].get(
                        "sources"
                    )
                )

                st.write(
                    "**LLM Evaluation:**",
                    result[
                        "policy_evaluation"
                    ].get(
                        "llm_evaluation"
                    )
                )


            # =================================================
            # RESOLUTION
            # =================================================

            with st.expander(
                "STEP 03   ·   RESOLUTION AGENT",
                expanded=True
            ):

                recommendation = (
                    result[
                        "resolution"
                    ][
                        "recommendation"
                    ]
                )

                st.markdown(
                    recommendation
                )


# ============================================================
# RIGHT — AUDIT
# ============================================================

with right_column:

    # --------------------------------------------------------
    # AUDIT HEADER
    # --------------------------------------------------------

    ui_html("""
    <div class="panel">

        <div class="panel-title">
            ▣ &nbsp; SYSTEM AUDIT & DISTILLATION LOGS
        </div>

        <div class="command-heading">
            Recorded JSONL Audit Trail
        </div>

        <div class="command-description">
            Execution records and distilled training events.
        </div>

    </div>
    """)


    # ========================================================
    # AUDIT FILE
    # ========================================================

    if AUDIT_LOG_PATH.exists():

        with open(
            AUDIT_LOG_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            lines = file.readlines()


        # ====================================================
        # PARSE RECORDS
        # ====================================================

        if lines:

            records = []


            for line in lines:

                try:

                    records.append(
                        json.loads(line)
                    )

                except json.JSONDecodeError:

                    continue


            # =================================================
            # EVENT COUNT
            # =================================================

            ui_html(f"""
            <div style="
                color:#555555;
                font-family:'JetBrains Mono',monospace;
                font-size:8px;
                margin-top:15px;
                margin-bottom:10px;
            ">

                {len(records)} REGISTERED EVENTS

            </div>
            """)


            # =================================================
            # AUDIT TABLE
            # =================================================

            recent_records = (
                records[-10:][::-1]
            )


            table_rows = ""


            for record in recent_records:

                # ---------------------------------------------
                # Risk
                # ---------------------------------------------

                risk = str(
                    record.get(
                        "risk_level",
                        "UNKNOWN"
                    )
                ).upper()


                if risk == "LOW":

                    risk_class = "badge-green"

                elif risk == "HIGH":

                    risk_class = "badge-red"

                else:

                    risk_class = "badge-yellow"


                # ---------------------------------------------
                # Timestamp
                # ---------------------------------------------

                timestamp = html.escape(
                    str(
                        record.get(
                            "timestamp",
                            ""
                        )
                    )
                )


                # ---------------------------------------------
                # Airport
                # ---------------------------------------------

                airport = html.escape(
                    str(
                        record.get(
                            "airport_code",
                            ""
                        )
                    )
                )


                # ---------------------------------------------
                # Query
                # ---------------------------------------------

                query = html.escape(
                    str(
                        record.get(
                            "query",
                            ""
                        )
                    )[:35]
                )


                # ---------------------------------------------
                # Row
                # ---------------------------------------------

                table_rows += f"""
                <tr>

                    <td>
                        {timestamp}
                    </td>

                    <td>
                        {airport}
                    </td>

                    <td>

                        <span class="badge {risk_class}">
                            {html.escape(risk)}
                        </span>

                    </td>

                    <td>
                        {query}
                    </td>

                </tr>
                """


            # =================================================
            # TABLE
            # =================================================

            ui_html(f"""
            <table class="audit-table">

                <thead>

                    <tr>

                        <th>
                            Timestamp
                        </th>

                        <th>
                            Airport
                        </th>

                        <th>
                            Risk
                        </th>

                        <th>
                            Query
                        </th>

                    </tr>

                </thead>

                <tbody>

                    {table_rows}

                </tbody>

            </table>
            """)


            # =================================================
            # LATEST EVENT
            # =================================================

            ui_html("""
            <div style="
                margin-top:25px;
                margin-bottom:10px;
                color:#D4D4D4;
                font-size:11px;
                font-weight:600;
            ">
                Latest Event Payload
            </div>
            """)


            latest_json = json.dumps(
                records[-1],
                indent=2
            )


            safe_latest_json = html.escape(
                latest_json
            )


            ui_html(f"""
            <div class="json-box">

                <pre>{safe_latest_json}</pre>

            </div>
            """)


        # ====================================================
        # EMPTY FILE
        # ====================================================

        else:

            st.info(
                "Audit log file is empty."
            )


    # ========================================================
    # NO FILE
    # ========================================================

    else:

        st.info(
            "No audit logs recorded yet."
        )