"""
ev_shared.db
------------
SQLAlchemy Engine / Session helpers.
Synopsis: created by emeday 2025
"""
from contextlib import contextmanager
import time
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
from .config import Settings

def build_engine(settings: Settings) -> Engine:
    """Crea un Engine de SQLAlchemy desde Settings"""
    return create_engine(settings.DATABASE_URL, pool_pre_ping=True, pool_recycle=300)

def make_session_factory(engine: Engine):
    """Crea un sessionmaker desde un Engine"""
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)

@contextmanager
def session_scope(settings: Settings):
    """
    Context manager para sesiones de SQLAlchemy.
    Ahora acepta Settings directamente y crea el engine y session internamente.
    
    Uso:
        with session_scope(settings) as session:
            result = session.execute(...)
    """
    engine = build_engine(settings)
    # Intentar conectar al DB con reintentos cortos antes de crear la sesión
    retries = getattr(settings, "DB_CONN_RETRIES", 1)
    delay = getattr(settings, "DB_CONN_RETRY_DELAY", 1)
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            # force a connection check
            conn = engine.connect()
            conn.close()
            last_exc = None
            break
        except OperationalError as e:
            last_exc = e
            time.sleep(delay)

    if last_exc is not None:
        # No pudimos conectar al DB
        raise last_exc

    SessionFactory = make_session_factory(engine)
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
        engine.dispose()
