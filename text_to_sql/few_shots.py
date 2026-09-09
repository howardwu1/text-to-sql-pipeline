"""Few-shot examples, split out of context_agent for easy tuning/extension."""

FEW_SHOT_EXAMPLES = """-- Example 1
-- Question: How many orders did each customer place?
SELECT c.first_name, c.last_name, COUNT(o.order_id) AS order_count
FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id;

-- Example 2
-- Question: What is the total revenue per product category?
SELECT p.category, SUM(o.total_amount) AS revenue
FROM orders o JOIN products p ON o.product_id = p.product_id
GROUP BY p.category;

-- Example 3
-- Question: Which products are low on stock (fewer than 20 units)?
SELECT product_name, stock_quantity
FROM products
WHERE stock_quantity < 20
ORDER BY stock_quantity ASC;
"""
