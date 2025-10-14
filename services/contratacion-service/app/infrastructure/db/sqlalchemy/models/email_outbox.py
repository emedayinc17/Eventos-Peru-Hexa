# services/contratacion-service/app/infrastructure/db/sqlalchemy/models/email_outbox.py
from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, SmallInteger, DateTime, JSON, text

# Si ya usas un Base compartido, impórtalo en lugar de esta clase local:
# from ev_shared.db import Base as SharedBase
# class Base(SharedBase): pass
class Base(DeclarativeBase):
    pass

class EmailOutbox(Base):
    __tablename__ = "email_outbox"
    __table_args__ = {"schema": "ev_mensajeria"}

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    to_email: Mapped[str] = mapped_column(String(200), nullable=False)
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(String(2**16), nullable=False)  # MEDIUMTEXT aprox
    template: Mapped[Optional[str]] = mapped_column(String(80))
    payload_json: Mapped[Optional[dict]] = mapped_column(JSON)
    status: Mapped[int] = mapped_column(SmallInteger, server_default=text("0"))   # 0=PEND,1=ENVIADO,2=ERROR,3=REINTENTO
    attempts: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    last_attempt_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    error_msg: Mapped[Optional[str]] = mapped_column(String(500))
    correlation_id: Mapped[Optional[str]] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    created_by: Mapped[Optional[str]] = mapped_column(String(36))
