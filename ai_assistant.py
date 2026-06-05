import requests
import json
from config import GEMINI_API_KEY
import database
import reports

def check_ai_status():
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_api_key_here":
        return False, "Gemini API key is not configured in .env"
    return True, "AI Ready"

def query_gemini(prompt, system_instruction="You are an expert AI business analyst for an Inventory System."):
    """Calls Gemini REST API via standard requests module."""
    status, msg = check_ai_status()
    if not status:
        return f"API Configuration Error: {msg}. Please check your .env file."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": f"System Context: {system_instruction}\n\nUser Request: {prompt}"}]}]
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"API Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Network Error contacting Gemini API: {str(e)}"

def generate_business_summary():
    """Fetches core metrics and asks AI to summarize the business health."""
    metrics = reports.get_dashboard_metrics()
    
    # Fetch low stock items explicitly
    conn = database.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, stock, reorder_level FROM products WHERE stock <= reorder_level")
    low_stock_list = cur.fetchall()
    conn.close()
    
    ls_text = ", ".join([f"{p[0]} (Stock: {p[1]})" for p in low_stock_list]) if low_stock_list else "None"
    
    prompt = f"""
    Here is the current live data of the inventory system:
    - Total Products Catalog: {metrics.get('total_products', 0)}
    - Total Physical Stock Items: {metrics.get('total_stock', 0)}
    - Total Value of Inventory: ${metrics.get('total_value', 0):.2f}
    - Total Lifetime Sales Revenue: ${metrics.get('sales_revenue', 0):.2f}
    - Items that are critically low on stock: {ls_text}
    
    Write a 3-paragraph executive summary addressing the business owner. 
    Point out any risks (like low stock) and provide 2 actionable recommendations. Keep the tone professional.
    """
    
    return query_gemini(prompt)

def get_smart_answer(user_question):
    """Answers general inventory questions using live data context."""
    metrics = reports.get_dashboard_metrics()
    prompt = f"""
    Context Data:
    Total Products: {metrics.get('total_products', 0)} | Total Value: ${metrics.get('total_value', 0):.2f}
    Revenue: ${metrics.get('sales_revenue', 0):.2f} | Out of Stock Items: {metrics.get('out_of_stock', 0)}
    
    User asks: "{user_question}"
    
    Provide a direct, helpful answer. If the question requires data not in the context, politely explain you only see the high-level dashboard metrics right now.
    """
    return query_gemini(prompt)
