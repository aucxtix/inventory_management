# Inventory Management System

A simple, role-based console application for managing an inventory system. Built with Python and SQLite3, it provides features like authentication, access control (Admin, Manager, Staff), and basic product management.

## Features

*   **Role-Based Access Control**:
    *   **Admin**: Full access (Add, View, Search, Delete products).
    *   **Manager**: Partial access (Add, View, Search products).
    *   **Staff**: Read-only access (View, Search products).
*   **Product Management**: Add new products, view inventory, search by name, and delete items.
*   **Persistent Storage**: All data is securely stored locally using an SQLite database (`inventory.db`).

## Setup & Installation

**1. Clone the repository** (if you haven't already):
```bash
git clone https://github.com/aucxtix/inventory_management.git
cd inventory_management
```

**2. Initialize the Database**:
This will create the necessary tables (`users`, `products`, `sales`, `purchases`) inside `inventory.db`.
```bash
python3 database.py
```

**3. Create the Default User**:
This script creates a default Admin user so you can log in for the first time.
```bash
python3 test.py
```

## How to Run

Start the application by running the main entry point:
```bash
python3 main.py
```

You will be prompted to log in. You can use the default credentials generated in the previous step:
*   **Username**: `admin`
*   **Password**: `1234`

From there, simply follow the on-screen menu to manage your inventory!

## Project Structure

*   `main.py` - Application entry point and role-based menu loop.
*   `database.py` - Database schema definition and initialization.
*   `auth.py` - Handles user authentication.
*   `products.py` - Contains all product-related CRUD operations.
*   `test.py` - Helper script to insert the initial admin user.
