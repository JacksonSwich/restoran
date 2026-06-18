"""SQL-запросы для всех таблиц."""

from database.connection import fetch_one, fetch_all, execute_insert, execute

# ─── CATEGORIES ─────────────────────────────────────────────────

def get_all_categories():
    return fetch_all("SELECT * FROM categories WHERE is_active = TRUE ORDER BY name")

def get_category_by_id(cat_id: int):
    return fetch_one("SELECT * FROM categories WHERE id = %s", (cat_id,))

def create_category(name: str, description: str = "") -> int:
    return execute_insert(
        "INSERT INTO categories (name, description) VALUES (%s, %s)",
        (name, description),
    )

def update_category(cat_id: int, name: str, description: str = ""):
    execute(
        "UPDATE categories SET name = %s, description = %s WHERE id = %s",
        (name, description, cat_id),
    )

def delete_category(cat_id: int):
    execute("UPDATE categories SET is_active = FALSE WHERE id = %s", (cat_id,))


# ─── DISHES ─────────────────────────────────────────────────────

def get_all_dishes():
    return fetch_all(
        """SELECT d.*, c.name AS category_name
           FROM dishes d
           JOIN categories c ON d.category_id = c.id
           ORDER BY c.name, d.name"""
    )

def get_available_dishes():
    return fetch_all(
        """SELECT d.*, c.name AS category_name
           FROM dishes d
           JOIN categories c ON d.category_id = c.id
           WHERE d.is_available = TRUE
           ORDER BY c.name, d.name"""
    )

def get_dishes_by_category(category_id: int):
    return fetch_all(
        """SELECT d.*, c.name AS category_name
           FROM dishes d
           JOIN categories c ON d.category_id = c.id
           WHERE d.category_id = %s
           ORDER BY d.name""",
        (category_id,),
    )

def get_dish_by_id(dish_id: int):
    return fetch_one(
        """SELECT d.*, c.name AS category_name
           FROM dishes d
           JOIN categories c ON d.category_id = c.id
           WHERE d.id = %s""",
        (dish_id,),
    )

