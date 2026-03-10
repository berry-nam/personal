"""SQLAlchemy ORM models matching db/init.sql schema."""

from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
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
    eng_name: Mapped[str | None] = mapped_column(String(100))
    bio: Mapped[str | None] = mapped_column(Text)
    email: Mapped[str | None] = mapped_column(String(200))
    homepage: Mapped[str | None] = mapped_column(Text)
    office_address: Mapped[str | None] = mapped_column(String(300))
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


# ── Asset Declarations (재산공개) ─────────────────────────────────────────────


class AssetDeclaration(Base):
    __tablename__ = "asset_declarations"
    __table_args__ = (UniqueConstraint("politician_id", "report_year"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    politician_id: Mapped[int] = mapped_column(Integer, ForeignKey("politicians.id"))
    report_year: Mapped[int] = mapped_column(Integer)
    total_assets: Mapped[int | None] = mapped_column(BigInteger)
    total_real_estate: Mapped[int | None] = mapped_column(BigInteger)
    total_deposits: Mapped[int | None] = mapped_column(BigInteger)
    total_securities: Mapped[int | None] = mapped_column(BigInteger)
    total_crypto: Mapped[int | None] = mapped_column(BigInteger)
    source: Mapped[str | None] = mapped_column(String(50))
    raw_data: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")

    politician: Mapped["Politician"] = relationship()
    items: Mapped[list["AssetItem"]] = relationship(back_populates="declaration", cascade="all, delete-orphan")


class AssetItem(Base):
    __tablename__ = "asset_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    declaration_id: Mapped[int] = mapped_column(Integer, ForeignKey("asset_declarations.id", ondelete="CASCADE"))
    category: Mapped[str] = mapped_column(String(50))
    subcategory: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    relation: Mapped[str | None] = mapped_column(String(20))
    value_krw: Mapped[int | None] = mapped_column(BigInteger)
    change_krw: Mapped[int | None] = mapped_column(BigInteger)
    note: Mapped[str | None] = mapped_column(Text)

    declaration: Mapped["AssetDeclaration"] = relationship(back_populates="items")


# ── Companies (기업) ──────────────────────────────────────────────────────────


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    corp_code: Mapped[str | None] = mapped_column(String(20), unique=True)
    corp_name: Mapped[str] = mapped_column(String(200))
    stock_code: Mapped[str | None] = mapped_column(String(20))
    industry: Mapped[str | None] = mapped_column(String(200))
    ceo_name: Mapped[str | None] = mapped_column(String(100))
    homepage: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")


class PoliticianCompany(Base):
    __tablename__ = "politician_companies"
    __table_args__ = (UniqueConstraint("politician_id", "company_id", "relation_type", "source_year"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    politician_id: Mapped[int] = mapped_column(Integer, ForeignKey("politicians.id"))
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"))
    relation_type: Mapped[str] = mapped_column(String(50))
    detail: Mapped[str | None] = mapped_column(Text)
    value_krw: Mapped[int | None] = mapped_column(BigInteger)
    source: Mapped[str | None] = mapped_column(String(50))
    source_year: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")

    politician: Mapped["Politician"] = relationship()
    company: Mapped["Company"] = relationship()


# ── Political Funds (정치자금) ────────────────────────────────────────────────


class PoliticalFund(Base):
    __tablename__ = "political_funds"
    __table_args__ = (UniqueConstraint("politician_id", "fund_year", "fund_type"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    politician_id: Mapped[int] = mapped_column(Integer, ForeignKey("politicians.id"))
    fund_year: Mapped[int] = mapped_column(Integer)
    fund_type: Mapped[str | None] = mapped_column(String(50))
    income_total: Mapped[int | None] = mapped_column(BigInteger)
    expense_total: Mapped[int | None] = mapped_column(BigInteger)
    balance: Mapped[int | None] = mapped_column(BigInteger)
    source: Mapped[str | None] = mapped_column(String(50))
    raw_data: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")

    politician: Mapped["Politician"] = relationship()
    items: Mapped[list["PoliticalFundItem"]] = relationship(back_populates="fund", cascade="all, delete-orphan")


class PoliticalFundItem(Base):
    __tablename__ = "political_fund_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    fund_id: Mapped[int] = mapped_column(Integer, ForeignKey("political_funds.id", ondelete="CASCADE"))
    item_type: Mapped[str] = mapped_column(String(20))
    category: Mapped[str | None] = mapped_column(String(100))
    counterpart: Mapped[str | None] = mapped_column(String(200))
    amount: Mapped[int] = mapped_column(BigInteger)
    item_date: Mapped[date | None] = mapped_column(Date)
    note: Mapped[str | None] = mapped_column(Text)

    fund: Mapped["PoliticalFund"] = relationship(back_populates="items")
