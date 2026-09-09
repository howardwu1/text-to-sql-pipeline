import sqlite3
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from init_db import SCHEMA_SQL


@pytest.fixture()
def file_db(tmp_path):                      # tmp_path = pytest's per-test temp dir
    path = str(tmp_path / "test.db")
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA_SQL)          # write schema to DISK
    conn.close()                            # file survives the close
    return path                             # hand back the PATH, not the connection


@pytest.fixture()
def mock_llm():
    """Patches generate_sqlite_query to return a canned, correct query."""
    canned = "```sql\nSELECT first_name, last_name FROM customers;\n```"
    with patch("text_to_sql.executor.generate_sqlite_query", return_value=canned):
        yield canned


@pytest.fixture()
def fail_then_succeed_llm():
    """First call returns broken SQL; the reflection call fixes it."""
    responses = iter([
        "```sql\nSELECT nocol FROM customers;\n```",
        "```sql\nSELECT first_name FROM customers;\n```",
    ])
    with patch(
        "text_to_sql.executor.generate_sqlite_query",
        side_effect=lambda _: next(responses),
    ):
        yield
