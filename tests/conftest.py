import sys
from pathlib import Path

# Ensure the project root is on sys.path so tests import local modules
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
