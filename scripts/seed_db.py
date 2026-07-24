"""Create tables and insert a sample quote into PostgreSQL.

    python -m scripts.seed_db

Requires a reachable database (see .env / DATABASE_URL).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from renovation_quote.data.sample_data import sample_quotation, sample_rental_yield
from renovation_quote.db.database import init_db
from renovation_quote.db.repository import QuoteRepository


def main() -> None:
    print("Creating tables ...")
    init_db()

    quote = sample_quotation()
    rental = sample_rental_yield(quote.grand_total)

    repo = QuoteRepository()
    quote_id = repo.save(quote, rental)
    print(f"Saved sample quote with id={quote_id}")

    print("\nRecent quotes:")
    for record in repo.list_recent(limit=5):
        print(f"  #{record.id}  {record.project_name}  NT$ {record.grand_total:,.0f}")


if __name__ == "__main__":
    main()
