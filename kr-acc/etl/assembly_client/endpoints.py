"""열린국회정보 API endpoint slug constants."""

BASE_URL = "https://open.assembly.go.kr/portal/openapi/"

# 국회의원 인적사항 (legislator bio)
LEGISLATORS = "nwvrqwxyaytdsfvhu"

# 의안 정보 (bill info)
BILLS = "nzmimeepazxkubdpn"

# 법률안 심사정보 (bill review)
BILL_REVIEW = "nojepdqqaweusdfbi"

# 의안별 표결현황 (plenary vote summary per bill)
VOTE_SUMMARY = "ncocpgfiaoituanbr"

# 국회의원 본회의 표결정보 (bill-level vote info — requires AGE param)
VOTE_PER_MEMBER = "nwbpacrgavhjryiph"

# 위원회 현황 — NOTE: endpoint slug TBD, currently broken
COMMITTEES = "nknaocmjlgzmoutew"
