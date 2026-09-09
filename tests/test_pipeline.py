import sqlite3

from text_to_sql import config
from text_to_sql.executor import execute_with_reflection, run_pipeline
from text_to_sql.llm_client import extract_sql


def test_extract_sql_from_code_block():
    assert extract_sql("```sql\nSELECT 1;\n```") == "SELECT 1;"


def test_extract_sql_fallback_bare_text():
    assert extract_sql("SELECT 1;") == "SELECT 1;"


def test_execution_success(db_conn, mock_llm):
    results, error = execute_with_reflection(
        ":memory:", "SELECT COUNT(*) FROM customers;", "how many customers?"
    )
    assert error is None
    assert results[0][0] == 3


def test_reflection_loop_repairs_query(fail_then_succeed_llm):
    conn = sqlite3.connect(":memory:")
    from init_db import SCHEMA_SQL
    conn.executescript(SCHEMA_SQL)
    conn.close()

    results, error = execute_with_reflection(
        ":memory:", "SELECT nocol FROM customers;", "list customers"
    )
    assert error is None
    assert results


def test_full_pipeline_end_to_end(file_db, mock_llm):
    results, sql, error = run_pipeline("List all customers", file_db)  # ✅ real path
    # run_pipeline's internal connections open the same file → schema visible
    results, sql, error = run_pipeline("List all customers", ":memory:")
    assert error is None
    assert "LIMIT 100" in sql
    assert results


def test_pipeline_blocks_mutation(db_conn, monkeypatch):
    monkeypatch.setenv("AIHUBMIX_API_KEY", "dummy")
    from unittest.mock import patch
    with patch("text_to_sql.executor.generate_sqlite_query",
               return_value="```sql\nDROP TABLE customers;\n```"):
        results, sql, error = run_pipeline("delete everything", ":memory:")
    assert results is None
    assert "guardrail" in error.lower()
