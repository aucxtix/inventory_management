"""
Configuration settings for the Inventory Management System.
Loads from .env file if available, otherwise uses sensible defaults.
"""
import os
from dotenv import load_dotenv

# Load .env file from project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Application
APP_NAME = os.getenv("APP_NAME", "Inventory Management System")
APP_VERSION = os.getenv("APP_VERSION", "2.0.0")

# Database
DB_TYPE = os.getenv("DB_TYPE", "sqlite")
DB_NAME = os.path.join(BASE_DIR, os.getenv("DB_NAME", "inventory.db"))

# Thresholds
LOW_STOCK_THRESHOLD = int(os.getenv("LOW_STOCK_THRESHOLD", "5"))

# Export directory
EXPORT_DIR = os.path.join(BASE_DIR, "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)

# AI & Billing Config
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
CGST_RATE = float(os.getenv("CGST_RATE", "9.0"))
SGST_RATE = float(os.getenv("SGST_RATE", "9.0"))
COMPANY_NAME = os.getenv("COMPANY_NAME", "TechStore Electronics Ltd.")
COMPANY_PHONE = os.getenv("COMPANY_PHONE", "+91-9876543210")
