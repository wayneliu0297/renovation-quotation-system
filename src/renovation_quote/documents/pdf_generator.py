"""Generate a .pdf renovation proposal from a Quotation (reportlab)."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from ..calculators.quotation import Quotation
from ..calculators.rental_yield import RentalYieldCalculator


def _money(value: float) -> str:
    return f"NT$ {value:,.0f}"


def _category_table(cat: dict) -> Table:
    data = [["Item", "Qty", "Unit price", "Amount"]]
    for item in cat["items"]:
        data.append(
            [
                item["name"],
                f"{item['quantity']:g} {item['unit']}",
                _money(item["unit_price"]),
                _money(item["base_cost"]),
            ]
        )
    data.append(["", "", f"Subtotal (x{cat['multiplier']:.2f})", _money(cat["subtotal"])])

    table = Table(data, colWidths=[80 * mm, 25 * mm, 32 * mm, 32 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("GRID", (0, 0), (-1, -2), 0.4, colors.HexColor("#E5E7EB")),
                ("LINEABOVE", (0, -1), (-1, -1), 0.6, colors.HexColor("#111827")),
                ("FONTNAME", (2, -1), (-1, -1), "Helvetica-Bold"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return table


def generate_pdf(
    quote: Quotation,
    output_path: str | Path,
    rental: RentalYieldCalculator | None = None,
) -> Path:
    """Render ``quote`` to a PDF document at ``output_path``."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
    )

    story: list = []
    story.append(Paragraph("Renovation Proposal", styles["Title"]))
    story.append(Paragraph(quote.project_name, styles["Heading2"]))

    diff = quote.difficulty.breakdown()
    story.append(
        Paragraph(
            f"Difficulty multiplier: <b>{diff['multiplier']:.2f}x</b> "
            f"(floor +{diff['floor_factor']:.2f}, age +{diff['age_factor']:.2f}, "
            f"condition +{diff['condition_factor']:.2f})",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 6 * mm))

    for cat in quote.category_breakdown():
        story.append(Paragraph(cat["display_name"], styles["Heading3"]))
        story.append(Paragraph(cat["description"], styles["Italic"]))
        story.append(Spacer(1, 2 * mm))
        story.append(_category_table(cat))
        story.append(Spacer(1, 5 * mm))

    # -- summary -----------------------------------------------------------
    summary_data = [
        ["Trade subtotal", _money(quote.trade_subtotal)],
        [f"Supervision fee ({quote.supervision_rate:.0%})", _money(quote.supervision_fee)],
        ["Grand total", _money(quote.grand_total)],
    ]
    summary = Table(summary_data, colWidths=[137 * mm, 32 * mm])
    summary.setStyle(
        TableStyle(
            [
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("LINEABOVE", (0, -1), (-1, -1), 0.8, colors.HexColor("#111827")),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(Paragraph("Summary", styles["Heading2"]))
    story.append(summary)

    # -- rental yield ------------------------------------------------------
    if rental is not None:
        ry = rental.as_dict()
        story.append(Spacer(1, 6 * mm))
        story.append(Paragraph("Rental Yield Analysis", styles["Heading2"]))
        payback = (
            "n/a"
            if ry["payback_months"] == float("inf")
            else f"{ry['payback_months']:.1f} months"
        )
        ry_data = [
            ["Expected monthly rent", _money(ry["monthly_rent"])],
            ["Effective monthly rent", _money(ry["effective_monthly_rent"])],
            ["Total investment", _money(ry["total_investment"])],
            ["Monthly net profit", _money(ry["monthly_net_profit"])],
            ["Net annual yield", f"{ry['net_yield']:.2%}"],
            ["Payback period", payback],
        ]
        ry_table = Table(ry_data, colWidths=[137 * mm, 32 * mm])
        ry_table.setStyle(
            TableStyle(
                [
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#E5E7EB")),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )
        story.append(ry_table)

    story.append(Spacer(1, 10 * mm))
    story.append(
        Paragraph(
            "<font size=7>Demo document — sample data only, not a binding quote.</font>",
            styles["Normal"],
        )
    )

    doc.build(story)
    return output_path
