from datetime import datetime
from database import get_connection, log_activity
from auth import Session
from config import CGST_RATE, SGST_RATE

def process_checkout(cart_items, customer_id=None, discount=0.0, payment_method="Cash"):
    """
    Processes a POS cart checkout via an atomic transaction.
    cart_items: list of dicts: [{'product_id': 1, 'qty': 2, 'price': 50.0}, ...]
    Returns (success, msg_or_invoice_id).
    """
    if not cart_items:
        return False, "Cart is empty."

    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Calculate totals
        subtotal = 0.0
        for item in cart_items:
            subtotal += item['qty'] * item['price']
            
        discount = float(discount)
        taxable_amount = max(0, subtotal - discount)
        
        cgst_amt = (taxable_amount * CGST_RATE) / 100.0
        sgst_amt = (taxable_amount * SGST_RATE) / 100.0
        grand_total = taxable_amount + cgst_amt + sgst_amt
        
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Generate Invoice Number (e.g. INV-20261105-001)
        cur.execute("SELECT COUNT(id) FROM invoices")
        count = cur.fetchone()[0] + 1
        date_str = datetime.now().strftime("%Y%m%d")
        invoice_no = f"INV-{date_str}-{count:03d}"

        # 1. Deduct Stock safely
        for item in cart_items:
            pid = item['product_id']
            qty = item['qty']
            
            cur.execute("SELECT name, stock FROM products WHERE id=?", (pid,))
            prod = cur.fetchone()
            if not prod:
                conn.rollback()
                return False, f"Product ID {pid} not found."
                
            if qty > prod[1]:
                conn.rollback()
                return False, f"Insufficient stock for '{prod[0]}'. Only {prod[1]} left."
                
            cur.execute("UPDATE products SET stock = stock - ? WHERE id=? AND stock >= ?", (qty, pid, qty))
            if cur.rowcount == 0:
                conn.rollback()
                return False, f"Stock update failed for '{prod[0]}'. Race condition detected."

        # 2. Create Invoice
        cur.execute("""
            INSERT INTO invoices (invoice_number, customer_id, subtotal, discount, cgst, sgst, grand_total, payment_method, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (invoice_no, customer_id, subtotal, discount, cgst_amt, sgst_amt, grand_total, payment_method, created_at))
        
        invoice_id = cur.lastrowid
        
        # 3. Create Invoice Items
        for item in cart_items:
            amt = item['qty'] * item['price']
            cur.execute("""
                INSERT INTO invoice_items (invoice_id, product_id, qty, rate, amount)
                VALUES (?, ?, ?, ?, ?)
            """, (invoice_id, item['product_id'], item['qty'], item['price'], amt))
            
        conn.commit()
        conn.close()

        user = Session.username or "System"
        log_activity(user, "Sale/Checkout", f"Generated {invoice_no} for ${grand_total:.2f}")

        return True, invoice_id
    except Exception as e:
        return False, str(e)

def get_all_invoices():
    """Returns list of invoices for the GUI."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT i.id, i.invoice_number, c.name, i.grand_total, i.payment_method, i.created_at
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            ORDER BY i.id DESC
        """)
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception:
        return []