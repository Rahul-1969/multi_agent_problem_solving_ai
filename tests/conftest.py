import sys
from pathlib import Path


# Resolve the project root from the tests directory
project_root = Path(__file__).resolve().parent.parent

# Insert the project root into sys.path only if it is not already present
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
