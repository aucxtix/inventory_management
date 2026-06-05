from datetime import datetime
from database import get_connection, log_activity
from auth import Session

def record_purchase(product_id, quantity):
    """Records a purchase, increases stock atomically. Returns (success, message)."""
    try:
        qty = int(quantity)
        if qty <= 0:
            return False, "Quantity must be greater than zero."
    except (ValueError, TypeError):
        return False, "Invalid quantity."

    try:
        conn = get_connection()
        cur = conn.cursor()

        # Get product info
        cur.execute("SELECT name, price, supplier FROM products WHERE id=?", (product_id,))
        product = cur.fetchone()
        if not product:
            conn.close()
            return False, "Product not found."

        name, price, supplier = product
        total_amount = round(price * qty, 2)

        # Atomic stock update
        cur.execute("UPDATE products SET stock = stock + ? WHERE id=?", (qty, product_id))
        if cur.rowcount == 0:
            conn.close()
            return False, "Stock update failed."

        purchase_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute(
            "INSERT INTO purchases(product_id, quantity, total_amount, purchase_date) "
            "VALUES (?, ?, ?, ?)",
            (product_id, qty, total_amount, purchase_date)
        )
        conn.commit()
        conn.close()

        user = Session.username or "System"
        log_activity(user, "Purchase", f"Purchased {qty}x '{name}' for ${total_amount:.2f}")

        return True, f"Purchased {qty}x '{name}' — Total: ${total_amount:.2f}"
    except Exception as e:
        return False, str(e)

def get_all_purchases():
    """Returns all purchases with product names, ordered newest first."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT pu.id, p.name, pu.quantity, pu.total_amount, pu.purchase_date
            FROM purchases pu JOIN products p ON pu.product_id = p.id
            ORDER BY pu.id DESC
        """)
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception:
        return []