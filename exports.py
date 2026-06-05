import csv
import os
from datetime import datetime
from database import get_connection

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

def _timestamp():
    """Returns a filesystem-safe timestamp string."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def export_products_csv(filepath):
    if not filepath:
        return False, "No file selected."
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, category, supplier, price, stock, reorder_level, sku FROM products")
        rows = cur.fetchall()
        conn.close()

        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Name", "Category", "Supplier", "Price", "Stock", "Reorder Level", "SKU"])
            writer.writerows(rows)
        return True, f"Products exported to {os.path.basename(filepath)}"
    except Exception as e:
        return False, str(e)

def export_sales_csv(filepath):
    if not filepath:
        return False, "No file selected."
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT s.id, p.name, s.quantity, s.total_amount, s.customer_name, s.sale_date "
            "FROM sales s JOIN products p ON s.product_id = p.id ORDER BY s.id DESC"
        )
        rows = cur.fetchall()
        conn.close()

        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Sale ID", "Product", "Qty", "Total", "Customer", "Date"])
            writer.writerows(rows)
        return True, f"Sales exported to {os.path.basename(filepath)}"
    except Exception as e:
        return False, str(e)

def export_purchases_csv(filepath):
    if not filepath:
        return False, "No file selected."
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT pu.id, p.name, pu.quantity, pu.total_amount, pu.purchase_date "
            "FROM purchases pu JOIN products p ON pu.product_id = p.id ORDER BY pu.id DESC"
        )
        rows = cur.fetchall()
        conn.close()

        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Purchase ID", "Product", "Qty", "Total", "Date"])
            writer.writerows(rows)
        return True, f"Purchases exported to {os.path.basename(filepath)}"
    except Exception as e:
        return False, str(e)

def _make_pdf_header(c, title, y=750):
    """Draws a standard PDF header and returns the starting y position."""
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, title)
    c.setFont("Helvetica", 10)
    c.drawString(50, y - 15, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    c.line(50, y - 20, 560, y - 20)
    return y - 40

def export_inventory_pdf(filepath):
    if not filepath:
        return False, "No file selected."
    if not REPORTLAB_AVAILABLE:
        return False, "ReportLab is not installed."
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, category, supplier, stock, price FROM products ORDER BY name")
        rows = cur.fetchall()
        conn.close()

        c = canvas.Canvas(filepath, pagesize=letter)
        y = _make_pdf_header(c, "Inventory Report")
        c.setFont("Helvetica", 9)

        for row in rows:
            line = f"ID: {row[0]}  |  {row[1]}  |  Cat: {row[2]}  |  Sup: {row[3]}  |  Stock: {row[4]}  |  Price: ${row[5]:.2f}"
            c.drawString(50, y, line)
            y -= 18
            if y < 50:
                c.showPage()
                y = _make_pdf_header(c, "Inventory Report (cont.)")
                c.setFont("Helvetica", 9)

        c.save()
        return True, f"Inventory PDF exported to {os.path.basename(filepath)}"
    except Exception as e:
        return False, str(e)

def export_sales_pdf(filepath):
    if not filepath:
        return False, "No file selected."
    if not REPORTLAB_AVAILABLE:
        return False, "ReportLab is not installed."
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT s.id, p.name, s.quantity, s.total_amount, s.sale_date "
            "FROM sales s JOIN products p ON s.product_id = p.id ORDER BY s.id DESC"
        )
        rows = cur.fetchall()
        conn.close()

        c = canvas.Canvas(filepath, pagesize=letter)
        y = _make_pdf_header(c, "Sales Report")
        c.setFont("Helvetica", 9)

        for row in rows:
            line = f"Sale #{row[0]}  |  {row[1]}  |  Qty: {row[2]}  |  Total: ${row[3]:.2f}  |  {row[4]}"
            c.drawString(50, y, line)
            y -= 18
            if y < 50:
                c.showPage()
                y = _make_pdf_header(c, "Sales Report (cont.)")
                c.setFont("Helvetica", 9)

        c.save()
        return True, f"Sales PDF exported to {os.path.basename(filepath)}"
    except Exception as e:
        return False, str(e)

def export_purchases_pdf(filepath):
    if not filepath:
        return False, "No file selected."
    if not REPORTLAB_AVAILABLE:
        return False, "ReportLab is not installed."
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT pu.id, p.name, pu.quantity, pu.total_amount, pu.purchase_date "
            "FROM purchases pu JOIN products p ON pu.product_id = p.id ORDER BY pu.id DESC"
        )
        rows = cur.fetchall()
        conn.close()

        c = canvas.Canvas(filepath, pagesize=letter)
        y = _make_pdf_header(c, "Purchases Report")
        c.setFont("Helvetica", 9)

        for row in rows:
            line = f"Purchase #{row[0]}  |  {row[1]}  |  Qty: {row[2]}  |  Total: ${row[3]:.2f}  |  {row[4]}"
            c.drawString(50, y, line)
            y -= 18
            if y < 50:
                c.showPage()
                y = _make_pdf_header(c, "Purchases Report (cont.)")
                c.setFont("Helvetica", 9)

        c.save()
        return True, f"Purchases PDF exported to {os.path.basename(filepath)}"
    except Exception as e:
        return False, str(e)
