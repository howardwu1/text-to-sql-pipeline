"""Stage 3b: blocklist sanitation + LIMIT enforcement."""
import re

from . import config

BLOCKLIST_PATTERNS = [
    r"\bDROP\b",
    r"\bDELETE\b",
    r"\bALTER\b",
    r"\bUPDATE\b",
    r"\bINSERT\b",
]

_LIMIT_RE = re.compile(r"\bLIMIT\s+\d+", re.IGNORECASE)
_TRAILING_SEMI = re.compile(r";\s*$")


class UnsafeQueryError(ValueError):
    pass


def validate(sql: str) -> str:
    """Raise UnsafeQueryError on structural-modification keywords."""
    for pattern in BLOCKLIST_PATTERNS:
        if re.search(pattern, sql, re.IGNORECASE):
            raise UnsafeQueryError(f"Blocked by safety guardrail: /{pattern}/ matched.")
    return sql


def enforce_limit(sql: str, limit: int = config.ROW_LIMIT) -> str:
    """Append LIMIT 100 if the model didn't specify one."""
    cleaned = _TRAILING_SEMI.sub("", sql.strip()).rstrip(";").strip()
    if _LIMIT_RE.search(cleaned):
        return cleaned
    return f"{cleaned} LIMIT {limit}"
