"""CLI entry point: interactive or single-question mode."""
import sys

from . import config
from .executor import run_pipeline


def main():
    db_path = config.resolve_db_path()
    print(f"Database: {db_path}")

    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        answer(question, db_path)
        return

    print("Interactive mode (type 'quit' to exit).")
    while True:
        try:
            question = input("\nQuestion> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if question.lower() in {"quit", "exit", ""}:
            break
        answer(question, db_path)


def answer(question: str, db_path: str):
    results, sql, error = run_pipeline(question, db_path)
    if error:
        print(f"ERROR: {error}")
        return
    print(f"\nSQL:\n{sql}\n")
    print(f"Rows returned: {len(results)}")
    for row in results[:20]:
        print(row)


if __name__ == "__main__":
    main()
