# Local Text-to-SQL Pipeline (SQLite + AIHubMix)

End-to-end pipeline: natural language → SQL via the **ox-alpha** model on
AIHubMix → safety validation → local SQLite execution with a reflection-based
self-correction loop (max 3 retries).

## Architecture
User question → Context Agent (pruned schema + few-shot) → Prompt Assembly →
AIHubMix (`ox-alpha`) → SQL extraction (```sql blocks) → blocklist sanitation
(DROP/DELETE/ALTER/UPDATE/INSERT) → auto `LIMIT 100` → SQLite execution →
results, or reflection loop on error.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # add your AIHUBMIX_API_KEY
python init_db.py      # creates ./data/ecommerce.db
python -m text_to_sql.main "Which customers spent the most in June 2025?"
```

Interactive mode:

```bash
python -m text_to_sql.main
```

## Configuration
| Env var | Default | Purpose |
|---|---|---|
| `AIHUBMIX_API_KEY` | — (required) | AIHubMix gateway key |
| `AIHUBMIX_BASE_URL` | `https://api.aihubmix.com/v1` | OpenAI-compatible endpoint |
| `DB_PATH` | `./data/ecommerce.db` (fallback `./data/local_cache.db`, then `:memory:`) | Database location |

LLM params (per spec): `temperature=0.0`, `max_tokens=1000`, `top_p=1.0`,
penalties `0.0`. API timeout fixed at **30 seconds.
