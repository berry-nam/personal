"""Unit tests for Newstapa and LIKMS scrapers — pure parser logic, no network."""

import pytest

from scrapers.newstapa import (
    AssetBreakdown,
    YearlyAsset,
    _parse_breakdown_tables,
    _parse_chart_data,
    parse_detail_page,
    parse_korean_amount,
)
from scrapers.likms import MemberVote, parse_vote_page


# ══════════════════════════════════════════════════════════════════════════════
# Newstapa: parse_korean_amount
# ══════════════════════════════════════════════════════════════════════════════


class TestParseKoreanAmount:
    def test_eok_and_man(self):
        assert parse_korean_amount("12억 1118만원") == 1_211_180_000

    def test_eok_only(self):
        assert parse_korean_amount("4억원") == 400_000_000

    def test_man_only(self):
        assert parse_korean_amount("500만원") == 5_000_000

    def test_man_with_digits(self):
        assert parse_korean_amount("2033만원") == 20_330_000

    def test_negative(self):
        assert parse_korean_amount("-1억 2000만원") == -120_000_000

    def test_with_commas(self):
        assert parse_korean_amount("1,200만원") == 12_000_000

    def test_dash_returns_none(self):
        assert parse_korean_amount("-") is None

    def test_empty_returns_none(self):
        assert parse_korean_amount("") is None

    def test_none_returns_none(self):
        assert parse_korean_amount(None) is None

    def test_plain_number(self):
        assert parse_korean_amount("5000원") == 5000

    def test_eok_man_combined(self):
        assert parse_korean_amount("4억 3718만원") == 437_180_000


# ══════════════════════════════════════════════════════════════════════════════
# Newstapa: _parse_chart_data
# ══════════════════════════════════════════════════════════════════════════════


class TestParseChartData:
    def test_basic_chart(self):
        html = """
        var chart = new Chart(ctx, {
            data: ["2020년", "2021년", "2022년"],
            data: [500000000, 600000000, 700000000],
        });
        """
        result = _parse_chart_data(html)
        assert len(result) == 3
        assert result[0].year == 2020
        assert result[0].total_assets == 500_000_000
        assert result[2].year == 2022
        assert result[2].total_assets == 700_000_000

    def test_no_data_arrays(self):
        assert _parse_chart_data("<html>nothing here</html>") == []

    def test_single_data_array(self):
        html = 'data: ["2020년", "2021년"]'
        assert _parse_chart_data(html) == []


# ══════════════════════════════════════════════════════════════════════════════
# Newstapa: _parse_breakdown_tables
# ══════════════════════════════════════════════════════════════════════════════


class TestParseBreakdownTables:
    def test_basic_table(self):
        html = """
        <div>2023년 재산내역</div>
        <table class="asset">
            <tr><td>항목</td><td>비율</td><td>금액</td></tr>
            <tr><td>건물</td><td>45%</td><td>5억원</td></tr>
            <tr><td>예금</td><td>30%</td><td>3억원</td></tr>
        </table>
        """
        result = _parse_breakdown_tables(html)
        assert 2023 in result
        items = result[2023]
        assert len(items) == 2
        assert items[0].category == "건물"
        assert items[0].amount_krw == 500_000_000
        assert items[1].category == "예금"

    def test_duplicate_year_uses_first(self):
        html = """
        <div>2023년</div>
        <table><tr><td>건물</td><td>50%</td><td>5억원</td></tr></table>
        <div>2023년</div>
        <table><tr><td>예금</td><td>50%</td><td>3억원</td></tr></table>
        """
        result = _parse_breakdown_tables(html)
        assert 2023 in result
        assert len(result[2023]) == 1
        assert result[2023][0].category == "건물"

    def test_no_tables(self):
        assert _parse_breakdown_tables("<html>empty</html>") == {}


# ══════════════════════════════════════════════════════════════════════════════
# Newstapa: parse_detail_page (integration of chart + breakdown)
# ══════════════════════════════════════════════════════════════════════════════


