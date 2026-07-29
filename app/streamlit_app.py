"""Streamlit UI for the Renovation Quotation System (portfolio demo).

    streamlit run app/streamlit_app.py

Three tabs:
  * Quote     — survey -> live quote, rental yield, Word/PDF export
  * What-if   — sensitivity of payback to rent & occupancy
  * Analytics — explore the synthetic dataset (interactive charts)
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from renovation_quote.calculators.quotation import Quotation
from renovation_quote.calculators.rental_yield import RentalYieldCalculator
from renovation_quote.data.sample_data import sample_categories
from renovation_quote.data.synthetic import generate_dataset
from renovation_quote.documents.pdf_generator import generate_pdf
from renovation_quote.documents.word_generator import generate_word
from renovation_quote.models.difficulty import Condition, DifficultyMultiplier

st.set_page_config(page_title="Renovation Quotation System", page_icon="🏠", layout="wide")


def _inject_css() -> None:
    """A warm, premium "renovation / interior" skin (muted-earth palette)."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500&display=swap');
        :root {
          --accent:#b0764f; --accent-strong:#96603d;
          --grad:linear-gradient(135deg,#b0764f 0%,#c89b62 100%);
          --ink:#34302a; --muted:#8a7d6c; --border:#e6dccb;
          --surface:#fffdf8; --soft:#f1e7db;
          --serif:'Fraunces',Georgia,'Times New Roman',serif;
          --sans:'IBM Plex Sans',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
        }
        html, body, .stApp, [data-testid="stAppViewContainer"], [class*="css"] { font-family:var(--sans); color:var(--ink); }
        /* serif for headings -> premium interior/contract feel */
        h1, h2, h3, [data-testid="stHeading"] { font-family:var(--serif); letter-spacing:-.01em; color:var(--ink); }
        /* cleaner chrome */
        [data-testid="stToolbar"], [data-testid="stDecoration"] { display:none; }
        #MainMenu, footer { visibility:hidden; }
        [data-testid="stHeader"] { background:transparent; }
        .block-container { padding-top:2.2rem; padding-bottom:3rem; max-width:1180px; }
        /* hero */
        .app-hero__title { font-family:var(--serif); font-weight:600; font-size:2.4rem; letter-spacing:-.01em; color:var(--ink); }
        .app-hero__title .g { background:var(--grad); -webkit-background-clip:text; background-clip:text; color:transparent; font-style:italic; }
        .app-hero__rule { height:4px; width:66px; border-radius:3px; background:var(--grad); margin:.9rem 0 .4rem; }
        .app-hero__sub { color:var(--muted); font-size:1rem; }
        /* metric cards */
        [data-testid="stMetric"] {
          background:var(--surface); border:1px solid var(--border); border-radius:14px;
          padding:.9rem 1.05rem; box-shadow:0 2px 10px -6px rgba(120,80,40,.20);
          position:relative; overflow:hidden;
        }
        [data-testid="stMetric"]::before { content:""; position:absolute; top:0; left:0; right:0; height:3px; background:var(--grad); }
        [data-testid="stMetricValue"] { font-family:var(--serif); font-weight:600; font-size:1.85rem; letter-spacing:-.01em; color:var(--ink); }
        [data-testid="stMetricValue"] > div { overflow:visible; }
        [data-testid="stMetricLabel"] { color:var(--muted); font-family:var(--sans); }
        /* tabs */
        .stTabs [data-baseweb="tab-list"] { gap:6px; border-bottom:1px solid var(--border); }
        .stTabs [data-baseweb="tab"] { font-family:var(--sans); font-weight:600; color:var(--muted); }
        .stTabs [aria-selected="true"] { color:var(--accent-strong); }
        .stTabs [data-baseweb="tab-highlight"] { background:var(--accent); }
        /* buttons */
        .stButton>button, .stDownloadButton>button {
          border-radius:10px; font-weight:600; border:1px solid var(--border); transition:all .15s ease;
        }
        .stButton>button:hover, .stDownloadButton>button:hover { border-color:var(--accent); color:var(--accent-strong); transform:translateY(-1px); }
        /* sidebar */
        [data-testid="stSidebar"] { background:#f3ece0; border-right:1px solid #e9e0d0; }
        /* expanders */
        [data-testid="stExpander"] { border:1px solid var(--border); border-radius:12px; box-shadow:0 2px 8px -6px rgba(120,80,40,.16); }
        [data-testid="stExpander"] summary:hover { color:var(--accent-strong); }
        </style>
        """,
        unsafe_allow_html=True,
    )


_inject_css()

CONDITION_ORDER = ["normal", "aging", "poor", "severe"]

# Chart palette — warm base with a teal "pop" for a designed, professional look
# (the classic terracotta + teal interior pairing), NOT everything one brown.
POP = "#1f9e8a"   # teal — primary chart / pop colour
WARM = "#c15f3c"  # terracotta — secondary series
# Distinct, designed categorical palette (normal -> severe): teal, ochre, terracotta, rust
CAT_SEQ = ["#1f9e8a", "#e0a03e", "#c15f3c", "#7a4a3a"]


def _style_fig(fig):
    """Blend a Plotly figure into the warm cream theme (transparent bg, serif titles)."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#34302a", family="IBM Plex Sans, sans-serif"),
        title_font=dict(family="Fraunces, Georgia, serif", size=18, color="#34302a"),
        margin=dict(t=52, l=8, r=8, b=8),
    )
    fig.update_xaxes(gridcolor="rgba(120,90,50,.12)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(120,90,50,.12)", zeroline=False)
    return fig


