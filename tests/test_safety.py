import pytest

from text_to_sql.safety import UnsafeQueryError, enforce_limit, validate


def test_blocks_drop():
    with pytest.raises(UnsafeQueryError):
        validate("DROP TABLE customers;")


def test_blocks_all_mutations():
    for bad in ["DELETE FROM customers;", "ALTER TABLE orders ADD COLUMN x TEXT;",
                "UPDATE customers SET email = 'x';", "INSERT INTO customers VALUES (,'a','b','c','d');"]:
        with pytest.raises(UnsafeQueryError):
            validate(bad)


def test_whole_word_matching_no_false_positive():
    # 'updated_at' as a column name must NOT trigger the UPDATE blocklist.
    assert validate("SELECT updated_at FROM logs;") is not None


def test_case_insensitive():
    with pytest.raises(UnsafeQueryError):
        validate("drop table customers;")


def test_limit_appended():
    assert enforce_limit("SELECT * FROM customers;").endswith("LIMIT 100")


def test_existing_limit_preserved():
    sql = enforce_limit("SELECT * FROM customers LIMIT 5;")
    assert sql == "SELECT * FROM customers LIMIT 5"


def test_trailing_semicolon_stripped_before_limit():
    assert not enforce_limit("SELECT 1;").endswith("LIMIT 100;")
