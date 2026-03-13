"""Test Pydantic schema validation."""

from datetime import date

import pytest

from app.schemas.schemas import (
    BillSummary,
    GraphData,
    GraphEdge,
    GraphNode,
    NeighborOut,
    PaginatedResponse,
    PartyOut,
    PoliticianDetail,
    PoliticianStats,
    PoliticianSummary,
    VoteSummary,
)


class TestPoliticianSchemas:
    def test_politician_summary(self):
        data = PoliticianSummary(
            id=1,
            assembly_id="ABC123",
            name="김철수",
            party="국민의힘",
            constituency="서울 강남구갑",
            elected_count=2,
            photo_url=None,
            assembly_term=22,
        )
        assert data.name == "김철수"
        assert data.party == "국민의힘"

    def test_politician_detail(self):
        data = PoliticianDetail(
            id=1,
            assembly_id="ABC123",
            name="김철수",
            name_hanja="金哲洙",
            party="국민의힘",
            constituency="서울 강남구갑",
            elected_count=2,
            committees=["기획재정위원회"],
            profile_url=None,
            photo_url=None,
            eng_name=None,
            bio=None,
            email=None,
            homepage=None,
            office_address=None,
            birth_date=date(1980, 3, 15),
            gender="남",
            assembly_term=22,
        )
        assert data.committees == ["기획재정위원회"]
        assert data.birth_date == date(1980, 3, 15)

    def test_politician_stats(self):
        stats = PoliticianStats(
            total_votes=100,
            yes_count=80,
            no_count=10,
            abstain_count=5,
            absent_count=5,
            participation_rate=95.0,
            bills_sponsored=50,
            bills_primary_sponsored=10,
        )
        assert stats.participation_rate == 95.0


class TestBillSchemas:
    def test_bill_summary(self):
        data = BillSummary(
            id=1,
            bill_id="PRC_B001",
            bill_no="2400001",
            bill_name="테스트법안",
            proposer_type="의원",
            propose_date=date(2024, 6, 1),
            committee_name="기획재정위원회",
            result="원안가결",
        )
        assert data.bill_name == "테스트법안"


class TestVoteSchemas:
    def test_vote_summary(self):
        data = VoteSummary(
            id=1,
            vote_id="V001_20240615",
            bill_id="PRC_B001",
            bill_name="투표법안",
            vote_date=date(2024, 6, 15),
            total_members=300,
            yes_count=200,
            no_count=50,
            abstain_count=10,
            absent_count=40,
            result="가결",
        )
        assert data.yes_count == 200


class TestGraphSchemas:
    def test_graph_data(self):
        data = GraphData(
            nodes=[
                GraphNode(id="A001", name="김철수", party="국민의힘", group="국민의힘"),
                GraphNode(id="A002", name="이영희", party="더불어민주당", group="더불어민주당"),
            ],
            edges=[
                GraphEdge(source="A001", target="A002", weight=5),
            ],
        )
        assert len(data.nodes) == 2
        assert data.edges[0].weight == 5

    def test_neighbor_out(self):
        data = NeighborOut(
            assembly_id="A002",
            name="이영희",
            party="더불어민주당",
            weight=10,
        )
        assert data.weight == 10


class TestPaginatedResponse:
    def test_paginated(self):
        data = PaginatedResponse(items=[], total=0, page=1, size=20, pages=0)
        assert data.pages == 0

    def test_with_items(self):
        data = PaginatedResponse(
            items=[{"id": 1}],
            total=100,
            page=3,
            size=20,
            pages=5,
        )
        assert data.page == 3
        assert data.total == 100


class TestPartySchema:
    def test_party_out(self):
        data = PartyOut(id=1, name="국민의힘", color_hex="#E61E2B", assembly_term=22)
        assert data.color_hex == "#E61E2B"
