import sqlite3
import shutil
import hashlib
from datetime import datetime
from config import DB_NAME

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # 1. Users
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('Admin', 'Manager', 'Staff'))
    )''')

    # 2. Categories
    cur.execute('''CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )''')

    # 3. Suppliers
    cur.execute('''CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        contact TEXT
    )''')

    # 4. Customers
    cur.execute('''CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        total_purchases REAL DEFAULT 0.0
    )''')

    # 5. Products
    cur.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        category TEXT,
        supplier TEXT,
        price REAL NOT NULL CHECK(price >= 0),
        stock INTEGER NOT NULL CHECK(stock >= 0),
        reorder_level INTEGER NOT NULL DEFAULT 5,
        description TEXT DEFAULT '',
        sku TEXT UNIQUE
    )''')

    # 6. Invoices (Sales)
    cur.execute('''CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_number TEXT UNIQUE NOT NULL,
        customer_id INTEGER,
        subtotal REAL NOT NULL,
        discount REAL DEFAULT 0.0,
        cgst REAL NOT NULL,
        sgst REAL NOT NULL,
        grand_total REAL NOT NULL,
        payment_method TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE SET NULL
    )''')

    # 7. Invoice Items (Sale Items)
    cur.execute('''CREATE TABLE IF NOT EXISTS invoice_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        qty INTEGER NOT NULL CHECK(qty > 0),
        rate REAL NOT NULL,
        amount REAL NOT NULL,
        FOREIGN KEY(invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
        FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE RESTRICT
    )''')

    # 8. Purchases
    cur.execute('''CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        quantity INTEGER NOT NULL CHECK(quantity > 0),
        total_amount REAL NOT NULL,
        purchase_date TEXT NOT NULL,
        FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
    )''')

    # 10. Activity Logs
    cur.execute('''CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        action TEXT NOT NULL,
        details TEXT DEFAULT '',
        timestamp TEXT NOT NULL
    )''')

    # SEED DATA
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        seed_data(cur)

    conn.commit()
    conn.close()

def seed_data(cur):
    print("Database is empty. Seeding realistic demo data...")
    # Users
    users = [
        ("admin", hash_password("admin123"), "Admin"),
        ("manager", hash_password("manager123"), "Manager"),
        ("staff", hash_password("staff123"), "Staff")
    ]
    cur.executemany("INSERT INTO users(username, password, role) VALUES (?, ?, ?)", users)

    # Categories
    cats = [("Peripherals",), ("Displays",), ("Cables & Adapters",), ("Storage",)]
    cur.executemany("INSERT INTO categories(name) VALUES (?)", cats)

    # Suppliers
    sups = [("TechDistributors Inc.", "contact@techdist.com"), ("Global Electronics", "1-800-555-0199"), ("FastCables LLC", "sales@fastcables.net")]
    cur.executemany("INSERT INTO suppliers(name, contact) VALUES (?, ?)", sups)

    # Customers
    custs = [("Walk-in Customer", "", ""), ("John Doe", "555-0123", "john@example.com"), ("Acme Corp", "555-0987", "billing@acme.com")]
    cur.executemany("INSERT INTO customers(name, phone, email) VALUES (?, ?, ?)", custs)

    # Products (id, name, cat, sup, price, stock, reorder, desc, sku)
    prods = [
        ("Logitech MX Master 3S", "Peripherals", "TechDistributors Inc.", 99.99, 45, 10, "Wireless ergonomic mouse", "LOGI-MX3S"),
        ("Mechanical Keyboard RGB", "Peripherals", "TechDistributors Inc.", 129.50, 30, 5, "Cherry MX Red switches", "KEY-MECH-01"),
        ("Dell UltraSharp 27\" 4K", "Displays", "Global Electronics", 450.00, 15, 3, "Color accurate IPS display", "DELL-U2723QE"),
        ("USB-C to USB-C Cable 2m", "Cables & Adapters", "FastCables LLC", 15.00, 120, 20, "100W PD compatible", "CBL-USBC-2M"),
        ("Samsung 1TB NVMe SSD", "Storage", "Global Electronics", 85.00, 50, 10, "PCIe Gen 4.0 Storage", "SAM-980PRO-1TB"),
        ("Sony WH-1000XM5", "Peripherals", "TechDistributors Inc.", 348.00, 2, 5, "Noise cancelling headphones", "SONY-WH5"),
        ("HDMI 2.1 Cable 3m", "Cables & Adapters", "FastCables LLC", 18.50, 0, 15, "8K Ultra High Speed", "CBL-HDMI-3M")
    ]
    cur.executemany("INSERT INTO products(name, category, supplier, price, stock, reorder_level, description, sku) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", prods)

def log_activity(username, action, details=""):
    try:
        conn = get_connection()
        cur = conn.cursor()
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO activity_logs(username, action, details, timestamp) VALUES (?, ?, ?, ?)", (username, action, details, ts))
        conn.commit()
        conn.close()
    except Exception:
        pass

def get_recent_activity(limit=10):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT username, action, details, timestamp FROM activity_logs ORDER BY id DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception:
        return []

# User management
def get_all_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, role FROM users")
    users = cur.fetchall()
    conn.close()
    return users

def add_user(username, password, role):
    if len(password) < 4: return False, "Password too short."
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users(username, password, role) VALUES (?, ?, ?)", (username, hash_password(password), role))
        conn.commit()
        conn.close()
        return True, f"User '{username}' added."
    except sqlite3.IntegrityError: return False, "Username exists."
    except Exception as e: return False, str(e)

def delete_user(user_id, active_user_id):
    if str(user_id) == str(active_user_id): return False, "Cannot delete yourself."
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT role FROM users WHERE id=?", (user_id,))
        role = cur.fetchone()
        if role and role[0] == "Admin":
            cur.execute("SELECT COUNT(*) FROM users WHERE role='Admin'")
            if cur.fetchone()[0] <= 1: return False, "Cannot delete last Admin."
        cur.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()
        conn.close()
        return True, "User deleted."
    except Exception as e: return False, str(e)

def update_user_role(user_id, new_role):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET role=? WHERE id=?", (new_role, user_id))
        conn.commit()
        conn.close()
        return True, "Role updated."
    except Exception as e: return False, str(e)

def reset_user_password(user_id, new_password):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET password=? WHERE id=?", (hash_password(new_password), user_id))
        conn.commit()
        conn.close()
        return True, "Password reset."
    except Exception as e: return False, str(e)

# Backup / Restore
def backup_db(dest_path):
    try:
        if dest_path: shutil.copy2(DB_NAME, dest_path)
        return True, "Backup successful."
    except Exception as e: return False, str(e)

def restore_db(source_path):
    try:
        if source_path: shutil.copy2(source_path, DB_NAME)
        return True, "Database restored."
    except Exception as e: return False, str(e)

if __name__ == "__main__":
    init_db()
    print("Database initialized.")