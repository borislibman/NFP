import urllib.request
import json
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, date

# ─────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NFP Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&family=IBM+Plex+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Mono', monospace !important;
    background-color: #07090c !important;
    color: #dde8f0 !important;
}
.stApp { background-color: #07090c; }

/* Remove default streamlit padding */
.block-container { padding-top: 1rem !important; padding-bottom: 1.5rem !important; max-width: 1400px !important; }

/* Metric cards */
div[data-testid="metric-container"] {
    background: #0f1318;
    border: 1px solid #1c2530;
    padding: 16px 20px 12px;
    border-radius: 2px;
}
div[data-testid="metric-container"] label {
    font-size: 10px !important;
    letter-spacing: .18em;
    color: #7a9ab5 !important;
    text-transform: uppercase;
    font-family: 'IBM Plex Mono', monospace !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 2.0rem !important;
    font-weight: 700 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    letter-spacing: 0 !important;
}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 13px !important;
    font-family: 'IBM Plex Mono', monospace !important;
}

/* Section headers */
.section-hdr {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .22em;
    color: #dde8f0;
    text-transform: uppercase;
    border-bottom: 1px solid #243040;
    padding-bottom: 10px;
    margin: 28px 0 16px;
}

/* Signal score card */
.sig-card {
    background: #0f1318;
    border: 1px solid #1c2530;
    padding: 24px 28px;
    border-radius: 2px;
}
.sig-score-big { font-size: 56px; font-weight: 700; line-height: 1; }
.sig-label { font-size: 13px; font-weight: 700; letter-spacing: .2em; margin-top: 6px; }
.sig-sub { font-size: 10px; color: #7a9ab5; margin-top: 4px; letter-spacing: .1em; }
.sig-row {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 10px;
}
.sig-name { font-size: 11px; color: #7a9ab5; width: 130px; flex-shrink: 0; }
.sig-bar-bg { background: #243040; height: 6px; border-radius: 3px; flex: 1; overflow: hidden; }
.sig-bar-fill { height: 100%; border-radius: 3px; }
.sig-pts { font-size: 12px; font-weight: 700; width: 42px; text-align: right; flex-shrink: 0; }
.sig-detail { font-size: 11px; color: #7a9ab5; width: 110px; flex-shrink: 0; }

/* Breakdown rows */
.brow {
    display: flex; justify-content: space-between; align-items: center;
    padding: 8px 0; border-bottom: 1px solid #1c2530;
    font-family: 'IBM Plex Mono', monospace;
}
.brow:last-child { border-bottom: none; }
.bname { font-size: 13px; color: #7a9ab5; }
.bval  { font-size: 16px; font-weight: 700; }

/* Revision cards */
.rev-card {
    background: #0f1318; border: 1px solid #1c2530;
    padding: 18px 20px; border-radius: 2px;
}
.rev-month { font-size: 10px; font-weight: 600; letter-spacing: .15em;
             color: #7a9ab5; text-transform: uppercase; margin-bottom: 10px; }
.rev-val   { font-size: 26px; font-weight: 700; margin-bottom: 6px; }
.rev-prior { font-size: 12px; color: #7a9ab5; margin-bottom: 4px; }
.rev-delta { font-size: 13px; font-weight: 700; }

/* Commentary */
.commentary {
    background: #131920;
    border: 1px solid #243040;
    border-left: 3px solid #00bcd4;
    padding: 24px 28px;
    border-radius: 0 2px 2px 0;
}
.commentary p {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 14px; line-height: 1.8; color: #dde8f0;
    margin-bottom: 14px; padding-bottom: 14px;
    border-bottom: 1px solid #1c2530;
}
.commentary p:last-child { margin-bottom: 0; padding-bottom: 0; border-bottom: none; }
.commentary b { color: #00bcd4; font-weight: 600; }

/* Beat/miss badges */
.badge-beat { color: #00e676; font-weight: 700; font-size: 12px; letter-spacing: .05em; }
.badge-miss { color: #ff4560; font-weight: 700; font-size: 12px; letter-spacing: .05em; }
.badge-line { color: #ffab00; font-weight: 700; font-size: 12px; letter-spacing: .05em; }

/* NFP banner */
.nfp-banner {
    background: linear-gradient(90deg, #00bcd4, #0097a7);
    color: #07090c; font-weight: 700; letter-spacing: .12em;
    font-size: 13px; text-align: center; padding: 10px;
    margin-bottom: 20px; text-transform: uppercase; border-radius: 2px;
}

/* Hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────
def get_api_key():
    try:
        return st.secrets["BLS_API_KEY"]
    except Exception:
        return st.sidebar.text_input("BLS API Key", type="password",
                                     help="Register free at bls.gov/developers")

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

SERIES = {
    "nfp":        "CES0000000001",
    "private":    "CES0500000001",
    "govt":       "CES9000000001",
    "federal":    "CES9091000001",
    "state":      "CES9092000001",
    "local":      "CES9093000001",
    "mfg":        "CES3000000001",
    "durable":    "CES3100000001",
    "nondurable": "CES3200000001",
    "healthcare": "CES6562000001",
    "social_asst":"CES6624000001",
    "retail":     "CES4200000001",
    "transport":  "CES4300000001",
    "construction":"CES2000000001",
    "leisure":    "CES7000000001",
    "prof_biz":   "CES6000000001",
    "financial":  "CES5500000001",
    "information":"CES5000000001",
    "ahe":        "CES0500000003",
    "hours":      "CES0500000002",
    "urate":      "LNS14000000",
    "u6":         "LNS13327709",
    "lfpr":       "LNS11300000",
    "epop_prime": "LNS12300060",
}

# ─────────────────────────────────────────────────────────
# NFP FRIDAY DETECTION
# ─────────────────────────────────────────────────────────
def is_nfp_friday():
    today = date.today()
    return today.weekday() == 4 and today.day <= 7

def next_nfp_friday():
    today = date.today()
    m, y = (1, today.year + 1) if today.month == 12 else (today.month + 1, today.year)
    d = date(y, m, 1)
    return d.replace(day=1 + (4 - d.weekday()) % 7)

# ─────────────────────────────────────────────────────────
# BLS API
# ─────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_all_data(api_key: str, year: int):
    all_ids = list(SERIES.values())
    batches = [all_ids[i:i+12] for i in range(0, len(all_ids), 12)]
    all_results = []
    for batch in batches:
        url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
        payload = json.dumps({
            "seriesid": batch,
            "startyear": str(year - 2),
            "endyear": str(year),
            "registrationkey": api_key
        }).encode("utf-8")
        req = urllib.request.Request(
            url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if data.get("status") != "REQUEST_SUCCEEDED":
            raise Exception("BLS API error: " + str(data.get("message")))
        all_results.extend(data["Results"]["series"])
    return all_results

def parse_series(results, series_id):
    series = next((s for s in results if s["seriesID"] == series_id), None)
    if not series:
        return []
    parsed = []
    for d in series["data"]:
        if not d["period"].startswith("M"):
            continue
        try:
            value = float(d["value"])
        except (ValueError, TypeError):
            continue
        parsed.append({
            "year":  int(d["year"]),
            "month": int(d["period"].replace("M", "")),
            "value": value,
            "label": MONTHS[int(d["period"].replace("M","")) - 1] + " " + d["year"]
        })
    parsed.sort(key=lambda x: x["year"] * 100 + x["month"], reverse=True)
    return parsed

def mom_change(data, idx=0):
    if len(data) < idx + 2:
        return None
    return data[idx]["value"] - data[idx+1]["value"]

# ─────────────────────────────────────────────────────────
# FORMATTERS
# ─────────────────────────────────────────────────────────
def fmt_k(val):
    if val is None: return "—"
    k = round(val)
    return ("+" if k > 0 else "") + f"{k:,}K"

def fmt_pct(val, decimals=1):
    if val is None: return "—"
    return ("+" if val > 0 else "") + f"{val:.{decimals}f}%"

def val_color(val, invert=False):
    if val is None: return "#8899aa"
    if invert:
        return "#ff4560" if val > 0 else "#00e676" if val < 0 else "#8899aa"
    return "#00e676" if val > 0 else "#ff4560" if val < 0 else "#8899aa"

def beat_miss(actual, estimate, higher_is_better=True):
    if actual is None or estimate is None:
        return "", "badge-line"
    diff = actual - estimate
    if abs(diff) < 0.05:
        return "IN LINE", "badge-line"
    if (diff > 0) == higher_is_better:
        return f"BEAT +{abs(diff):.1f}", "badge-beat"
    return f"MISS −{abs(diff):.1f}", "badge-miss"

def delta_str(val, fmt="k"):
    """Format for st.metric delta."""
    if val is None: return None
    if fmt == "k":
        k = round(val)
        return ("+" if k > 0 else "") + f"{k:,}K"
    return ("+" if val > 0 else "") + f"{val:.2f}%"

# ─────────────────────────────────────────────────────────
# SIGNAL SCORE
# ─────────────────────────────────────────────────────────
def compute_signal_score(nfp_mom, urate, urate_chg, ahe_mom_pct,
                          hours_mom, u6, lfpr, epop_prime, consensus):
    components = []

    # Job growth (0-25)
    if nfp_mom is not None:
        k = round(nfp_mom)
        pts = 25 if k >= 200 else 22 if k >= 150 else 18 if k >= 100 else 13 if k >= 50 else 7 if k >= 0 else 0
        components.append({"name": "Job Growth",    "pts": pts, "max": 25, "detail": fmt_k(nfp_mom) + "/mo"})
    else:
        components.append({"name": "Job Growth",    "pts": 0,  "max": 25, "detail": "N/A"})

    # Unemployment (0-20)
    if urate is not None and urate_chg is not None:
        base = 18 if urate <= 3.5 else 15 if urate <= 4.0 else 11 if urate <= 4.5 else 7 if urate <= 5.0 else 3
        trend = 2 if urate_chg < 0 else (-2 if urate_chg > 0.1 else 0)
        pts = max(0, min(20, base + trend))
        components.append({"name": "Unemployment",  "pts": pts, "max": 20,
                            "detail": f"{urate:.1f}% ({fmt_pct(urate_chg,2)})"})
    else:
        components.append({"name": "Unemployment",  "pts": 10, "max": 20, "detail": "N/A"})

    # Wages Goldilocks (0-20)
    if ahe_mom_pct is not None:
        diff = ahe_mom_pct - consensus["ahe_mom"]
        pts = 20 if abs(diff) <= 0.03 else 16 if abs(diff) <= 0.07 else 10 if diff > 0.07 else 14
        components.append({"name": "Wage Pressure", "pts": pts, "max": 20,
                            "detail": fmt_pct(ahe_mom_pct) + " MoM"})
    else:
        components.append({"name": "Wage Pressure", "pts": 10, "max": 20, "detail": "N/A"})

    # Labor supply (0-20)
    pts = 10
    parts = []
    if lfpr is not None:
        pts += 5 if lfpr >= 63.5 else 3 if lfpr >= 62.5 else 1 if lfpr >= 61.5 else -2
        parts.append(f"LFPR {lfpr:.1f}%")
    if epop_prime is not None:
        pts += 5 if epop_prime >= 81.0 else 3 if epop_prime >= 80.0 else 1 if epop_prime >= 79.0 else -2
        parts.append(f"EPOP {epop_prime:.1f}%")
    components.append({"name": "Labor Supply",  "pts": max(0,min(20,pts)), "max": 20,
                        "detail": " / ".join(parts) or "N/A"})

    # Avg hours (0-15)
    if hours_mom is not None:
        pts = 15 if hours_mom >= 0.2 else 12 if hours_mom >= 0.05 else 9 if hours_mom >= -0.05 else 5 if hours_mom >= -0.15 else 2
        components.append({"name": "Avg Hours",     "pts": pts, "max": 15, "detail": fmt_pct(hours_mom) + " MoM"})
    else:
        components.append({"name": "Avg Hours",     "pts": 7,  "max": 15, "detail": "N/A"})

    total = sum(c["pts"] for c in components)
    return total, components

def signal_color(score):
    if score >= 75: return "#00e676"
    if score >= 55: return "#ffab00"
    if score >= 35: return "#ff9100"
    return "#ff4560"

def signal_label(score):
    if score >= 75: return "STRONG"
    if score >= 60: return "SOLID"
    if score >= 45: return "MIXED"
    if score >= 30: return "WEAK"
    return "POOR"

# ─────────────────────────────────────────────────────────
# PLOTLY HELPERS
# ─────────────────────────────────────────────────────────
CHART_BG   = "#0f1318"
CHART_GRID = "#1c2530"
CHART_TICK = "#7a9ab5"
CHART_H    = 200

def hex_to_rgba(hex_color, alpha=0.12):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{alpha})"

def _base_layout(title=""):
    return dict(
        title=dict(text=title, font=dict(size=10, color=CHART_TICK,
                   family="IBM Plex Mono"), x=0.01, y=0.99),
        paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        margin=dict(l=44, r=8, t=22, b=36),
        height=CHART_H,
        xaxis=dict(gridcolor=CHART_GRID, tickfont=dict(size=8, color=CHART_TICK),
                   tickangle=45, showgrid=False),
        yaxis=dict(gridcolor=CHART_GRID, tickfont=dict(size=9, color=CHART_TICK)),
        showlegend=False,
    )

def line_chart(labels, values, color, title=""):
    if not values:
        return go.Figure()
    pad = (max(values) - min(values)) * 0.15 or 0.5
    ymin = min(values) - pad
    ymax = max(values) + pad
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=labels, y=[ymin] * len(labels),
        mode="lines", line=dict(width=0),
        showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=labels, y=values,
        mode="lines+markers",
        line=dict(color=color, width=2),
        marker=dict(size=3, color=color),
        fill="tonexty",
        fillcolor=hex_to_rgba(color, 0.08),
    ))
    layout = _base_layout(title)
    layout["yaxis"]["range"] = [ymin, ymax]
    fig.update_layout(**layout)
    return fig

def bar_chart(labels, values, title=""):
    colors = ["#00e676" if v >= 0 else "#ff4560" for v in values]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=values,
        marker_color=colors,
        marker_line_width=0,
    ))
    fig.update_layout(**_base_layout(title))
    fig.update_layout(bargap=0.25)
    return fig

def chart_pts(data_series, n=13, mom=False):
    """Return (labels, values) oldest-first for last n points."""
    if mom:
        pts = [{"label": data_series[i]["label"],
                "value": round(data_series[i]["value"] - data_series[i+1]["value"])}
               for i in range(min(n, len(data_series)-1))]
    else:
        pts = [{"label": p["label"], "value": p["value"]} for p in data_series[:n]]
    pts = list(reversed(pts))
    return [p["label"] for p in pts], [p["value"] for p in pts]

# ─────────────────────────────────────────────────────────
# COMMENTARY
# ─────────────────────────────────────────────────────────
def generate_commentary(nfp_mom, private_mom, govt_mom, federal_mom,
                         mfg_mom, durable_mom, nondurable_mom,
                         urate, urate_chg, ahe_mom_pct, ahe_yoy_pct,
                         hours, hours_mom,
                         healthcare_mom, social_mom, retail_mom, transport_mom,
                         construction_mom, leisure_mom, prof_mom, financial_mom, info_mom,
                         revisions, consensus, current_month,
                         u6, lfpr, epop_prime):

    nfp_k = round(nfp_mom) if nfp_mom is not None else 0
    est   = consensus["nfp"]
    diff  = nfp_k - est

    try:
        month_full = datetime.strptime(current_month.split()[0], "%b").strftime("%B")
    except Exception:
        month_full = "This month"

    # Headline
    if diff > 50:
        headline = (f"<b>Major beat:</b> {month_full} payrolls surged to {fmt_k(nfp_mom)}, nearly double "
                    f"the {est}K consensus. This is an unambiguously strong print that removes any near-term "
                    f"recession narrative and puts rate-cut expectations firmly on the back burner.")
    elif diff > 20:
        headline = (f"<b>Strong beat:</b> {fmt_k(nfp_mom)} vs the {est}K estimate — labor market resilience "
                    f"intact. The beat is large enough to shift rate expectations at the margin and should "
                    f"be received as risk-positive.")
    elif diff > 5:
        headline = (f"<b>Modest beat:</b> {fmt_k(nfp_mom)} vs {est}K estimate — labor market holding up "
                    f"without giving the Fed reason to move in either direction.")
    elif diff > -5:
        headline = (f"<b>In-line print:</b> {fmt_k(nfp_mom)} essentially matched the {est}K consensus. "
                    f"No market-moving surprise. Attention shifts to composition and wage data for the real signal.")
    elif diff > -30:
        headline = (f"<b>Mild miss:</b> {fmt_k(nfp_mom)} vs {est}K estimate — softening but not alarming. "
                    f"The labor market is cooling gradually. Watch the trend over the next 2–3 prints.")
    else:
        headline = (f"<b>Significant miss:</b> {fmt_k(nfp_mom)} vs {est}K estimate — a material "
                    f"disappointment that reignites recession risk discussion.")

    # Composition
    comp_lines = []
    if private_mom is not None and govt_mom is not None:
        if private_mom > 0 and govt_mom < 0:
            comp_lines.append(
                f"The composition is constructive: private sector drove all of the gain ({fmt_k(private_mom)}) "
                f"while government contracted ({fmt_k(govt_mom)}). Private-led growth is the higher-quality read.")
        elif private_mom > 0 and govt_mom > 0:
            comp_lines.append(f"Both private ({fmt_k(private_mom)}) and government ({fmt_k(govt_mom)}) payrolls "
                               f"expanded — broad-based strength.")
        elif private_mom < 0 and govt_mom > 0:
            comp_lines.append(f"Headline masks a concerning split: private payrolls declined ({fmt_k(private_mom)}) "
                               f"while government hiring ({fmt_k(govt_mom)}) propped up the number.")
        elif private_mom < 0:
            comp_lines.append(f"Private payrolls declined ({fmt_k(private_mom)}) — a red flag regardless of headline.")
    if federal_mom is not None and federal_mom < -5:
        comp_lines.append(
            f"Federal employment fell another {fmt_k(federal_mom)}, extending the DOGE-driven drawdown. "
            f"This is a structural, policy-driven drag — not a signal of cyclical weakness.")

    # Breadth
    breadth_lines = []
    if u6 is not None:
        u6_est = consensus.get("u6", 7.9)
        spread = round(u6 - (urate or 0), 1) if urate else None
        if u6 < u6_est - 0.1:
            breadth_lines.append(
                f"<b>Underemployment (U-6):</b> {u6:.1f}% — below the {u6_est}% estimate. "
                f"More slack is being absorbed than the headline rate implies."
                + (f" The U-6/U-3 spread of {spread}pp is tight, consistent with a fully employed labor market." if spread is not None else ""))
        elif u6 > u6_est + 0.1:
            breadth_lines.append(
                f"<b>Underemployment (U-6):</b> {u6:.1f}% — above the {u6_est}% estimate. "
                f"Elevated underemployment signals more hidden slack than the headline rate suggests.")
        else:
            breadth_lines.append(f"<b>Underemployment (U-6):</b> {u6:.1f}% — in line with estimates.")

    if lfpr is not None or epop_prime is not None:
        lfpr_str = f"LFPR {lfpr:.1f}%" if lfpr else ""
        epop_str = f"prime-age EPOP {epop_prime:.1f}%" if epop_prime else ""
        both = " / ".join(filter(None, [lfpr_str, epop_str]))
        if epop_prime is not None and epop_prime >= 80.5:
            breadth_lines.append(f"<b>Labor supply:</b> {both}. Prime-age EPOP above 80.5% signals the core "
                                  f"working-age cohort is nearly fully employed — structurally tight labor market.")
        elif epop_prime is not None and epop_prime < 79.5:
            breadth_lines.append(f"<b>Labor supply:</b> {both}. Prime-age EPOP below 79.5% suggests meaningful "
                                  f"remaining supply — the Fed has room to see job growth continue without it "
                                  f"being inherently inflationary.")
        elif both:
            breadth_lines.append(f"<b>Labor supply:</b> {both} — within normal range, no unusual signal.")

    # Sectors
    sector_lines = []
    sectors = [
        ("Healthcare", healthcare_mom), ("Social assistance", social_mom),
        ("Retail trade", retail_mom), ("Transportation & warehousing", transport_mom),
        ("Construction", construction_mom), ("Leisure & hospitality", leisure_mom),
        ("Professional & business svc", prof_mom), ("Financial activities", financial_mom),
        ("Information", info_mom), ("Manufacturing", mfg_mom),
    ]
    gainers = sorted([(n,v) for n,v in sectors if v is not None and v > 5], key=lambda x: -x[1])
    losers  = sorted([(n,v) for n,v in sectors if v is not None and v < -5], key=lambda x:  x[1])
    if gainers:
        sector_lines.append("Top contributors: " + ", ".join(f"{n} ({fmt_k(v)})" for n,v in gainers[:4]) + ".")
    if losers:
        sector_lines.append("Sectors shedding jobs: " + ", ".join(f"{n} ({fmt_k(v)})" for n,v in losers[:3]) + ".")
    if healthcare_mom is not None:
        if healthcare_mom > 50:
            sector_lines.append(f"Healthcare's {fmt_k(healthcare_mom)} gain is outsized — likely reflects "
                                 f"post-strike normalization plus structural demographic demand.")
        elif healthcare_mom > 20:
            sector_lines.append(f"Healthcare added {fmt_k(healthcare_mom)}, in line with its ~32K/month trend. "
                                 f"Structural hiring continues to be the ballast of the employment report.")
        elif healthcare_mom < 10:
            sector_lines.append(f"Healthcare added only {fmt_k(healthcare_mom)} — well below its ~32K average. "
                                 f"If this slowdown persists it removes the primary engine of job creation.")
    if mfg_mom is not None:
        if mfg_mom > 15:
            sector_lines.append(f"Manufacturing added {fmt_k(mfg_mom)} ({fmt_k(durable_mom)} durable / "
                                 f"{fmt_k(nondurable_mom)} nondurable) — positive signal for goods-producing sector.")
        elif mfg_mom < -10:
            sector_lines.append(f"Manufacturing shed {fmt_k(mfg_mom)} ({fmt_k(durable_mom)} durable / "
                                 f"{fmt_k(nondurable_mom)} nondurable) — trade policy uncertainty showing up in hiring.")
        else:
            sector_lines.append(f"Manufacturing roughly flat ({fmt_k(mfg_mom)}) — holding pattern amid tariff cross-currents.")

    # Wages
    wage_lines = []
    if ahe_mom_pct is not None and ahe_yoy_pct is not None:
        ahe_est = consensus["ahe_mom"]
        if ahe_mom_pct < ahe_est - 0.05:
            wage_lines.append(f"<b>Wages — Goldilocks:</b> AHE {fmt_pct(ahe_mom_pct)} MoM / "
                               f"{fmt_pct(ahe_yoy_pct)} YoY, below the {fmt_pct(ahe_est)} estimate. "
                               f"Strong job creation without inflationary wage pressure — best combination "
                               f"for risk assets. Removes the hike tail.")
        elif ahe_mom_pct > ahe_est + 0.05:
            wage_lines.append(f"<b>Wages — Hawkish:</b> AHE {fmt_pct(ahe_mom_pct)} MoM / "
                               f"{fmt_pct(ahe_yoy_pct)} YoY, above the {fmt_pct(ahe_est)} estimate. "
                               f"Wage growth at {fmt_pct(ahe_yoy_pct)} annualized is incompatible with 2% inflation "
                               f"without a productivity offset. Rate hike probability rises at the margin.")
        else:
            wage_lines.append(f"<b>Wages — Neutral:</b> AHE {fmt_pct(ahe_mom_pct)} MoM / "
                               f"{fmt_pct(ahe_yoy_pct)} YoY — in line. No new inflation signal from labor costs.")
    if hours is not None and hours_mom is not None:
        if hours_mom > 0.05:
            wage_lines.append(f"Avg weekly hours ticked up to {hours:.1f} hrs ({fmt_pct(hours_mom)} MoM). "
                               f"Rising hours means aggregate labor input is expanding faster than headcount alone.")
        elif hours_mom < -0.05:
            wage_lines.append(f"Avg weekly hours slipped to {hours:.1f} hrs ({fmt_pct(hours_mom)} MoM). "
                               f"Employers reducing hours before headcount — a classic leading indicator to watch.")
        else:
            wage_lines.append(f"Avg weekly hours flat at {hours:.1f} hrs — no new signal from hours channel.")

    # Revisions
    rev_lines = []
    if len(revisions) >= 3:
        net = sum(r["change"] for r in revisions[1:3])
        net_k = round(net)
        details = []
        for r in revisions[1:3]:
            if r["prior"] is not None and r["rev_delta"] is not None:
                direction = "up" if r["rev_delta"] > 0 else "down"
                details.append(f"{r['label']} revised {direction} {fmt_k(abs(r['rev_delta']))} to {fmt_k(r['change'])}")
        summary = ("The upward revisions reinforce re-acceleration." if net_k > 10
                   else "The downward revisions temper the headline." if net_k < -10
                   else "Revisions are minor, leaving the trend intact.")
        if details:
            rev_lines.append(f"Revisions: {'; '.join(details)}. Net two-month: {fmt_k(net)}. {summary}")
        else:
            rev_lines.append(f"Net two-month revision: {fmt_k(net)}. {summary}")

    # Fed implications
    fed_lines = []
    if ahe_mom_pct is not None and nfp_mom is not None:
        hot_w  = ahe_mom_pct > consensus["ahe_mom"] + 0.05
        soft_w = ahe_mom_pct < consensus["ahe_mom"] - 0.05
        strong = round(nfp_mom) > 100
        weak   = round(nfp_mom) < 30
        if strong and hot_w:
            fed_lines.append("<b>Fed implications:</b> Strong jobs + hot wages — the hawkish combination. "
                             "No room to cut; hike probability rises at the margin. "
                             "Expect Powell to emphasize patience. ES: initial pop may fade as hike tail reprices.")
        elif strong and soft_w:
            fed_lines.append("<b>Fed implications:</b> Goldilocks — strong hiring without wage-driven inflation. "
                             "Fed stays on hold, no urgency in either direction. "
                             "ES: net positive — recession fears fade, hike risk contained.")
        elif weak and soft_w:
            fed_lines.append("<b>Fed implications:</b> Weak jobs + contained wages reopens cut debate, "
                             "but inflation backdrop prevents dovish action. Fed paralysis — can't cut, can't hike. "
                             "ES likely lower on growth concern despite rate relief.")
        elif weak and hot_w:
            fed_lines.append("<b>Fed implications:</b> Stagflationary signal — the worst combination. "
                             "Cannot cut (inflation), cannot hike (growth risk). "
                             "Associated with equity underperformance and gold strength.")
        else:
            fed_lines.append("<b>Fed implications:</b> Consistent with continued patience. "
                             "Fed on hold — not decisive enough to shift the calculus. "
                             "CME hike/cut odds unlikely to move significantly.")

    sections = []
    for group in [headline], comp_lines, breadth_lines, sector_lines, wage_lines, rev_lines, fed_lines:
        if isinstance(group, str): sections.append(group)
        elif group: sections.extend(group if isinstance(group, list) else [group])
    return sections

# ─────────────────────────────────────────────────────────
# HTML HELPERS
# ─────────────────────────────────────────────────────────
def brow_html(rows):
    """rows = [(name, formatted_val, raw_val), ...]"""
    html = ""
    for name, val, raw in rows:
        color = val_color(raw)
        html += f"""<div class="brow">
          <span class="bname">{name}</span>
          <span class="bval" style="color:{color}">{val}</span>
        </div>"""
    return html

def rev_card_html(r, prior_reported):
    change = r["change"]
    label  = r["label"]
    prior  = r.get("prior")
    delta  = r.get("rev_delta")
    color  = val_color(change)
    val_s  = fmt_k(change)
    delta_html = prior_html = ""
    if delta is not None and prior is not None:
        d_color = "#00e676" if delta > 0 else "#ff4560" if delta < 0 else "#ffab00"
        arrow   = "▲" if delta > 0 else "▼"
        delta_html = f"<div class='rev-delta' style='color:{d_color}'>{arrow} {fmt_k(abs(delta))} vs prev rpt</div>"
        prior_html = f"<div class='rev-prior'>Prev: {fmt_k(prior)}</div>"
    inner = prior_html + delta_html
    return (
        f'<div class="rev-card">'
        f'<div class="rev-month">{label}</div>'
        f'<div class="rev-val" style="color:{color}">{val_s}</div>'
        + inner +
        '</div>'
    )

def signal_bars_html(components):
    html = ""
    for c in components:
        pct = (c["pts"] / c["max"]) * 100
        color = signal_color(pct)
        html += f"""<div class="sig-row">
          <div class="sig-name">{c["name"]}</div>
          <div class="sig-bar-bg"><div class="sig-bar-fill" style="width:{pct:.0f}%;background:{color}"></div></div>
          <div class="sig-pts" style="color:{color}">{c["pts"]}/{c["max"]}</div>
          <div class="sig-detail">{c["detail"]}</div>
        </div>"""
    return html

# ─────────────────────────────────────────────────────────
# SIDEBAR — CONSENSUS CONFIG
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.markdown("**Consensus Estimates**")
    CONSENSUS = {
        "nfp":     st.number_input("NFP (K)",      value=65,  step=5),
        "urate":   st.number_input("U-Rate (%)",   value=4.3, step=0.1, format="%.1f"),
        "ahe_mom": st.number_input("AHE MoM (%)",  value=0.3, step=0.05, format="%.2f"),
        "ahe_yoy": st.number_input("AHE YoY (%)",  value=3.8, step=0.1,  format="%.1f"),
        "u6":      st.number_input("U-6 (%)",      value=7.9, step=0.1,  format="%.1f"),
        "lfpr":    st.number_input("LFPR (%)",      value=62.5,step=0.1, format="%.1f"),
    }
    st.markdown("---")
    st.markdown("**Prior Reported (for revision delta)**")
    pr_feb = st.number_input("Feb 2026 prior (K)", value=-133, step=1)
    pr_mar = st.number_input("Mar 2026 prior (K)", value=178,  step=1)
    PRIOR_REPORTED = {"Feb 2026": pr_feb, "Mar 2026": pr_mar}
    st.markdown("---")
    refresh = st.button("🔄 Refresh Data", use_container_width=True)
    if refresh:
        st.cache_data.clear()

# ─────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────
api_key = get_api_key()

if not api_key:
    st.warning("Enter your BLS API key in the sidebar to load data. "
               "Register free at [bls.gov/developers](https://www.bls.gov/developers/home.htm).")
    st.stop()

# Header
nfp_day = is_nfp_friday()
if nfp_day:
    st.markdown("<div class='nfp-banner'>★ NFP RELEASE DAY — EMPLOYMENT SITUATION ★</div>",
                unsafe_allow_html=True)

col_title, col_date = st.columns([3, 1])
with col_title:
    st.markdown("<div style='font-size:26px;font-weight:700;letter-spacing:.14em;"
                "color:#00bcd4;text-transform:uppercase'>NFP Dashboard</div>", unsafe_allow_html=True)
with col_date:
    st.markdown(f"<div style='text-align:right;font-size:15px;font-weight:600'>"
                f"{datetime.now().strftime('%B %d, %Y')}</div>"
                f"<div style='text-align:right;font-size:12px;color:#7a9ab5'>"
                f"{datetime.now().strftime('%I:%M %p')} ET</div>", unsafe_allow_html=True)

st.markdown("<hr style='border-color:#243040;margin:16px 0 24px'>", unsafe_allow_html=True)

# Load data
with st.spinner("Fetching data from BLS API..."):
    try:
        year = datetime.now().year
        raw = fetch_all_data(api_key, year)
    except Exception as e:
        st.error(f"BLS API error: {e}")
        st.stop()

data = {k: parse_series(raw, v) for k, v in SERIES.items()}

# ── Core calcs ─────────────────────────────────────────
nfp_mom         = mom_change(data["nfp"])
private_mom     = mom_change(data["private"])
govt_mom        = mom_change(data["govt"])
federal_mom     = mom_change(data["federal"])
state_mom       = mom_change(data["state"])
local_mom       = mom_change(data["local"])
mfg_mom         = mom_change(data["mfg"])
durable_mom     = mom_change(data["durable"])
nondurable_mom  = mom_change(data["nondurable"])
healthcare_mom  = mom_change(data["healthcare"])
social_mom      = mom_change(data["social_asst"])
retail_mom      = mom_change(data["retail"])
transport_mom   = mom_change(data["transport"])
construction_mom= mom_change(data["construction"])
leisure_mom     = mom_change(data["leisure"])
prof_mom        = mom_change(data["prof_biz"])
financial_mom   = mom_change(data["financial"])
info_mom        = mom_change(data["information"])
hours_mom       = mom_change(data["hours"])

ahe_cur      = data["ahe"][0]["value"] if data["ahe"] else None
ahe_prior    = data["ahe"][1]["value"] if len(data["ahe"]) > 1 else None
ahe_mom_pct  = ((ahe_cur - ahe_prior) / ahe_prior * 100) if ahe_cur and ahe_prior else None
ahe_year_ago = next((d for d in data["ahe"]
                     if d["month"] == data["ahe"][0]["month"]
                     and d["year"] == data["ahe"][0]["year"] - 1), None) if data["ahe"] else None
ahe_yoy_pct  = ((ahe_cur - ahe_year_ago["value"]) / ahe_year_ago["value"] * 100) \
               if ahe_cur and ahe_year_ago else None

urate        = data["urate"][0]["value"] if data["urate"] else None
urate_prior  = data["urate"][1]["value"] if len(data["urate"]) > 1 else None
urate_chg    = (urate - urate_prior) if urate and urate_prior else None
hours        = data["hours"][0]["value"] if data["hours"] else None

u6           = data["u6"][0]["value"]        if data["u6"]       else None
u6_prior     = data["u6"][1]["value"]        if len(data["u6"]) > 1 else None
u6_chg       = (u6 - u6_prior)              if u6 and u6_prior  else None
lfpr         = data["lfpr"][0]["value"]      if data["lfpr"]     else None
lfpr_prior   = data["lfpr"][1]["value"]      if len(data["lfpr"]) > 1 else None
lfpr_chg     = (lfpr - lfpr_prior)          if lfpr and lfpr_prior else None
epop_prime   = data["epop_prime"][0]["value"] if data["epop_prime"] else None

current_month = data["nfp"][0]["label"] if data["nfp"] else "N/A"

revisions = []
for i in range(3):
    if len(data["nfp"]) > i + 1:
        chg = data["nfp"][i]["value"] - data["nfp"][i+1]["value"]
        lbl = data["nfp"][i]["label"]
        prior = PRIOR_REPORTED.get(lbl)
        rev_delta = (round(chg) - prior) if prior is not None else None
        revisions.append({"label": lbl, "change": chg, "prior": prior, "rev_delta": rev_delta})

nfp_k = round(nfp_mom) if nfp_mom is not None else None
nfp_bm,   nfp_bm_cls   = beat_miss(nfp_k, CONSENSUS["nfp"])
urate_bm, urate_bm_cls = beat_miss(urate, CONSENSUS["urate"], higher_is_better=False)
ahe_bm,   ahe_bm_cls   = beat_miss(round(ahe_mom_pct,1) if ahe_mom_pct else None,
                                     CONSENSUS["ahe_mom"], higher_is_better=False)
u6_bm,    u6_bm_cls    = (beat_miss(u6, CONSENSUS["u6"], higher_is_better=False) if u6 else ("","badge-line"))
lfpr_bm,  lfpr_bm_cls  = (beat_miss(lfpr, CONSENSUS["lfpr"]) if lfpr else ("","badge-line"))

score, sig_comps = compute_signal_score(
    nfp_mom, urate, urate_chg, ahe_mom_pct, hours_mom,
    u6, lfpr, epop_prime, CONSENSUS)
sig_c = signal_color(score)
sig_l = signal_label(score)

# Subtitle with signal badge
st.markdown(
    f"<div style='margin-bottom:4px;font-size:14px;color:#7a9ab5'>Employment Situation — {current_month}"
    f"&nbsp;&nbsp;&nbsp;<span style='padding:3px 12px;border-radius:3px;font-size:11px;font-weight:700;"
    f"letter-spacing:.15em;background:{sig_c}20;color:{sig_c};border:1px solid {sig_c}40'>"
    f"SIGNAL: {sig_l} {score}/100</span></div>",
    unsafe_allow_html=True)

# ── SECTION: Headline ──────────────────────────────────
st.markdown("<div class='section-hdr'>Headline</div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    d_val = delta_str(nfp_mom - CONSENSUS["nfp"] * 1000 / 1000)  # show vs consensus
    st.metric("Nonfarm Payrolls", fmt_k(nfp_mom),
              delta=f"vs {CONSENSUS['nfp']}K est",
              delta_color="normal" if nfp_mom and nfp_mom > 0 else "inverse")
    st.markdown(f"<span class='{nfp_bm_cls}'>{nfp_bm}</span>", unsafe_allow_html=True)
with c2:
    st.metric("Unemployment Rate",
              f"{urate:.1f}%" if urate else "—",
              delta=fmt_pct(urate_chg, 2) if urate_chg else None,
              delta_color="inverse")
    st.markdown(f"<span class='{urate_bm_cls}'>{urate_bm}</span>", unsafe_allow_html=True)
with c3:
    st.metric("Avg Hourly Earnings",
              fmt_pct(ahe_mom_pct) if ahe_mom_pct else "—",
              delta=f"YoY: {fmt_pct(ahe_yoy_pct)}" if ahe_yoy_pct else None,
              delta_color="off")
    st.markdown(f"<span class='{ahe_bm_cls}'>{ahe_bm}</span>", unsafe_allow_html=True)

c4, c5, c6 = st.columns(3)
with c4:
    st.metric("Avg Weekly Hours", f"{hours:.1f} hrs" if hours else "—",
              delta=fmt_pct(hours_mom) if hours_mom else None, delta_color="normal")
with c5:
    st.metric("Private Payrolls", fmt_k(private_mom),
              delta=None, delta_color="normal")
with c6:
    st.metric("Government Payrolls", fmt_k(govt_mom),
              delta=None, delta_color="normal")

# ── SECTION: Expanded Indicators ──────────────────────
st.markdown("<div class='section-hdr'>Expanded Labor Market Indicators</div>", unsafe_allow_html=True)

ec1, ec2, ec3 = st.columns(3)
with ec1:
    if u6 is not None:
        st.metric("U-6 Underemployment", f"{u6:.1f}%",
                  delta=fmt_pct(u6_chg, 2) if u6_chg else None, delta_color="inverse")
        st.markdown(f"<span class='{u6_bm_cls}'>{u6_bm}</span>", unsafe_allow_html=True)
with ec2:
    if lfpr is not None:
        st.metric("Labor Force Part. Rate", f"{lfpr:.1f}%",
                  delta=fmt_pct(lfpr_chg, 2) if lfpr_chg else None, delta_color="normal")
        st.markdown(f"<span class='{lfpr_bm_cls}'>{lfpr_bm}</span>", unsafe_allow_html=True)
with ec3:
    if epop_prime is not None:
        st.metric("Prime-Age EPOP (25–54)", f"{epop_prime:.1f}%")

# ── SECTION: Signal Score ──────────────────────────────
st.markdown("<div class='section-hdr'>Labor Market Signal Score</div>", unsafe_allow_html=True)

sc1, sc2 = st.columns([1, 1])
with sc1:
    st.markdown(
        f"""<div class="sig-card">
          <div style="display:flex;align-items:center;gap:20px;margin-bottom:20px">
            <div>
              <div class="sig-score-big" style="color:{sig_c}">{score}</div>
              <div style="font-size:12px;color:#7a9ab5;margin-top:4px">out of 100</div>
            </div>
            <div>
              <div class="sig-label" style="color:{sig_c}">{sig_l}</div>
              <div class="sig-sub">COMPOSITE LABOR HEALTH SCORE</div>
              <div style="font-size:11px;color:#7a9ab5;margin-top:8px;line-height:1.7">
                5 dimensions: job growth,<br>unemployment, wages,<br>labor supply, avg hours
              </div>
            </div>
          </div>
          {signal_bars_html(sig_comps)}
        </div>""",
        unsafe_allow_html=True)

with sc2:
    if data["nfp"]:
        lbs, vals = chart_pts(data["nfp"], n=13, mom=True)
        st.plotly_chart(bar_chart(lbs, vals, "Monthly Payroll Change (K)"),
                        use_container_width=True, config={"displayModeBar": False})

# ── SECTION: Trend Charts ──────────────────────────────
st.markdown("<div class='section-hdr'>Historical Trends — 13 Months</div>", unsafe_allow_html=True)

tc1, tc2, tc3 = st.columns(3)
charts_row1 = [
    (tc1, data["urate"],  "#ff4560", "Unemployment Rate (%)"),
    (tc2, data["ahe"],    "#ffab00", "Avg Hourly Earnings ($/hr)"),
    (tc3, data["lfpr"],   "#00bcd4", "Labor Force Participation Rate (%)"),
]
for col, series, color, title in charts_row1:
    with col:
        if series:
            lbs, vals = chart_pts(series, n=13)
            st.plotly_chart(line_chart(lbs, vals, color, title),
                            use_container_width=True, config={"displayModeBar": False})

tc4, tc5 = st.columns(2)
with tc4:
    if data["u6"]:
        lbs, vals = chart_pts(data["u6"], n=13)
        st.plotly_chart(line_chart(lbs, vals, "#ff9100", "U-6 Underemployment Rate (%)"),
                        use_container_width=True, config={"displayModeBar": False})
with tc5:
    if data["epop_prime"]:
        lbs, vals = chart_pts(data["epop_prime"], n=13)
        st.plotly_chart(line_chart(lbs, vals, "#00e676", "Prime-Age EPOP, 25–54 (%)"),
                        use_container_width=True, config={"displayModeBar": False})

# ── SECTION: Breakdown ─────────────────────────────────
st.markdown("<div class='section-hdr'>Breakdown</div>", unsafe_allow_html=True)

bc1, bc2, bc3 = st.columns(3)
with bc1:
    st.markdown(f"""<div class="breakdown-card" style="background:#0f1318;border:1px solid #1c2530;padding:20px 24px">
      <div class="btitle" style="font-size:11px;font-weight:700;letter-spacing:.18em;color:#00bcd4;
           text-transform:uppercase;margin-bottom:16px">Government Detail</div>
      {brow_html([("Federal", fmt_k(federal_mom), federal_mom),
                  ("State",   fmt_k(state_mom),   state_mom),
                  ("Local",   fmt_k(local_mom),   local_mom)])}
    </div>""", unsafe_allow_html=True)
with bc2:
    st.markdown(f"""<div class="breakdown-card" style="background:#0f1318;border:1px solid #1c2530;padding:20px 24px">
      <div class="btitle" style="font-size:11px;font-weight:700;letter-spacing:.18em;color:#00bcd4;
           text-transform:uppercase;margin-bottom:16px">Manufacturing</div>
      {brow_html([("Total Mfg",       fmt_k(mfg_mom),        mfg_mom),
                  ("Durable Goods",   fmt_k(durable_mom),    durable_mom),
                  ("Nondurable Goods",fmt_k(nondurable_mom), nondurable_mom)])}
    </div>""", unsafe_allow_html=True)
with bc3:
    industry_rows = [
        ("Healthcare",           healthcare_mom),
        ("Social Assistance",    social_mom),
        ("Retail Trade",         retail_mom),
        ("Transport & Whse",     transport_mom),
        ("Construction",         construction_mom),
        ("Leisure & Hosp",       leisure_mom),
        ("Prof & Biz Svcs",      prof_mom),
        ("Financial Activities", financial_mom),
        ("Information",          info_mom),
    ]
    st.markdown(f"""<div class="breakdown-card" style="background:#0f1318;border:1px solid #1c2530;padding:20px 24px">
      <div class="btitle" style="font-size:11px;font-weight:700;letter-spacing:.18em;color:#00bcd4;
           text-transform:uppercase;margin-bottom:16px">Industry Contributors</div>
      {brow_html([(n, fmt_k(v), v) for n, v in industry_rows])}
    </div>""", unsafe_allow_html=True)

# ── SECTION: Revisions ─────────────────────────────────
st.markdown("<div class='section-hdr'>Prior Months — As Revised Today</div>",
            unsafe_allow_html=True)

rev_cols = st.columns(4)
for i, r in enumerate(revisions[:3]):
    with rev_cols[i]:
        st.markdown(rev_card_html(r, PRIOR_REPORTED), unsafe_allow_html=True)
if len(revisions) >= 3:
    net = sum(r["change"] for r in revisions[1:3])
    with rev_cols[3]:
        net_color = val_color(net)
        st.markdown(f"""<div class="rev-card">
          <div class="rev-month">Net (2-mo)</div>
          <div class="rev-val" style="color:{net_color}">{fmt_k(net)}</div>
          <div class="rev-prior">&nbsp;</div>
        </div>""", unsafe_allow_html=True)

# ── SECTION: Commentary ────────────────────────────────
st.markdown("<div class='section-hdr'>Commentary</div>", unsafe_allow_html=True)

commentary = generate_commentary(
    nfp_mom, private_mom, govt_mom, federal_mom,
    mfg_mom, durable_mom, nondurable_mom,
    urate, urate_chg, ahe_mom_pct, ahe_yoy_pct, hours, hours_mom,
    healthcare_mom, social_mom, retail_mom, transport_mom,
    construction_mom, leisure_mom, prof_mom, financial_mom, info_mom,
    revisions, CONSENSUS, current_month,
    u6, lfpr, epop_prime
)
commentary_html = "\n".join(f"<p>{line}</p>" for line in commentary)
st.markdown(f'<div class="commentary">{commentary_html}</div>', unsafe_allow_html=True)

# ── FOOTER ─────────────────────────────────────────────
st.markdown(
    f"<div style='margin-top:32px;font-size:11px;color:#3a5068;text-align:center;"
    f"border-top:1px solid #1c2530;padding-top:16px'>"
    f"Data: U.S. Bureau of Labor Statistics · "
    f"Refreshed: {datetime.now().strftime('%B %d, %Y %I:%M %p')} ET · "
    f"{'Next NFP Friday: ' + next_nfp_friday().strftime('%B %d, %Y') if not nfp_day else 'NFP Release Day'}"
    f"</div>",
    unsafe_allow_html=True)