def create_dish(category_id: int, name: str, description: str,
                price: float, weight: str, cooking_time: int) -> int:
    return execute_insert(
        """INSERT INTO dishes (category_id, name, description, price, weight, cooking_time_minutes)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (category_id, name, description, price, weight, cooking_time),
    )

def update_dish(dish_id: int, **kwargs):
    allowed = {"name", "description", "price", "weight", "cooking_time_minutes",
               "is_available", "category_id"}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return
    set_clause = ", ".join(f"{k} = %s" for k in fields)
    values = list(fields.values()) + [dish_id]
    execute(f"UPDATE dishes SET {set_clause} WHERE id = %s", values)

def toggle_dish_availability(dish_id: int):
    dish = get_dish_by_id(dish_id)
    if dish:
        execute("UPDATE dishes SET is_available = NOT is_available WHERE id = %s", (dish_id,))


# ─── RESTAURANT TABLES ──────────────────────────────────────────

def get_all_tables():
    return fetch_all("SELECT * FROM restaurant_tables ORDER BY table_number")

def get_free_tables():
    return fetch_all("SELECT * FROM restaurant_tables WHERE status = 'free' ORDER BY table_number")

def get_table_by_id(table_id: int):
    return fetch_one("SELECT * FROM restaurant_tables WHERE id = %s", (table_id,))

def create_table(table_number: int, seats: int, zone: str = "") -> int:
    return execute_insert(
        "INSERT INTO restaurant_tables (table_number, seats_count, zone) VALUES (%s, %s, %s)",
        (table_number, seats, zone),
    )

def update_table_status(table_id: int, status: str):
    execute(
        "UPDATE restaurant_tables SET status = %s WHERE id = %s",
        (status, table_id),
    )

def update_table(table_id: int, **kwargs):
    """Update table fields (table_number, seats_count, zone)."""
    allowed = {"table_number", "seats_count", "zone"}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return
    set_clause = ", ".join(f"{k} = %s" for k in fields)
    values = list(fields.values()) + [table_id]
    execute(f"UPDATE restaurant_tables SET {set_clause} WHERE id = %s", values)


# ─── CUSTOMERS ──────────────────────────────────────────────────

def get_all_customers():
    return fetch_all("""
        SELECT c.*,
               COUNT(o.id) AS orders_count,
               COALESCE(SUM(o.final_amount), 0) AS total_amount,
               MAX(o.created_at) AS last_order_date
        FROM customers c
        LEFT JOIN orders o ON o.customer_id = c.id
        GROUP BY c.id
        ORDER BY c.full_name
    """)

def get_customer_by_id(cust_id: int):
    return fetch_one("SELECT * FROM customers WHERE id = %s", (cust_id,))

def find_customers(query: str):
    like = f"%{query}%"
    return fetch_all(
        """SELECT * FROM customers
           WHERE full_name LIKE %s OR phone LIKE %s OR email LIKE %s
           ORDER BY full_name""",
        (like, like, like),
    )

def create_customer(full_name: str, phone: str, email: str,
                    discount: float = 0) -> int:
    return execute_insert(
        "INSERT INTO customers (full_name, phone, email, discount_percent) VALUES (%s, %s, %s, %s)",
        (full_name, phone, email, discount),
    )

def update_customer(cust_id: int, **kwargs):
    allowed = {"full_name", "phone", "email", "discount_percent"}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return
    set_clause = ", ".join(f"{k} = %s" for k in fields)
    values = list(fields.values()) + [cust_id]
    execute(f"UPDATE customers SET {set_clause} WHERE id = %s", values)


# ─── ORDERS ─────────────────────────────────────────────────────

def get_all_orders():
    return fetch_all(
        """SELECT o.*, rt.table_number, c.full_name AS customer_name
           FROM orders o
           JOIN restaurant_tables rt ON o.table_id = rt.id
           LEFT JOIN customers c ON o.customer_id = c.id
           ORDER BY o.created_at DESC"""
    )

def get_order_by_id(order_id: int):
    return fetch_one(
        """SELECT o.*, rt.table_number, c.full_name AS customer_name
           FROM orders o
           JOIN restaurant_tables rt ON o.table_id = rt.id
           LEFT JOIN customers c ON o.customer_id = c.id
           WHERE o.id = %s""",
        (order_id,),
    )

def get_orders_by_status(status: str):
    return fetch_all(
        """SELECT o.*, rt.table_number, c.full_name AS customer_name
           FROM orders o
           JOIN restaurant_tables rt ON o.table_id = rt.id
           LEFT JOIN customers c ON o.customer_id = c.id
           WHERE o.status = %s
           ORDER BY o.created_at DESC""",
        (status,),
    )

def get_active_orders():
    return fetch_all(
        """SELECT o.*, rt.table_number, c.full_name AS customer_name
           FROM orders o
           JOIN restaurant_tables rt ON o.table_id = rt.id
           LEFT JOIN customers c ON o.customer_id = c.id
           WHERE o.status IN ('new', 'cooking', 'ready', 'served')
           ORDER BY o.created_at DESC"""
    )

def create_order(table_id: int, customer_id: int | None = None,
                 comment: str = "") -> int:
    return execute_insert(
        """INSERT INTO orders (table_id, customer_id, comment) VALUES (%s, %s, %s)""",
        (table_id, customer_id, comment),
    )

def update_order_status(order_id: int, status: str):
    execute("UPDATE orders SET status = %s WHERE id = %s", (status, order_id))

def cancel_order(order_id: int):
    execute(
        "UPDATE orders SET status = 'cancelled', closed_at = NOW() WHERE id = %s",
        (order_id,),
    )


# ─── ORDER ITEMS ────────────────────────────────────────────────

def get_order_items(order_id: int):
    return fetch_all(
        """SELECT oi.*, d.name AS dish_name
           FROM order_items oi
           JOIN dishes d ON oi.dish_id = d.id
           WHERE oi.order_id = %s""",
        (order_id,),
    )

def add_order_item(order_id: int, dish_id: int, quantity: int,
                   price_at_order: float, comment: str = "") -> int:
    return execute_insert(
        """INSERT INTO order_items (order_id, dish_id, quantity, price_at_order, comment)
           VALUES (%s, %s, %s, %s, %s)""",
        (order_id, dish_id, quantity, price_at_order, comment),
    )

def remove_order_item(item_id: int):
    execute("DELETE FROM order_items WHERE id = %s", (item_id,))


# ─── PAYMENTS ───────────────────────────────────────────────────

def get_all_payments():
    return fetch_all(
        """SELECT p.*, o.table_id, rt.table_number
           FROM payments p
           JOIN orders o ON p.order_id = o.id
           JOIN restaurant_tables rt ON o.table_id = rt.id
           ORDER BY p.created_at DESC"""
    )

def get_payments_by_order(order_id: int):
    return fetch_all("SELECT * FROM payments WHERE order_id = %s", (order_id,))

def create_payment(order_id: int, amount: float, method: str) -> int:
    return execute_insert(
        """INSERT INTO payments (order_id, amount, payment_method, status, paid_at)
           VALUES (%s, %s, %s, 'paid', NOW())""",
        (order_id, amount, method),
    )


# ─── REPORTS ────────────────────────────────────────────────────

def get_daily_revenue():
    return fetch_all("SELECT * FROM view_daily_revenue ORDER BY payment_date DESC")

def get_popular_dishes():
    return fetch_all("SELECT * FROM view_popular_dishes LIMIT 10")

def get_orders_full():
    return fetch_all("SELECT * FROM view_orders_full ORDER BY created_at DESC")
