"""ETL test configuration."""

import sys
from pathlib import Path

# Add etl/ to path so assembly_client is importable
sys.path.insert(0, str(Path(__file__).parent.parent))
