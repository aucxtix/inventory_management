import sqlite3

def add_product(name, category, supplier, price, stock):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO products(name, category, supplier, price, stock)
    VALUES (?, ?, ?, ?, ?)
    """, (name, category, supplier, price, stock))

    conn.commit()
    conn.close()

    print("Product Added Successfully")

def view_products():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()

    for product in products:
        print(product)

    conn.close()

def delete_product(product_id):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM products WHERE id=?",
        (product_id,)
    )

    conn.commit()
    conn.close()

    print("Product Deleted")

def update_stock(product_id, stock):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE products SET stock=? WHERE id=?",
        (stock, product_id)
    )

    conn.commit()
    conn.close()

    print("Stock Updated")

def search_product(name):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE name LIKE ?",
        ('%' + name + '%',)
    )

    products = cursor.fetchall()

    for product in products:
        print(product)

    conn.close()