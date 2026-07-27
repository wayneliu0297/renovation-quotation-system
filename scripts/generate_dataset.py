"""Write the synthetic quote dataset to data/quotes_sample.csv.

    python -m scripts.generate_dataset
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from renovation_quote.data.synthetic import generate_dataset


def main() -> None:
    df = generate_dataset(n=800, seed=42)
    out = Path(__file__).resolve().parent.parent / "data" / "quotes_sample.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"wrote {len(df)} rows x {df.shape[1]} cols -> {out}")


if __name__ == "__main__":
    main()
