"""Run the engine end-to-end with sample data. No database required.

    python -m scripts.demo
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make ``src`` importable when run directly.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from renovation_quote.data.sample_data import sample_quotation, sample_rental_yield
from renovation_quote.documents.pdf_generator import generate_pdf
from renovation_quote.documents.word_generator import generate_word


def _money(v: float) -> str:
    return f"NT$ {v:,.0f}"


def main() -> None:
    quote = sample_quotation()
    rental = sample_rental_yield(quote.grand_total)

    print(f"Project: {quote.project_name}")
    print(f"Difficulty multiplier: {quote.difficulty_value:.2f}x\n")

    for cat in quote.category_breakdown():
        print(f"  {cat['display_name']:<24} {_money(cat['subtotal'])}")

    print("-" * 44)
    print(f"  {'Trade subtotal':<24} {_money(quote.trade_subtotal)}")
    print(f"  {'Supervision fee':<24} {_money(quote.supervision_fee)}")
    print(f"  {'GRAND TOTAL':<24} {_money(quote.grand_total)}")

    print("\nRental yield:")
    print(f"  Monthly net profit  {_money(rental.monthly_net_profit)}")
    print(f"  Net annual yield    {rental.net_yield:.2%}")
    print(f"  Payback period      {rental.payback_months:.1f} months")

    out = Path(__file__).resolve().parent.parent / "output"
    docx_path = generate_word(quote, out / "sample_proposal.docx", rental)
    pdf_path = generate_pdf(quote, out / "sample_proposal.pdf", rental)
    print(f"\nGenerated:\n  {docx_path}\n  {pdf_path}")


if __name__ == "__main__":
    main()
