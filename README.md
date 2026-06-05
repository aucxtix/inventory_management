# Inventory Management System (with POS & AI)

A production-grade, globally deployable Inventory Management System built with Python 3 and CustomTkinter. The system now features a fully integrated Point-of-Sale (POS) shopping cart, ReportLab GST billing, and an AI Business Assistant powered by Google Gemini.

## Features

- **Point-of-Sale (POS) Checkout**: A dedicated checkout interface featuring a multi-item shopping cart. Processes sales via atomic SQL transactions to ensure stock deduction and invoice generation never desync due to race conditions.
- **Professional GST Billing**: Dynamically generates B2B/B2C Tax Invoices as PDFs using ReportLab. Includes configurable CGST/SGST tax breakdown, SKUs, and auto-calculated grand totals.
- **Gemini AI Business Assistant**: A built-in chat UI that queries the Google Gemini API (`gemini-flash-latest`). It has a read-only context of your live dashboard metrics and can generate 3-paragraph executive summaries covering your total inventory value, revenue, and low-stock warnings.
- **Role-Based Access Control**: Admin, Manager, and Staff roles with strict permissions. Only Admins/Managers can access the AI features and Purchase history.
- **Secure Authentication**: SHA-256 hashed passwords. No plaintext storage.
- **Relational SQLite Architecture**: Rebuilt database schema with Foreign Key constraints spanning `customers`, `invoices`, `invoice_items`, `products`, and `purchases`.
- **Intelligent Demo Seeding**: Launching the app on an empty database instantly seeds a robust tech-store catalog, suppliers, categories, and walk-in customers.
- **Professional GUI**: Modern, scalable dashboard with Light/Dark/System themes, live charts (Matplotlib), and responsive side navigation.
- **Robust Reporting**: Export raw data to CSV or generate professional PDF invoices and reports using ReportLab.
- **Admin Tools**: Built-in SQLite database Backup and Restore functions, user role modification, and password resetting.
- **Cloud/Deployment Ready**: Includes `.env` configuration, `requirements.txt`, and a base `Dockerfile`.

## Tech Stack

- **Language**: Python 3.11+
- **Database**: SQLite (Relational structure via `sqlite3` driver)
- **GUI**: CustomTkinter, Tkinter (ttk)
- **AI Integration**: Google Gemini REST API (`requests`)
- **Data Vis**: Matplotlib
- **PDF Generation**: ReportLab
- **Config**: python-dotenv

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/aucxtix/inventory_management.git
   cd inventory_management
   ```

2. **Set up Virtual Environment (Optional but recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration:**
   Copy `.env.example` to `.env` to customize application settings. Make sure to add your Google AI Studio API key!
   ```bash
   cp .env.example .env
   # Edit .env and insert: GEMINI_API_KEY=your_actual_key_here
   ```

5. **Run the Application:**
   The database will automatically initialize on the first run and seed the default accounts and tech-store products.
   ```bash
   python3 main.py
   ```

## Default Accounts

- **Admin**: `admin` / `admin123`
- **Manager**: `manager` / `manager123`
- **Staff**: `staff` / `staff123`

*Note: It is highly recommended to change these passwords or create new accounts immediately.*

## Architecture & Code Structure

The codebase strictly follows the Single Responsibility Principle:
- `main.py`: Application entry point.
- `database.py`: Core relational SQLite schema, database seeding, and activity logging.
- `ai_assistant.py`: Network logic and prompt engineering for the Gemini API.
- `billing.py`: ReportLab canvas logic for drawing PDF tax invoices.
- `auth.py`: Session and authentication management.
- `config.py`: Environment variable loading (GST rates, API keys, Company Profile).
- `products.py`, `sales.py`, `purchases.py`: Domain logic for specific business actions (POS checkout, stock updates).
- `reports.py`, `exports.py`: Analytics aggregation and file I/O operations.
- `ui/`: Modular directory containing the distinct screens (`pos.py`, `ai_insights.py`, `dashboard.py`, etc.) ensuring no single massive GUI file.

## Docker Deployment

A base `Dockerfile` is included. Note that because this is a desktop GUI application using X11/Tkinter, running it directly inside an isolated Docker container requires setting up an X11 server host or VNC configuration to display the graphical window. The Dockerfile serves as a foundation for CI/CD testing or future web/API migrations.
