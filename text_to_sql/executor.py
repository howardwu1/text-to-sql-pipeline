"""Stage 4: local SQLite execution with a reflection self-correction loop."""
import sqlite3

from . import config

# 1. Import extract_sql at the top of your file
from .llm_client import extract_sql, generate_sqlite_query
from .safety import UnsafeQueryError, enforce_limit, validate

REFLECTION_PROMPT_TEMPLATE = """The previous SQL query you generated caused an error. Please fix it.
Original Request: {original_prompt}
Generated Query: {sql_query}
SQLite Error Message: {error}
Return only the corrected SQLite query in a ```sql block."""


def execute_with_reflection(
    db_path: str,
    sql_query: str,
    original_prompt: str,
    retries: int = config.MAX_RETRIES,
):
    """Returns (results, error). Retries heal SQL via ox-alpha on failure."""
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        for attempt in range(retries):
            try:
                cursor.execute(sql_query)
                results = cursor.fetchall()
                return results, None
            except sqlite3.Error as e:
                if attempt == retries - 1:
                    return None, (
                        f"Execution failed after maximum retries. "
                        f"Final Error: {e!s}"
                    )
                print(f"[reflection] Attempt {attempt + 1} failed: {e}. Repairing...")
                
                # 2. Capture the raw response from the AI model
                raw_response = generate_sqlite_query(
                    REFLECTION_PROMPT_TEMPLATE.format(
                        original_prompt=original_prompt,
                        sql_query=sql_query,
                        error=str(e),
                    )
                )
                
                # 3. Clean the markdown backticks out of the string before looping!
                sql_query = extract_sql(raw_response)
                
        return None, "Execution failed after maximum retries."
    finally:
        conn.close()


def run_pipeline(question: str, db_path: str):
    """Full flow: context -> LLM -> safety -> execute. Returns (results, sql, error)."""
    from .context_agent import build_prompt, get_schema_context

    conn = sqlite3.connect(db_path)
    try:
        schema = get_schema_context(conn, config.PRUNED_TABLES)
    finally:
        conn.close()

    prompt = build_prompt(question, schema)
    raw = generate_sqlite_query(prompt)

    # Note: run_pipeline was already doing it right here!
    sql = extract_sql(raw)

    try:
        sql = validate(sql)
    except UnsafeQueryError as e:
        return None, sql, str(e)

    sql = enforce_limit(sql)
    results, error = execute_with_reflection(db_path, sql, prompt)
    return results, sql, error