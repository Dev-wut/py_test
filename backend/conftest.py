import sys
from unittest.mock import MagicMock

sys.modules.setdefault("psycopg2", MagicMock())
