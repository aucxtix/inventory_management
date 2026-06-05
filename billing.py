import os
from datetime import datetime
from config import CGST_RATE, SGST_RATE, COMPANY_NAME, COMPANY_PHONE, EXPORT_DIR
from database import get_connection

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

def generate_invoice_pdf(invoice_id, filepath=None):
    """Generates a professional B2B/B2C GST invoice PDF."""
    if not REPORTLAB_AVAILABLE:
        return False, "ReportLab is not installed."
        
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Fetch Invoice Data
        cur.execute("""
            SELECT i.invoice_number, c.name, c.phone, c.email, i.subtotal, i.discount, 
                   i.cgst, i.sgst, i.grand_total, i.payment_method, i.created_at
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            WHERE i.id = ?
        """, (invoice_id,))
        inv = cur.fetchone()
        
        if not inv:
            return False, "Invoice not found."
            
        inv_no, c_name, c_phone, c_email, subtotal, discount, cgst, sgst, grand_total, p_method, created_at = inv
        
        # Fetch Items
        cur.execute("""
            SELECT p.name, p.sku, ii.qty, ii.rate, ii.amount
            FROM invoice_items ii
            JOIN products p ON ii.product_id = p.id
            WHERE ii.invoice_id = ?
        """, (invoice_id,))
        items = cur.fetchall()
        conn.close()

        if not filepath:
            filename = f"Invoice_{inv_no}.pdf"
            filepath = os.path.join(EXPORT_DIR, filename)

        c = canvas.Canvas(filepath, pagesize=letter)
        
        # HEADER
        c.setFont("Helvetica-Bold", 24)
        c.drawString(50, 750, COMPANY_NAME)
        
        c.setFont("Helvetica", 10)
        c.drawString(50, 735, f"Phone: {COMPANY_PHONE}")
        c.drawString(50, 720, "TAX INVOICE")
        
        # INVOICE META
        c.setFont("Helvetica-Bold", 10)
        c.drawString(400, 750, f"Invoice #: {inv_no}")
        c.setFont("Helvetica", 10)
        c.drawString(400, 735, f"Date: {created_at}")
        c.drawString(400, 720, f"Payment: {p_method}")
        
        # CUSTOMER INFO
        c.line(50, 700, 550, 700)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 680, "Billed To:")
        c.setFont("Helvetica", 10)
        c.drawString(50, 665, c_name or "Walk-in Customer")
        if c_phone: c.drawString(50, 650, f"Phone: {c_phone}")
        if c_email: c.drawString(50, 635, f"Email: {c_email}")
        
        # TABLE HEADER
        y = 600
        c.setFillColorRGB(0.9, 0.9, 0.9)
        c.rect(50, y-5, 500, 20, fill=1)
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(55, y, "Item Description")
        c.drawString(300, y, "SKU")
        c.drawString(380, y, "Qty")
        c.drawString(430, y, "Rate")
        c.drawString(490, y, "Amount")
        
        # ITEMS
        y -= 20
        c.setFont("Helvetica", 10)
        for item in items:
            name, sku, qty, rate, amt = item
            c.drawString(55, y, name[:35] + ("..." if len(name)>35 else ""))
            c.drawString(300, y, sku or "N/A")
            c.drawString(380, y, str(qty))
            c.drawString(430, y, f"${rate:.2f}")
            c.drawString(490, y, f"${amt:.2f}")
            y -= 20
            
            if y < 150:
                c.showPage()
                y = 750
        
        c.line(50, y, 550, y)
        y -= 20
        
        # TOTALS
        c.drawString(400, y, "Subtotal:")
        c.drawString(490, y, f"${subtotal:.2f}")
        y -= 15
        if discount > 0:
            c.drawString(400, y, "Discount:")
            c.drawString(490, y, f"-${discount:.2f}")
            y -= 15
            
        c.drawString(400, y, f"CGST ({CGST_RATE}%):")
        c.drawString(490, y, f"${cgst:.2f}")
        y -= 15
        
        c.drawString(400, y, f"SGST ({SGST_RATE}%):")
        c.drawString(490, y, f"${sgst:.2f}")
        y -= 15
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(400, y-5, "Grand Total:")
        c.drawString(490, y-5, f"${grand_total:.2f}")
        
        # FOOTER
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(50, 50, "Thank you for your business!")
        c.drawString(50, 35, "This is a computer generated invoice and requires no signature.")
        
        c.save()
        return True, f"Invoice saved to {filepath}"
        
    except Exception as e:
        return False, str(e)
