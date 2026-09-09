"""Initialize the local SQLite target database (ecommerce.db)."""
import os
import sqlite3

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    join_date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    stock_quantity INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    total_amount REAL NOT NULL,
    order_date TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

INSERT OR IGNORE INTO customers (customer_id, first_name, last_name, email, join_date) VALUES
(1, 'Alice', 'Smith', 'alice.smith@example.com', '2025-01-15'),
(2, 'Bob', 'Johnson', 'bob.johnson@example.com', '2025-02-20'),
(3, 'Charlie', 'Brown', 'charlie.brown@example.com', '2025-03-05');

INSERT OR IGNORE INTO products (product_id, product_name, category, price, stock_quantity) VALUES
(101, 'Wireless Mouse', 'Electronics', 29.99, 150),
(102, 'Mechanical Keyboard', 'Electronics', 89.99, 45),
(103, 'Ergonomic Desk Chair', 'Furniture', 249.99, 12),
(104, 'Leather Journal', 'Stationery', 15.50, 80);

INSERT OR IGNORE INTO orders (order_id, customer_id, product_id, quantity, total_amount, order_date) VALUES
(5001, 1, 101, 2, 59.98, '2025-05-10'),
(5002, 1, 104, 1, 15.50, '2025-05-12'),
(5003, 2, 102, 1, 89.99, '2025-06-01'),
(5004, 3, 103, 1, 249.99, '2025-06-14'),
(5005, 2, 101, 1, 29.99, '2025-06-15');
"""


def main(db_path: str = "./data/ecommerce.db") -> str:
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()
    print(f"Database ready at {db_path}")
    return db_path


if __name__ == "__main__":
    main()
