"""Tests for ETL transform tasks."""

from datetime import date

import pytest

from tasks.transform import (
    _parse_date,
    _parse_elected_count,
    _safe_int,
    parse_sponsors,
    transform_bills,
    transform_committees,
    transform_legislators,
    transform_vote_members,
    transform_vote_summaries,
)


# ── Helper function tests ────────────────────────────────────────────────────


class TestParseDate:
    def test_yyyymmdd(self):
        assert _parse_date("19800315") == date(1980, 3, 15)

    def test_yyyy_mm_dd(self):
        assert _parse_date("1980-03-15") == date(1980, 3, 15)

    def test_empty(self):
        assert _parse_date("") is None

    def test_none_like(self):
        assert _parse_date("  ") is None

    def test_invalid(self):
        assert _parse_date("not-a-date") is None


class TestSafeInt:
    def test_valid(self):
        assert _safe_int("42") == 42

    def test_empty(self):
        assert _safe_int("") is None

    def test_whitespace(self):
        assert _safe_int(" 100 ") == 100

    def test_invalid(self):
        assert _safe_int("abc") is None


class TestParseElectedCount:
    def test_first_term(self):
        assert _parse_elected_count("초선") == 1

    def test_second_term(self):
        assert _parse_elected_count("재선") == 2

    def test_third_term(self):
        assert _parse_elected_count("3선") == 3

    def test_empty(self):
        assert _parse_elected_count("") is None


# ── Sponsor parsing tests ────────────────────────────────────────────────────


class TestParseSponsors:
    def test_simple_proposer(self):
        result = parse_sponsors.fn("김철수의원 외 10인")
        assert len(result) == 1
        assert result[0]["name"] == "김철수"
        assert result[0]["sponsor_type"] == "primary"

    def test_multiple_sponsors(self):
        result = parse_sponsors.fn("김철수의원(대표발의), 이영희의원, 박민수의원")
        assert len(result) == 3
        assert result[0]["name"] == "김철수"
        assert result[0]["sponsor_type"] == "primary"
        assert result[1]["sponsor_type"] == "co-sponsor"
        assert result[2]["sponsor_type"] == "co-sponsor"

    def test_explicit_primary(self):
        result = parse_sponsors.fn(
            "김철수의원, 이영희의원, 박민수의원",
            primary_proposer="이영희의원",
        )
        assert len(result) == 3
        kim = next(r for r in result if r["name"] == "김철수")
        lee = next(r for r in result if r["name"] == "이영희")
        assert lee["sponsor_type"] == "primary"
        assert kim["sponsor_type"] == "co-sponsor"

    def test_empty_proposer(self):
        assert parse_sponsors.fn("") == []

    def test_no_matches(self):
        assert parse_sponsors.fn("정부제출") == []

    def test_deduplication(self):
        result = parse_sponsors.fn("김철수의원, 김철수의원, 이영희의원")
        names = [r["name"] for r in result]
        assert names == ["김철수", "이영희"]

    def test_primary_via_bracket(self):
        result = parse_sponsors.fn("홍길동의원(대표발의), 김영수의원")
        assert result[0]["name"] == "홍길동"
        assert result[0]["sponsor_type"] == "primary"


# ── Transform task tests ─────────────────────────────────────────────────────


