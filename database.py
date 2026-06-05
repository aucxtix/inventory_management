import sqlite3

cnt = sqlite3.connect("inventory.db")
cursor = cnt.cursor()

# Users Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password VARCHAR(20) NOT NULL,
    role VARCHAR(20) NOT NULL
)
""")

# Products Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS products(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    supplier TEXT,
    price REAL,
    stock INTEGER
)
""")

# Sales Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    quantity INTEGER,
    sale_date TEXT
)
""")

# Purchases Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS purchases(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    quantity INTEGER,
    purchase_date TEXT
)
""")

cnt.commit()

print("All Tables Created Successfully")

cnt.close()