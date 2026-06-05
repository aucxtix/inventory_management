from database import get_connection
from config import LOW_STOCK_THRESHOLD

def add_product(name, category, supplier, price, stock, reorder_level=5, description="", sku=""):
    """Adds a new product. Returns (success, message)."""
    if not name or not category or not supplier:
        return False, "Name, Category, and Supplier are required."
    try:
        price = float(price)
        stock = int(stock)
        reorder_level = int(reorder_level)
        if price < 0:
            return False, "Price cannot be negative."
        if stock < 0:
            return False, "Stock cannot be negative."
    except (ValueError, TypeError):
        return False, "Invalid numeric values for Price, Stock, or Reorder Level."

    try:
        conn = get_connection()
        cur = conn.cursor()
        # Check for duplicate product name
        cur.execute("SELECT id FROM products WHERE LOWER(name)=?", (name.lower(),))
        if cur.fetchone():
            conn.close()
            return False, f"Product '{name}' already exists."

        cur.execute(
            "INSERT INTO products(name, category, supplier, price, stock, reorder_level, description, sku) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (name, category, supplier, price, stock, reorder_level, description, sku)
        )
        conn.commit()
        conn.close()
        return True, f"Product '{name}' added successfully."
    except Exception as e:
        return False, str(e)

def get_all_products():
    """Returns all products as a list of tuples."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, category, supplier, price, stock, reorder_level, description, sku FROM products")
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception:
        return []

def get_product(product_id):
    """Returns a single product by ID."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, category, supplier, price, stock, reorder_level, description, sku FROM products WHERE id=?", (product_id,))
        row = cur.fetchone()
        conn.close()
        return row
    except Exception:
        return None

def update_product(product_id, name, category, supplier, price, stock, reorder_level=5, description="", sku=""):
    """Updates an existing product. Returns (success, message)."""
    if not name or not category or not supplier:
        return False, "Name, Category, and Supplier are required."
    try:
        price = float(price)
        stock = int(stock)
        reorder_level = int(reorder_level)
        if price < 0:
            return False, "Price cannot be negative."
        if stock < 0:
            return False, "Stock cannot be negative."
    except (ValueError, TypeError):
        return False, "Invalid numeric values."

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE products SET name=?, category=?, supplier=?, price=?, stock=?, "
            "reorder_level=?, description=?, sku=? WHERE id=?",
            (name, category, supplier, price, stock, reorder_level, description, sku, product_id)
        )
        if cur.rowcount == 0:
            conn.close()
            return False, "Product not found."
        conn.commit()
        conn.close()
        return True, f"Product '{name}' updated."
    except Exception as e:
        return False, str(e)

def delete_product(product_id):
    """Deletes a product by ID. Returns (success, message)."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT name FROM products WHERE id=?", (product_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return False, "Product not found."
        cur.execute("DELETE FROM products WHERE id=?", (product_id,))
        conn.commit()
        conn.close()
        return True, f"Product '{row[0]}' deleted."
    except Exception as e:
        return False, str(e)

def search_products(query_type, query_val):
    """Searches products by name, category, or supplier."""
    allowed_cols = {"name", "category", "supplier"}
    if query_type not in allowed_cols:
        return []
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            f"SELECT id, name, category, supplier, price, stock, reorder_level, description, sku "
            f"FROM products WHERE {query_type} LIKE ?",
            (f"%{query_val}%",)
        )
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception:
        return []

def get_categories():
    """Returns a list of unique categories."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT category FROM products ORDER BY category")
        cats = [row[0] for row in cur.fetchall()]
        conn.close()
        return cats
    except Exception:
        return []

def get_suppliers():
    """Returns a list of unique suppliers."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT supplier FROM products ORDER BY supplier")
        sups = [row[0] for row in cur.fetchall()]
        conn.close()
        return sups
    except Exception:
        return []

def get_low_stock_products():
    """Returns products where stock <= reorder_level."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, name, category, supplier, price, stock, reorder_level FROM products "
            "WHERE stock <= reorder_level AND stock > 0"
        )
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception:
        return []

def get_out_of_stock_products():
    """Returns products with zero stock."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, name, category, supplier, price, stock FROM products WHERE stock = 0"
        )
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception:
        return []

def get_product_names_ids():
    """Returns list of (id, name, stock, price) for dropdowns."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, stock, price FROM products ORDER BY name")
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception:
        return []