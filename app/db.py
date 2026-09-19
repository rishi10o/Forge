from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

# pool_pre_ping matters for the workers: they hold connections idle between jobs,
# long enough for Postgres or a proxy to drop them, and a dead connection would
# otherwise surface as a failed job rather than a reconnect.
#
# The pool has to be at least as wide as the number of threads that can demand a
# connection at once, or it becomes the system's concurrency limit. FastAPI runs
# sync handlers in a threadpool of ~40, and SQLAlchemy's default pool is 5 with 10
# overflow: at that ratio requests spend their time waiting for a checkout rather
# than for Postgres, and the API's measured latency is really the pool's queue.
#
# pool_size is the steady-state warm set; max_overflow is burst headroom created on
# demand. A worker only ever holds one session at a time, so it stays near the
# floor, which is what keeps a scaled-out pool from exhausting max_connections.
engine = create_engine(
    settings.DATABASE_URL,
    future=True,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT_SECONDS,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Iterator[Session]:
    """Yields one DB session per request, then closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope() -> Iterator[Session]:
    """Session for code outside a request, such as the worker loop.

    Rolls back on an exception so a failed unit of work cannot leave a
    half-applied transaction open on a long-lived connection.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
