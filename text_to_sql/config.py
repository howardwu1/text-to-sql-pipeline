"""Central configuration: LLM params, endpoints, DB fallback resolution."""
import os

from dotenv import load_dotenv

load_dotenv()

AIHUBMIX_API_KEY = os.environ.get("AIHUBMIX_API_KEY", "")
AIHUBMIX_BASE_URL = os.environ.get("AIHUBMIX_BASE_URL", "https://api.aihubmix.com/v1")

MODEL_ID = "ox-alpha"
LLM_PARAMS = {
    "temperature": 0.0,
    "max_tokens": 1000,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
}
REQUEST_TIMEOUT = 30  # seconds, per spec
MAX_RETRIES = 3
ROW_LIMIT = 100

# Meta-tables pruned from schema context to stay under token budget.
PRUNED_TABLES = {"sqlite_sequence", "sqlite_stat1", "sqlite_stat4"}


def resolve_db_path() -> str:
    """DB path fallback chain: DB_PATH -> ./data/local_cache.db -> :memory:"""
    env_path = os.environ.get("DB_PATH", "./data/ecommerce.db")
    if os.path.exists(env_path):
        return env_path
    fallback = "./data/local_cache.db"
    if os.path.exists(fallback):
        return fallback
    return ":memory:"  # transient mock structure
