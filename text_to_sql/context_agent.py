"""Stage 1: schema extraction + prompt assembly (token-budget pruning)."""
import sqlite3

SYSTEM_PROMPT = (
    "You are a strict SQLite expert. Return ONLY valid, executable SQLite "
    "code inside a markdown block. No preamble, no explanation."
)

from .few_shots import FEW_SHOT_EXAMPLES



def get_schema_context(conn: sqlite3.Connection, pruned_tables: set[str]) -> str:
    """Pull PRAGMA table_info for all user tables, skipping meta-tables."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name NOT LIKE 'sqlite_%'"
    )
    tables = [r[0] for r in cursor.fetchall() if r[0] not in pruned_tables]

    blocks = []
    for table in sorted(tables):
        cursor.execute(f"PRAGMA table_info({table})")
        cols = cursor.fetchall()
        col_defs = ", ".join(f"{c[1]} {c[2]}" for c in cols)
        pk = [c[1] for c in cols if c[5]]
        if pk:
            col_defs += f", PRIMARY KEY ({', '.join(pk)})"
        blocks.append(f"CREATE TABLE {table} ({col_defs});")
    return "\n".join(blocks)


def build_prompt(user_question: str, schema_context: str) -> str:
    return (
        f"{SYSTEM_PROMPT}\n\n"
        "### Database Schema\n"
        f"{schema_context}\n\n"
        "### Few-Shot Examples\n"
        f"{FEW_SHOT_EXAMPLES}\n"
        "### Task\n"
        f"Question: {user_question}\n"
        "Write one SQLite query that answers the question."
    )