class TestTransformLegislators:
    def test_basic_transform(self):
        raw = [{
            "HG_NM": "김철수",
            "HJ_NM": "金哲洙",
            "POLY_NM": "국민의힘",
            "ORIG_NM": "서울 강남구갑",
            "REELE_GBN_NM": "초선",
            "CMITS": "기획재정위원회, 예산결산특별위원회",
            "MONA_CD": "ABC123",
            "LINK_URL": "https://example.com",
            "BTH_DATE": "19800315",
            "SEX_GBN_NM": "남",
        }]
        result = transform_legislators.fn(raw)
        assert len(result) == 1
        r = result[0]
        assert r["assembly_id"] == "ABC123"
        assert r["name"] == "김철수"
        assert r["party"] == "국민의힘"
        assert r["elected_count"] == 1
        assert r["committees"] == ["기획재정위원회", "예산결산특별위원회"]
        assert r["birth_date"] == date(1980, 3, 15)

    def test_skip_missing_id(self):
        raw = [{"HG_NM": "이영희", "MONA_CD": ""}]
        result = transform_legislators.fn(raw)
        assert len(result) == 0

    def test_skip_missing_name(self):
        raw = [{"HG_NM": "", "MONA_CD": "XYZ"}]
        result = transform_legislators.fn(raw)
        assert len(result) == 0


class TestTransformBills:
    def test_basic_transform(self):
        raw = [{
            "BILL_ID": "PRC_B2400001",
            "BILL_NO": "2400001",
            "BILL_NAME": "테스트법안",
            "PROPOSER": "김철수의원 외 10인",
            "PROPOSER_KIND": "의원",
            "PROPOSE_DT": "20240601",
            "COMMITTEE_ID": "C001",
            "COMMITTEE": "기획재정위원회",
            "PROC_RESULT": "원안가결",
            "DETAIL_LINK": "https://example.com/bill",
            "RST_PROPOSER": "김철수의원",
        }]
        result = transform_bills.fn(raw)
        assert len(result) == 1
        r = result[0]
        assert r["bill_id"] == "PRC_B2400001"
        assert r["propose_date"] == date(2024, 6, 1)
        assert r["_raw_proposer"] == "김철수의원 외 10인"

    def test_skip_missing_bill_id(self):
        raw = [{"BILL_ID": "", "BILL_NAME": "법안"}]
        result = transform_bills.fn(raw)
        assert len(result) == 0


class TestTransformVoteSummaries:
    def test_basic_transform(self):
        raw = [{
            "BILL_ID": "PRC_V001",
            "VOTE_DATE": "20240615",
            "BILL_NAME": "투표법안",
            "MEMBER_TCNT": "300",
            "YES_TCNT": "200",
            "NO_TCNT": "50",
            "BLANK_TCNT": "10",
            "ABSENT_TCNT": "40",
            "RESULT": "가결",
        }]
        result = transform_vote_summaries.fn(raw)
        assert len(result) == 1
        r = result[0]
        assert r["vote_id"] == "PRC_V001_20240615"
        assert r["yes_count"] == 200
        assert r["result"] == "가결"


class TestTransformVoteMembers:
    def test_basic_transform(self):
        raw = [{
            "BILL_ID": "PRC_V001",
            "HG_NM": "김철수",
            "POLY_NM": "국민의힘",
            "ORIG_NM": "서울 강남구갑",
            "RESULT_VOTE_MOD": "찬성",
            "VOTE_DATE": "20240615",
        }]
        result = transform_vote_members.fn(raw, "PRC_V001_20240615")
        assert len(result) == 1
        assert result[0]["_politician_name"] == "김철수"
        assert result[0]["vote_result"] == "찬성"
        assert result[0]["vote_id"] == "PRC_V001_20240615"


class TestTransformCommittees:
    def test_basic_transform(self):
        raw = [
            {"CURR_COMMITTEE_ID": "C001", "CURR_COMMITTEE": "기획재정위원회", "COMMITTEE_TYPE": "상임"},
            {"CURR_COMMITTEE_ID": "C001", "CURR_COMMITTEE": "기획재정위원회", "COMMITTEE_TYPE": "상임"},
            {"CURR_COMMITTEE_ID": "C002", "CURR_COMMITTEE": "외교통일위원회", "COMMITTEE_TYPE": "상임"},
        ]
        result = transform_committees.fn(raw)
        # Should deduplicate
        assert len(result) == 2
        ids = {r["committee_id"] for r in result}
        assert ids == {"C001", "C002"}
