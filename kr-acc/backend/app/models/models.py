"""SQLAlchemy ORM models matching db/init.sql schema."""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Party(Base):
    __tablename__ = "parties"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    color_hex: Mapped[str | None] = mapped_column(String(7))
    assembly_term: Mapped[int] = mapped_column(Integer, default=22)


class Committee(Base):
    __tablename__ = "committees"

    id: Mapped[int] = mapped_column(primary_key=True)
    committee_id: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    committee_type: Mapped[str | None] = mapped_column(String(50))
    assembly_term: Mapped[int] = mapped_column(Integer, default=22)


class Politician(Base):
    __tablename__ = "politicians"

    id: Mapped[int] = mapped_column(primary_key=True)
    assembly_id: Mapped[str] = mapped_column(String(20), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    name_hanja: Mapped[str | None] = mapped_column(String(100))
    party: Mapped[str | None] = mapped_column(String(100))
    constituency: Mapped[str | None] = mapped_column(String(200))
    elected_count: Mapped[int | None] = mapped_column(Integer)
    committees: Mapped[dict | None] = mapped_column(JSONB)
    profile_url: Mapped[str | None] = mapped_column(Text)
    photo_url: Mapped[str | None] = mapped_column(Text)
    birth_date: Mapped[date | None] = mapped_column(Date)
    gender: Mapped[str | None] = mapped_column(String(10))
    assembly_term: Mapped[int] = mapped_column(Integer, default=22)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")

    sponsored_bills: Mapped[list["BillSponsor"]] = relationship(back_populates="politician")
    vote_records: Mapped[list["VoteRecord"]] = relationship(back_populates="politician")


class Bill(Base):
    __tablename__ = "bills"

    id: Mapped[int] = mapped_column(primary_key=True)
    bill_id: Mapped[str] = mapped_column(String(30), unique=True)
    bill_no: Mapped[str | None] = mapped_column(String(20))
    bill_name: Mapped[str] = mapped_column(Text)
    proposer_type: Mapped[str | None] = mapped_column(String(20))
    propose_date: Mapped[date | None] = mapped_column(Date)
    committee_id: Mapped[str | None] = mapped_column(String(50))
    committee_name: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[str | None] = mapped_column(String(50))
    result: Mapped[str | None] = mapped_column(String(50))
    assembly_term: Mapped[int] = mapped_column(Integer, default=22)
    detail_url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")

    sponsors: Mapped[list["BillSponsor"]] = relationship(back_populates="bill")
    votes: Mapped[list["Vote"]] = relationship(back_populates="bill")


class BillSponsor(Base):
    __tablename__ = "bill_sponsors"
    __table_args__ = (UniqueConstraint("bill_id", "politician_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    bill_id: Mapped[str] = mapped_column(String(30), ForeignKey("bills.bill_id"))
    politician_id: Mapped[int] = mapped_column(Integer, ForeignKey("politicians.id"))
    sponsor_type: Mapped[str | None] = mapped_column(String(20))

    bill: Mapped["Bill"] = relationship(back_populates="sponsors")
    politician: Mapped["Politician"] = relationship(back_populates="sponsored_bills")


class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(primary_key=True)
    vote_id: Mapped[str] = mapped_column(String(50), unique=True)
    bill_id: Mapped[str] = mapped_column(String(30), ForeignKey("bills.bill_id"))
    vote_date: Mapped[date] = mapped_column(Date)
    total_members: Mapped[int | None] = mapped_column(Integer)
    yes_count: Mapped[int | None] = mapped_column(Integer)
    no_count: Mapped[int | None] = mapped_column(Integer)
    abstain_count: Mapped[int | None] = mapped_column(Integer)
    absent_count: Mapped[int | None] = mapped_column(Integer)
    result: Mapped[str | None] = mapped_column(String(30))
    assembly_term: Mapped[int] = mapped_column(Integer, default=22)

    bill: Mapped["Bill"] = relationship(back_populates="votes")
    records: Mapped[list["VoteRecord"]] = relationship(back_populates="vote")


class VoteRecord(Base):
    __tablename__ = "vote_records"
    __table_args__ = (UniqueConstraint("vote_id", "politician_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    vote_id: Mapped[str] = mapped_column(String(50), ForeignKey("votes.vote_id"))
    politician_id: Mapped[int] = mapped_column(Integer, ForeignKey("politicians.id"))
    vote_result: Mapped[str | None] = mapped_column(String(10))

    vote: Mapped["Vote"] = relationship(back_populates="records")
    politician: Mapped["Politician"] = relationship(back_populates="vote_records")
