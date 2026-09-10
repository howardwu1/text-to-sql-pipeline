"""Integration tests: extraction, execution, reflection loop, full pipeline."""
import sqlite3
from unittest.mock import patch

from text_to_sql.executor import execute_with_reflection, run_pipeline
from text_to_sql.llm_client import extract_sql

# ---------------------------------------------------------------- extraction

def test_extract_sql_from_code_block():
    assert extract_sql("```sql\nSELECT 1;\n```") == "SELECT 1;"


def test_extract_sql_fallback_bare_text():
    assert extract_sql("SELECT 1;") == "SELECT 1;"


# ------------------------------------------------------- execution (direct SQL)

def test_execution_success(file_db, mock_llm):
    results, error = execute_with_reflection(
        file_db, "SELECT COUNT(*) FROM customers;", "how many customers?"
    )
    assert error is None
    assert results[0][0] == 3  # Alice, Bob, Charlie from init_db seed data


def test_reflection_loop_repairs_query(file_db, fail_then_succeed_llm):
    """Broken SQL on attempt 1 → repaired by the reflection loop on attempt 2."""
    results, error = execute_with_reflection(
        file_db, "SELECT nocol FROM customers;", "list customers"
    )
    assert error is None
    assert results
    assert results[0][0] in ("Alice", "Bob", "Charlie")


def test_reflection_loop_gives_up_after_max_retries(file_db, mock_llm):
    """If repairs keep failing, the loop must give up after MAX_RETRIES."""
    with patch(
        "text_to_sql.executor.generate_sqlite_query",
        return_value="```sql\nSELECT nocol FROM customers;\n```",
    ):
        results, error = execute_with_reflection(
            file_db, "SELECT nocol FROM customers;", "list customers"
        )
    assert results is None
    assert error is not None
    assert "maximum retries" in error.lower()


def test_empty_result_is_success(file_db, mock_llm):
    """Zero rows is a valid outcome, not an error."""
    # Define a repaired query that actually keeps the empty-result filter!
    repaired_query = "```sql\nSELECT * FROM customers WHERE customer_id = 99999;\n```"
    
    with patch("text_to_sql.executor.generate_sqlite_query", return_value=repaired_query):
        results, error = execute_with_reflection(
            file_db, "SELECT * customers WHERE customer_id = 99999;", "find 99999"
        )
        
    assert error is None
    assert results == []


# ------------------------------------------------------------- full pipeline

def test_full_pipeline_end_to_end(file_db, mock_llm):
    """question → (mocked) LLM → extract → validate → LIMIT 100 → execute."""
    results, sql, error = run_pipeline("List all customers", file_db)
    assert error is None
    assert "LIMIT 100" in sql
    assert results
    assert results[0][0] in ("Alice", "Bob", "Charlie")


def test_pipeline_blocks_mutation(file_db, monkeypatch):
    """Guardrail must stop destructive SQL even if the model emits it."""
    with patch(
        "text_to_sql.executor.generate_sqlite_query",
        return_value="```sql\nDROP TABLE customers;\n```",
    ):
        results, sql, error = run_pipeline("delete everything", file_db)
    assert results is None
    assert sql is not None          # SQL was extracted before being blocked
    assert "guardrail" in error.lower()
    # and the database is untouched:
    conn = sqlite3.connect(file_db)
    count = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    conn.close()
    assert count == 3
