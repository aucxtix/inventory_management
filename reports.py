from database import get_connection, get_recent_activity
from config import LOW_STOCK_THRESHOLD

def get_dashboard_metrics():
    """Returns a dict of aggregate stats for the dashboard."""
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*), COALESCE(SUM(stock), 0), COALESCE(SUM(price * stock), 0) FROM products")
        total_products, total_stock, total_value = cur.fetchone()

        cur.execute("SELECT COUNT(*) FROM products WHERE stock <= reorder_level AND stock > 0")
        low_stock = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM products WHERE stock = 0")
        out_of_stock = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*), COALESCE(SUM(grand_total), 0) FROM invoices")
        total_sales, sales_revenue = cur.fetchone()

        cur.execute("SELECT COUNT(*), COALESCE(SUM(total_amount), 0) FROM purchases")
        total_purchases, purchase_cost = cur.fetchone()

        conn.close()

        return {
            "total_products": total_products or 0,
            "total_stock": int(total_stock or 0),
            "total_value": float(total_value or 0.0),
            "low_stock": low_stock or 0,
            "out_of_stock": out_of_stock or 0,
            "total_sales": total_sales or 0,
            "sales_revenue": float(sales_revenue or 0.0),
            "total_purchases": total_purchases or 0,
            "purchase_cost": float(purchase_cost or 0.0),
        }
    except Exception:
        return {
            "total_products": 0, "total_stock": 0, "total_value": 0.0,
            "low_stock": 0, "out_of_stock": 0,
            "total_sales": 0, "sales_revenue": 0.0,
            "total_purchases": 0, "purchase_cost": 0.0,
        }

def get_activity_feed(limit=10):
    """Returns recent activity for the dashboard."""
    return get_recent_activity(limit)