def money(v: float) -> str:
    return f"NT$ {v:,.0f}"


def md_money(v: float) -> str:
    """money() escaped for st.markdown, so the ``$`` is not parsed as LaTeX."""
    return money(v).replace("$", r"\$")


@st.cache_data
def load_dataset() -> pd.DataFrame:
    """Load the synthetic dataset (or generate it on the fly if missing)."""
    csv = ROOT / "data" / "quotes_sample.csv"
    if csv.exists():
        return pd.read_csv(csv)
    return generate_dataset(n=800, seed=42)


st.markdown(
    """
    <div class="app-hero">
      <div class="app-hero__title">🏠 Renovation <span class="g">Quotation System</span></div>
      <div class="app-hero__rule"></div>
      <div class="app-hero__sub">Instant renovation quotes · rental-yield analysis · one-click Word/PDF proposals</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption("Portfolio demo · sample data only, not tied to any real company.")

# -- sidebar: survey inputs -----------------------------------------------
with st.sidebar:
    st.header("Building survey")
    project_name = st.text_input("Project name", "Demo Unit — Renovation")
    floor = st.number_input("Floor", min_value=1, max_value=40, value=5)
    has_elevator = st.checkbox("Has elevator", value=False)
    building_age = st.number_input("Building age (years)", min_value=0, max_value=100, value=38)
    condition = st.selectbox(
        "Condition",
        options=list(Condition),
        index=list(Condition).index(Condition.POOR),
        format_func=lambda c: c.value.title(),
    )
    supervision_rate = st.slider("Supervision fee", 0.0, 0.20, 0.10, step=0.01)

    st.header("Rental scenario")
    monthly_rent = st.number_input("Expected monthly rent", min_value=0, value=32000, step=1000)
    property_value = st.number_input("Property value (0 = renovation only)", min_value=0, value=0, step=100000)
    occupancy_rate = st.slider("Occupancy rate", 0.5, 1.0, 0.95, step=0.01)

# -- build the quotation from sample categories ---------------------------
difficulty = DifficultyMultiplier(
    floor=int(floor),
    has_elevator=has_elevator,
    building_age=int(building_age),
    condition=condition,
)
quote = Quotation(
    project_name=project_name,
    difficulty=difficulty,
    supervision_rate=supervision_rate,
)
for category in sample_categories():
    quote.add_category(category)

rental = RentalYieldCalculator(
    monthly_rent=monthly_rent,
    renovation_cost=quote.grand_total,
    property_value=property_value,
    occupancy_rate=occupancy_rate,
)
payback = "n/a" if rental.payback_months == float("inf") else f"{rental.payback_months:.1f} mo"

tab_quote, tab_whatif, tab_analytics = st.tabs(["📋 Quote", "🎚️ What-if", "📊 Analytics"])

# =========================================================================
# Tab 1 — Quote
# =========================================================================
with tab_quote:
    diff = difficulty.breakdown()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Difficulty", f"{diff['multiplier']:.2f}x")
    c2.metric("Grand total", money(quote.grand_total))
    c3.metric("Net annual yield", f"{rental.net_yield:.2%}")
    c4.metric("Payback", payback)

    st.divider()
    left, right = st.columns([3, 2])

    with left:
        st.subheader("Cost breakdown")
        for cat in quote.category_breakdown():
            with st.expander(f"{cat['display_name']} — {money(cat['subtotal'])}", expanded=False):
                st.caption(cat["description"])
                st.table(
                    [
                        {
                            "Item": it["name"],
                            "Qty": f"{it['quantity']:g} {it['unit']}",
                            "Unit price": money(it["unit_price"]),
                            "Amount": money(it["base_cost"]),
                        }
                        for it in cat["items"]
                    ]
                )
        st.markdown(
            f"**Trade subtotal:** {md_money(quote.trade_subtotal)}  \n"
            f"**Supervision fee ({supervision_rate:.0%}):** {md_money(quote.supervision_fee)}  \n"
            f"**Grand total:** {md_money(quote.grand_total)}"
        )

    with right:
        st.subheader("Rental yield analysis")
        ry = rental.as_dict()
        st.table(
            {
                "Metric": [
                    "Effective monthly rent",
                    "Total investment",
                    "Monthly net profit",
                    "Net annual yield",
                    "Payback period",
                ],
                "Value": [
                    money(ry["effective_monthly_rent"]),
                    money(ry["total_investment"]),
                    money(ry["monthly_net_profit"]),
                    f"{ry['net_yield']:.2%}",
                    payback,
                ],
            }
        )

    st.divider()
    st.subheader("Export proposal")
    out = ROOT / "output"
    col_docx, col_pdf = st.columns(2)
    with col_docx:
        if st.button("Generate Word (.docx)", use_container_width=True):
            path = generate_word(quote, out / "proposal.docx", rental)
            with open(path, "rb") as fh:
                st.download_button(
                    "Download .docx",
                    fh,
                    file_name="proposal.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
    with col_pdf:
        if st.button("Generate PDF (.pdf)", use_container_width=True):
            path = generate_pdf(quote, out / "proposal.pdf", rental)
            with open(path, "rb") as fh:
                st.download_button(
                    "Download .pdf",
                    fh,
                    file_name="proposal.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

# =========================================================================
# Tab 2 — What-if / sensitivity analysis
# =========================================================================
with tab_whatif:
    st.subheader("How sensitive is payback to rent & occupancy?")
    reno_cost = quote.grand_total
    st.caption(
        f"Holding the current quote fixed (renovation cost **{md_money(reno_cost)}**), "
        f"we sweep the rental assumptions around the base case "
        f"(rent {md_money(monthly_rent)}, occupancy {occupancy_rate:.0%})."
    )

    occ_grid = np.round(np.arange(0.70, 1.001, 0.05), 2)
    rent_grid = np.round(np.linspace(monthly_rent * 0.7, monthly_rent * 1.3, 13)).astype(int)

    def payback_for(rent: float, occ: float) -> float:
        calc = RentalYieldCalculator(
            monthly_rent=float(rent), renovation_cost=reno_cost, occupancy_rate=float(occ)
        )
        return calc.payback_months

    col_a, col_b = st.columns(2)
    with col_a:
        pay_occ = [payback_for(monthly_rent, o) for o in occ_grid]
        fig_o = px.line(
            x=occ_grid, y=pay_occ, markers=True,
            labels={"x": "Occupancy rate", "y": "Payback (months)"},
            title="Payback vs occupancy (at base rent)",
            color_discrete_sequence=[POP],
        )
        st.plotly_chart(_style_fig(fig_o), use_container_width=True)
    with col_b:
        pay_rent = [payback_for(r, occupancy_rate) for r in rent_grid]
        fig_r = px.line(
            x=rent_grid, y=pay_rent, markers=True,
            labels={"x": "Monthly rent (TWD)", "y": "Payback (months)"},
            title="Payback vs rent (at base occupancy)",
            color_discrete_sequence=[POP],
        )
        st.plotly_chart(_style_fig(fig_r), use_container_width=True)

    z = [[payback_for(r, o) for r in rent_grid] for o in occ_grid]
    fig_h = px.imshow(
        z, x=rent_grid, y=occ_grid, origin="lower", aspect="auto",
        color_continuous_scale="Teal",
        labels={"x": "Monthly rent (TWD)", "y": "Occupancy rate", "color": "Payback (mo)"},
        title="Payback months across rent × occupancy",
    )
    st.plotly_chart(_style_fig(fig_h), use_container_width=True)
    st.caption(
        "Lighter = faster payback (darker = longer). A steeper gradient along an "
        "axis means the investment case is more sensitive to that variable."
    )

# =========================================================================
# Tab 3 — Analytics (dataset explorer)
# =========================================================================
with tab_analytics:
    df = load_dataset()
    st.subheader("Synthetic dataset explorer")
    st.caption(f"{len(df):,} synthetic quotes generated by the same costing engine.")

    f1, f2 = st.columns([2, 3])
    conds = f1.multiselect("Condition", CONDITION_ORDER, default=CONDITION_ORDER)
    a_min, a_max = int(df["area_ping"].min()), int(df["area_ping"].max())
    area_range = f2.slider("Floor area (ping)", a_min, a_max, (a_min, a_max))

    d = df[df["condition"].isin(conds) & df["area_ping"].between(*area_range)]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Quotes", f"{len(d):,}")
    k2.metric("Avg total", money(d["grand_total"].mean()) if len(d) else "—")
    k3.metric("Avg net yield", f"{d['net_yield'].mean():.1%}" if len(d) else "—")
    k4.metric("Avg payback", f"{d['payback_months'].mean():.1f} mo" if len(d) else "—")

    if len(d):
        g1, g2 = st.columns(2)
        with g1:
            fig1 = px.histogram(d, x="grand_total", nbins=30, title="Total price distribution",
                                color_discrete_sequence=[POP])
            fig1.update_layout(showlegend=False)
            st.plotly_chart(_style_fig(fig1), use_container_width=True)
        with g2:
            fig2 = px.scatter(
                d, x="area_ping", y="grand_total", color="condition",
                category_orders={"condition": CONDITION_ORDER}, opacity=0.7,
                color_discrete_sequence=CAT_SEQ,
                title="Floor area vs total price",
            )
            st.plotly_chart(_style_fig(fig2), use_container_width=True)

        cost_cols = [c for c in df.columns if c.startswith("cost_")]
        means = d[cost_cols].mean().sort_values()
        means.index = [c.replace("cost_", "").title() for c in means.index]
        fig3 = px.bar(
            means, orientation="h",
            labels={"value": "Mean cost (TWD)", "index": "Category"},
            title="Average cost by trade category",
            color_discrete_sequence=[WARM],
        )
        fig3.update_layout(showlegend=False)
        st.plotly_chart(_style_fig(fig3), use_container_width=True)
    else:
        st.info("No quotes match the current filters.")
