"""Streamlit UI for the Renovation Quotation System (portfolio demo).

    streamlit run app/streamlit_app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Make ``src`` importable when Streamlit runs this file directly.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from renovation_quote.calculators.quotation import Quotation
from renovation_quote.calculators.rental_yield import RentalYieldCalculator
from renovation_quote.data.sample_data import sample_categories
from renovation_quote.documents.pdf_generator import generate_pdf
from renovation_quote.documents.word_generator import generate_word
from renovation_quote.models.difficulty import Condition, DifficultyMultiplier

st.set_page_config(page_title="Renovation Quotation System", page_icon="🏠", layout="wide")


def money(v: float) -> str:
    return f"NT$ {v:,.0f}"


st.title("🏠 Renovation Quotation System")
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

# -- headline metrics ------------------------------------------------------
diff = difficulty.breakdown()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Difficulty", f"{diff['multiplier']:.2f}x")
c2.metric("Grand total", money(quote.grand_total))
c3.metric("Net annual yield", f"{rental.net_yield:.2%}")
payback = "n/a" if rental.payback_months == float("inf") else f"{rental.payback_months:.1f} mo"
c4.metric("Payback", payback)

st.divider()

# -- category breakdown ----------------------------------------------------
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
        f"**Trade subtotal:** {money(quote.trade_subtotal)}  \n"
        f"**Supervision fee ({supervision_rate:.0%}):** {money(quote.supervision_fee)}  \n"
        f"**Grand total:** {money(quote.grand_total)}"
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

# -- document export -------------------------------------------------------
st.divider()
st.subheader("Export proposal")
out = Path(__file__).resolve().parent.parent / "output"

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