class TestParseDetailPage:
    def test_merges_chart_and_breakdown(self):
        # Simulate realistic page: chart data in JS, breakdown tables in HTML body
        html = """
        <script>
        var chart = new Chart(ctx, {
            data: ["2022년", "2023년"],
            data: [500000000, 800000000],
        });
        </script>
        <div class="breakdown">
            <h3>2022년 재산내역</h3>
            <table>
                <tr><td>건물</td><td>70%</td><td>3억원</td></tr>
            </table>
            <h3>2023년 재산내역</h3>
            <table>
                <tr><td>건물</td><td>60%</td><td>5억원</td></tr>
                <tr><td>예금</td><td>40%</td><td>3억원</td></tr>
            </table>
        </div>
        """
        result = parse_detail_page(html)
        assert len(result) == 2
        assert result[0].year == 2022
        assert result[1].year == 2023
        # Both years should have breakdown data
        assert len(result[0].breakdown) >= 1
        assert len(result[1].breakdown) == 2
        assert result[1].breakdown[0].category == "건물"


# ══════════════════════════════════════════════════════════════════════════════
# LIKMS: parse_vote_page
# ══════════════════════════════════════════════════════════════════════════════


SAMPLE_LIKMS_HTML = """
<html>
<body>
<div>재적 300명</div>
<ul id="voteAgreeList" class="list">
    <li><a href="https://open.assembly.go.kr/portal/member/M001"><img/><p>김철수</p></a></li>
    <li><a href="https://open.assembly.go.kr/portal/member/M002"><img/><p>이영희</p></a></li>
    <li><a href="https://open.assembly.go.kr/portal/member/M003"><img/><p>박민수</p></a></li>
</ul>
<ul id="voteDisAgreeList" class="list">
    <li><a href="https://open.assembly.go.kr/portal/member/M004"><img/><p>최지은</p></a></li>
</ul>
<ul id="voteAbsList" class="list">
    <li><a href="https://open.assembly.go.kr/portal/member/M005"><img/><p>정하나</p></a></li>
    <li><a href="https://open.assembly.go.kr/portal/member/M006"><img/><p>강두리</p></a></li>
</ul>
</body>
</html>
"""


class TestParseVotePage:
    def test_basic_parse(self):
        result = parse_vote_page(SAMPLE_LIKMS_HTML, "PRC_TEST001")
        assert result.bill_id == "PRC_TEST001"
        assert result.total_members == 300
        assert result.yes_count == 3
        assert result.no_count == 1
        assert result.abstain_count == 2
        assert len(result.member_votes) == 6

    def test_member_names(self):
        result = parse_vote_page(SAMPLE_LIKMS_HTML, "PRC_TEST001")
        names = {mv.name for mv in result.member_votes}
        assert "김철수" in names
        assert "이영희" in names
        assert "최지은" in names
        assert "정하나" in names

    def test_vote_results_assigned_correctly(self):
        result = parse_vote_page(SAMPLE_LIKMS_HTML, "PRC_TEST001")
        by_name = {mv.name: mv.vote_result for mv in result.member_votes}
        assert by_name["김철수"] == "찬성"
        assert by_name["최지은"] == "반대"
        assert by_name["정하나"] == "기권"

    def test_profile_urls_extracted(self):
        result = parse_vote_page(SAMPLE_LIKMS_HTML, "PRC_TEST001")
        by_name = {mv.name: mv.profile_url for mv in result.member_votes}
        assert "assembly.go.kr" in by_name["김철수"]

    def test_empty_page(self):
        result = parse_vote_page("<html><body>no votes</body></html>", "PRC_EMPTY")
        assert result.member_votes == []
        assert result.yes_count == 0
        assert result.no_count == 0
        assert result.abstain_count == 0

    def test_missing_sections(self):
        html = """
        <ul id="voteAgreeList">
            <li><a><p>김철수</p></a></li>
        </ul>
        """
        result = parse_vote_page(html, "PRC_PARTIAL")
        assert result.yes_count == 1
        assert result.no_count == 0
        assert result.abstain_count == 0

    def test_no_total_members(self):
        html = """
        <ul id="voteAgreeList">
            <li><a><p>김철수</p></a></li>
        </ul>
        """
        result = parse_vote_page(html, "PRC_NOTOTAL")
        assert result.total_members == 0

    def test_short_names_excluded(self):
        """Names shorter than 2 characters should be excluded by regex."""
        html = """
        <ul id="voteAgreeList">
            <li><a><p>김</p></a></li>
            <li><a><p>김철수</p></a></li>
        </ul>
        """
        result = parse_vote_page(html, "PRC_SHORT")
        assert result.yes_count == 1
        assert result.member_votes[0].name == "김철수"
