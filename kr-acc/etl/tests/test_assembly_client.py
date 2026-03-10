"""Tests for the Assembly API client."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from assembly_client import (
    LEGISLATORS,
    AssemblyAPIError,
    AssemblyClient,
    RawBill,
    RawBillReview,
    RawCommittee,
    RawLegislator,
    RawVotePerMember,
    RawVoteSummary,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────


def _make_api_response(endpoint: str, rows: list[dict], total: int) -> dict:
    """Build a mock Assembly API JSON response."""
    return {
        endpoint: [
            {"head": [{"list_total_count": total}, {"RESULT": {"CODE": "INFO-000"}}]},
            {"row": rows},
        ]
    }


def _make_empty_response(endpoint: str) -> dict:
    return {endpoint: [{"head": [{"list_total_count": 0}]}]}


FAKE_KEY = "test_api_key_123"


# ── Unit tests: response parsing ──────────────────────────────────────────────


class TestParseResponse:
    def test_parse_normal_response(self):
        rows = [{"HG_NM": "김철수", "POLY_NM": "국민의힘"}]
        data = _make_api_response(LEGISLATORS, rows, 1)
        result_rows, total = AssemblyClient._parse_response(data, LEGISLATORS)
        assert result_rows == rows
        assert total == 1

    def test_parse_empty_response(self):
        data = _make_empty_response(LEGISLATORS)
        rows, total = AssemblyClient._parse_response(data, LEGISLATORS)
        assert rows == []
        assert total == 0

    def test_parse_missing_endpoint(self):
        rows, total = AssemblyClient._parse_response({}, LEGISLATORS)
        assert rows == []
        assert total == 0

    def test_parse_multi_page_total(self):
        rows = [{"HG_NM": "이영희"}]
        data = _make_api_response(LEGISLATORS, rows, 300)
        result_rows, total = AssemblyClient._parse_response(data, LEGISLATORS)
        assert total == 300
        assert len(result_rows) == 1


# ── Unit tests: fetch with mocked HTTP ───────────────────────────────────────


class TestFetch:
    @staticmethod
    def _make_mock_response(json_data: dict) -> MagicMock:
        """Create a mock httpx.Response (json() is sync in httpx)."""
        resp = MagicMock()
        resp.status_code = 200
        resp.raise_for_status = MagicMock()
        resp.json.return_value = json_data
        return resp

    @pytest.mark.asyncio
    async def test_fetch_single_page(self):
        rows = [{"HG_NM": "김철수", "MONA_CD": "ABC123"}]
        mock_resp = self._make_mock_response(_make_api_response(LEGISLATORS, rows, 1))

        async with AssemblyClient(api_key=FAKE_KEY, rate_limit=100) as client:
            client._client.get = AsyncMock(return_value=mock_resp)
            result = await client.fetch(LEGISLATORS, params={"AGE": "22"})

        assert len(result) == 1
        assert result[0]["HG_NM"] == "김철수"

    @pytest.mark.asyncio
    async def test_fetch_all_pagination(self):
        page1_rows = [{"id": i} for i in range(100)]
        page2_rows = [{"id": i} for i in range(100, 150)]

        call_count = 0

        async def mock_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return self._make_mock_response(
                    _make_api_response(LEGISLATORS, page1_rows, 150)
                )
            return self._make_mock_response(
                _make_api_response(LEGISLATORS, page2_rows, 150)
            )

        async with AssemblyClient(api_key=FAKE_KEY, rate_limit=100) as client:
            client._client.get = mock_get
            result = await client.fetch_all(LEGISLATORS, params={"AGE": "22"})

        assert len(result) == 150
        assert call_count == 2


# ── Unit tests: Pydantic models ──────────────────────────────────────────────


class TestModels:
    def test_raw_legislator_defaults(self):
        leg = RawLegislator()
        assert leg.HG_NM == ""
        assert leg.MONA_CD == ""

    def test_raw_legislator_from_dict(self):
        data = {"HG_NM": "박민수", "POLY_NM": "더불어민주당", "MONA_CD": "XYZ"}
        leg = RawLegislator(**data)
        assert leg.HG_NM == "박민수"
        assert leg.POLY_NM == "더불어민주당"

    def test_raw_legislator_extra_fields_ignored(self):
        data = {"HG_NM": "홍길동", "UNKNOWN_FIELD": "value"}
        leg = RawLegislator.model_validate(data)
        assert leg.HG_NM == "홍길동"

    def test_raw_bill(self):
        data = {"BILL_ID": "PRC_B1234", "BILL_NAME": "테스트법안", "PROPOSER": "김철수의원 외 10인"}
        bill = RawBill(**data)
        assert bill.BILL_ID == "PRC_B1234"
        assert "김철수" in bill.PROPOSER

    def test_raw_vote_summary(self):
        data = {"BILL_ID": "PRC_V1", "YES_TCNT": "180", "NO_TCNT": "50", "RESULT": "가결"}
        vote = RawVoteSummary(**data)
        assert vote.YES_TCNT == "180"
        assert vote.RESULT == "가결"

    def test_raw_vote_per_member(self):
        data = {"HG_NM": "이영희", "RESULT_VOTE_MOD": "찬성", "POLY_NM": "국민의힘"}
        record = RawVotePerMember(**data)
        assert record.RESULT_VOTE_MOD == "찬성"

    def test_raw_committee(self):
        data = {"CURR_COMMITTEE_ID": "C001", "CURR_COMMITTEE": "기획재정위원회"}
        comm = RawCommittee(**data)
        assert comm.CURR_COMMITTEE == "기획재정위원회"

    def test_raw_bill_review(self):
        data = {"BILL_ID": "PRC_R1", "PLENARY_PROC_RESULT": "원안가결"}
        review = RawBillReview(**data)
        assert review.PLENARY_PROC_RESULT == "원안가결"


# ── Integration tests (require network + valid API key) ───────────────────────

INTEGRATION_KEY = "fbfdf6945fea48e8837c8cd8b60e89f2"


@pytest.mark.integration
class TestIntegration:
    """Integration tests that call the real API.

    Run with: pytest -m integration
    Requires network access and valid ASSEMBLY_API_KEY.
    """

    @pytest.mark.asyncio
    async def test_fetch_legislators(self):
        async with AssemblyClient(api_key=INTEGRATION_KEY) as client:
            rows = await client.fetch(LEGISLATORS, params={"AGE": "22"}, size=5)
        assert len(rows) > 0
        leg = RawLegislator(**rows[0])
        assert leg.HG_NM != ""

    @pytest.mark.asyncio
    async def test_fetch_all_legislators(self):
        async with AssemblyClient(api_key=INTEGRATION_KEY) as client:
            rows = await client.fetch_all(LEGISLATORS, params={"AGE": "22"})
        # 22nd Assembly should have ~300 members
        assert len(rows) >= 200

    @pytest.mark.asyncio
    async def test_fetch_committees(self):
        from assembly_client import COMMITTEES

        async with AssemblyClient(api_key=INTEGRATION_KEY) as client:
            rows = await client.fetch(COMMITTEES, size=10)
        assert len(rows) > 0
        comm = RawCommittee(**rows[0])
        assert comm.CURR_COMMITTEE != ""
