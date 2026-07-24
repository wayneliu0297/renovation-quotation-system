"""QuoteRepository: save and retrieve quotes from PostgreSQL."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..calculators.quotation import Quotation
from ..calculators.rental_yield import RentalYieldCalculator
from .database import SessionLocal
from .schema import QuoteRecord


class QuoteRepository:
    """Data-access object for :class:`QuoteRecord`.

    Pass a custom ``session_factory`` (e.g. bound to a test engine) or rely on
    the default module-level ``SessionLocal``.
    """

    def __init__(self, session_factory=SessionLocal) -> None:
        self._session_factory = session_factory

    def _session(self) -> Session:
        return self._session_factory()

    # -- write -------------------------------------------------------------
    def save(
        self,
        quote: Quotation,
        rental: RentalYieldCalculator | None = None,
    ) -> int:
        """Persist a quote (plus optional rental analysis) and return its id."""
        payload = {"quotation": quote.as_dict()}
        if rental is not None:
            payload["rental_yield"] = rental.as_dict()

        record = QuoteRecord(
            project_name=quote.project_name,
            difficulty=quote.difficulty_value,
            trade_subtotal=quote.trade_subtotal,
            supervision_fee=quote.supervision_fee,
            grand_total=quote.grand_total,
            payload=payload,
        )
        with self._session() as session:
            session.add(record)
            session.commit()
            session.refresh(record)
            return record.id

    # -- read --------------------------------------------------------------
    def get(self, quote_id: int) -> QuoteRecord | None:
        with self._session() as session:
            return session.get(QuoteRecord, quote_id)

    def list_recent(self, limit: int = 20) -> list[QuoteRecord]:
        stmt = select(QuoteRecord).order_by(QuoteRecord.created_at.desc()).limit(limit)
        with self._session() as session:
            return list(session.scalars(stmt))
