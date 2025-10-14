"""
ev_shared.db
------------
SQLAlchemy Engine / Session helpers.
Synopsis: created by emeday 2025
"""
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
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
