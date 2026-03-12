"""ETL configuration — shared constants and settings."""

import os

# 열린국회정보 API
ASSEMBLY_API_BASE = "https://open.assembly.go.kr/portal/openapi"
ASSEMBLY_API_KEY = os.getenv("ASSEMBLY_API_KEY", "")

# API endpoint codes
ENDPOINTS = {
    "politicians": "nwvrqwxyaytdsfvhu",
    "bills": "nzmimeepazxkubdpn",
    "bill_review": "nojepdqqaweusdfbi",
    "vote_results": "ncocpbgebiallbyeq",
    "vote_records": "nwbpacrgavhjryiph",
    "committees": "nknaocmjlgzmoutew",
}

# Database
DATABASE_URL_SYNC = os.getenv(
    "DATABASE_URL_SYNC", "postgresql://kracc:kracc@db:5432/kracc"
)
AGE_GRAPH_NAME = os.getenv("AGE_GRAPH_NAME", "kr_acc")

# Current assembly term
ASSEMBLY_TERM = 22

# Pagination
PAGE_SIZE = 1000
