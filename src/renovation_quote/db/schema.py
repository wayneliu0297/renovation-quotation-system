"""ORM tables for persisted quotes.

The quote itself is stored as a header row plus a JSON snapshot of the fully
computed breakdown, which keeps the demo simple while still being queryable.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class QuoteRecord(Base):
    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_name: Mapped[str] = mapped_column(String(200), nullable=False)
    difficulty: Mapped[float] = mapped_column(Float, nullable=False)
    trade_subtotal: Mapped[float] = mapped_column(Float, nullable=False)
    supervision_fee: Mapped[float] = mapped_column(Float, nullable=False)
    grand_total: Mapped[float] = mapped_column(Float, nullable=False)
    #: Full computed breakdown (categories + rental yield) as a JSON snapshot.
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<QuoteRecord id={self.id} project={self.project_name!r} total={self.grand_total:.0f}>"
