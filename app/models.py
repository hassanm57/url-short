from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Url(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    original: Mapped[str] = mapped_column(String, nullable=False)
    short_code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    # nullable=True means expiry is optional — links without it never expire
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # One Url can have many Clicks. `back_populates` links the two sides of the relationship.
    clicks: Mapped[list["Click"]] = relationship("Click", back_populates="url")

    # Explicit index so PostgreSQL can look up a short_code in O(log n) instead of a full table scan
    __table_args__ = (Index("ix_urls_short_code", "short_code"),)


class Click(Base):
    __tablename__ = "clicks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url_id: Mapped[int] = mapped_column(Integer, ForeignKey("urls.id"), nullable=False)
    clicked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)  # 45 covers IPv6

    url: Mapped["Url"] = relationship("Url", back_populates="clicks")
