"""Stage 2: unified inference via the AIHubMix gateway (ox-alpha model)."""
import re

from openai import OpenAI

from . import config

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        if not config.AIHUBMIX_API_KEY:
            raise RuntimeError("AIHUBMIX_API_KEY is not set.")
        _client = OpenAI(
            api_key=config.AIHUBMIX_API_KEY,
            base_url=config.AIHUBMIX_BASE_URL,
            timeout=config.REQUEST_TIMEOUT,
        )
    return _client


def generate_sqlite_query(prompt_context: str) -> str:
    """Call ox-alpha; deterministic temperature=0.0 per spec."""
    response = _get_client().chat.completions.create(
        model=config.MODEL_ID,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_TEMPLATE},
            {"role": "user", "content": prompt_context},
        ],
        **config.LLM_PARAMS,
    )
    return response.choices[0].message.content


SYSTEM_PROMPT_TEMPLATE = (
    "You are a strict SQLite expert. Return ONLY valid, executable SQLite "
    "code inside a markdown block. No preamble, no explanation."
)


def extract_sql(raw_response: str) -> str | None:
    """Stage 3a: regex-extract ```sql ... ``` block contents."""
    match = re.search(r"```sql\s*(.*?)\s*```", raw_response, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # Fallback: bare fenced block or raw string.
    match = re.search(r"```\s*(.*?)\s*```", raw_response, re.DOTALL)
    return (match.group(1) if match else raw_response).strip() or None
