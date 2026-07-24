"""Database engine / session setup (SQLAlchemy + PostgreSQL)."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/renovation_quote",
)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


def make_engine(url: str | None = None):
    """Create a SQLAlchemy engine. ``future=True`` uses the 2.0 style API."""
    return create_engine(url or DATABASE_URL, future=True)


# A module-level engine + session factory for convenience. The repository can
# also be pointed at a custom engine for tests.
engine = make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db(target_engine=None) -> None:
    """Create all tables. Safe to call repeatedly."""
    from . import schema  # noqa: F401  (register models on Base.metadata)

    Base.metadata.create_all(target_engine or engine)
