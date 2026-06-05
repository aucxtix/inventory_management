import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
from datetime import datetime
import threading

import auth
import products
import sales
import purchases
import reports
import exports
import database
from config import LOW_STOCK_THRESHOLD

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Inventory Management System")
        self.geometry("1100x700")
        self.minsize(900, 600)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.current_frame = None
        self.show_login()

    def show_login(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = LoginFrame(self)
        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def show_main_app(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = MainAppFrame(self)
        self.current_frame.grid(row=0, column=0, sticky="nsew")


class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.login_box = ctk.CTkFrame(self, width=300, corner_radius=15)
        self.login_box.grid(row=1, column=1, rowspan=4, pady=20, padx=20, sticky="nsew")

        self.title_lbl = ctk.CTkLabel(self.login_box, text="Inventory Login", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_lbl.pack(pady=(30, 20), padx=20)

        self.username_entry = ctk.CTkEntry(self.login_box, placeholder_text="Username", width=200)
        self.username_entry.pack(pady=10, padx=20)

        self.password_entry = ctk.CTkEntry(self.login_box, placeholder_text="Password", show="*", width=200)
        self.password_entry.pack(pady=10, padx=20)

        self.show_pass_var = ctk.BooleanVar(value=False)
        self.show_pass_cb = ctk.CTkCheckBox(self.login_box, text="Show Password", variable=self.show_pass_var, command=self.toggle_password)
        self.show_pass_cb.pack(pady=10, padx=20, anchor="w")

        self.login_btn = ctk.CTkButton(self.login_box, text="Login", command=self.attempt_login, width=200)
        self.login_btn.pack(pady=(20, 30), padx=20)

    def toggle_password(self):
        if self.show_pass_var.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="*")

    def attempt_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        success, msg = auth.login(username, password)
        if success:
            self.parent.show_main_app()
        else:
            messagebox.showerror("Login Failed", msg)


class MainAppFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_rowconfigure(9, weight=1)

        self.logo_lbl = ctk.CTkLabel(self.sidebar, text="Inventory App", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_lbl.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.role_lbl = ctk.CTkLabel(self.sidebar, text=f"{auth.Session.username} ({auth.Session.role})", font=ctk.CTkFont(size=14))
        self.role_lbl.grid(row=1, column=0, padx=20, pady=(0, 20))

        # Navigation
        self.btn_dashboard = ctk.CTkButton(self.sidebar, text="Dashboard", command=lambda: self.show_view(DashboardView))
        self.btn_dashboard.grid(row=2, column=0, padx=20, pady=5)

        self.btn_products = ctk.CTkButton(self.sidebar, text="Products", command=lambda: self.show_view(ProductsView))
        self.btn_products.grid(row=3, column=0, padx=20, pady=5)

        self.btn_sales = ctk.CTkButton(self.sidebar, text="Sales", command=lambda: self.show_view(SalesView))
        self.btn_sales.grid(row=4, column=0, padx=20, pady=5)

        if auth.Session.role in ["Admin", "Manager"]:
            self.btn_purchases = ctk.CTkButton(self.sidebar, text="Purchases", command=lambda: self.show_view(PurchasesView))
            self.btn_purchases.grid(row=5, column=0, padx=20, pady=5)

            self.btn_exports = ctk.CTkButton(self.sidebar, text="Reports/Exports", command=lambda: self.show_view(ExportsView))
            self.btn_exports.grid(row=6, column=0, padx=20, pady=5)

        if auth.Session.role == "Admin":
            self.btn_users = ctk.CTkButton(self.sidebar, text="Admin Tools", command=lambda: self.show_view(AdminView))
            self.btn_users.grid(row=7, column=0, padx=20, pady=5)

        # Theme Switcher
        self.theme_menu = ctk.CTkOptionMenu(self.sidebar, values=["Light", "Dark", "System"], command=self.change_theme)
        self.theme_menu.grid(row=10, column=0, padx=20, pady=10)
        self.theme_menu.set("Light")

        self.btn_logout = ctk.CTkButton(self.sidebar, text="Logout", fg_color="red", hover_color="darkred", command=self.logout)
        self.btn_logout.grid(row=11, column=0, padx=20, pady=20)

        # Top Header (Clock)
        self.header = ctk.CTkFrame(self, height=40, corner_radius=0)
        self.header.grid(row=0, column=1, sticky="ew")
        self.clock_lbl = ctk.CTkLabel(self.header, text="", font=ctk.CTkFont(size=14))
        self.clock_lbl.pack(side="right", padx=20, pady=10)
        self.update_clock()

        # Content Area
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.grid(row=1, column=1, sticky="nsew", padx=20, pady=10)
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)

        # Status Bar
        self.status_bar = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.status_lbl = ctk.CTkLabel(self.status_bar, text="Ready", font=ctk.CTkFont(size=12))
        self.status_lbl.pack(side="left", padx=10)

        self.current_view = None
        self.show_view(DashboardView)

    def update_clock(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.clock_lbl.configure(text=now)
        self.after(1000, self.update_clock)

    def change_theme(self, new_theme):
        ctk.set_appearance_mode(new_theme)

    def set_status(self, text):
        self.status_lbl.configure(text=text)

    def show_view(self, view_class):
        if self.current_view:
            self.current_view.destroy()
        self.current_view = view_class(self.content_area, self)
        self.current_view.grid(row=0, column=0, sticky="nsew")

    def logout(self):
        auth.logout()
        self.parent.show_login()


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="transparent")
        self.main_app = main_app
        self.main_app.set_status("Viewing Dashboard")

        self.lbl_title = ctk.CTkLabel(self, text="Dashboard Summary", font=ctk.CTkFont(size=24, weight="bold"))
        self.lbl_title.pack(pady=10)

        metrics = reports.get_dashboard_metrics()

        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", pady=20)

        self.create_card(cards_frame, "Total Products", str(metrics['total_products']), 0, 0)
        self.create_card(cards_frame, "Inventory Value", f"${metrics['total_value']:,.2f}", 0, 1)
        self.create_card(cards_frame, "Low Stock Items", str(metrics['low_stock']), 0, 2, text_color="red" if metrics['low_stock']>0 else "black")
        self.create_card(cards_frame, "Total Sales", str(metrics['total_sales']), 1, 0)
        self.create_card(cards_frame, "Total Purchases", str(metrics['total_purchases']), 1, 1)

        # Chart
        if MATPLOTLIB_AVAILABLE:
            chart_frame = ctk.CTkFrame(self)
            chart_frame.pack(fill="both", expand=True, pady=10)
            
            fig = Figure(figsize=(5, 3), dpi=100)
            ax = fig.add_subplot(111)
            
            prods = products.get_all_products()
            # Sort by stock descending, take top 5
            prods.sort(key=lambda x: x[5], reverse=True)
            top_prods = prods[:5]
            names = [p[1] for p in top_prods]
            stocks = [p[5] for p in top_prods]
            
            if names:
                ax.bar(names, stocks, color='skyblue')
                ax.set_title("Top 5 Products by Stock Volume")
                ax.set_ylabel("Stock Quantity")
                
                canvas = FigureCanvasTkAgg(fig, master=chart_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True)

    def create_card(self, parent, title, value, row, col, text_color="black"):
        card = ctk.CTkFrame(parent, corner_radius=10)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)

        lbl_t = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14))
        lbl_t.pack(pady=(15, 0), padx=20)

        lbl_v = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=22, weight="bold"), text_color=text_color)
        lbl_v.pack(pady=(5, 15), padx=20)


class ProductsView(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="transparent")
        self.main_app = main_app
        self.main_app.set_status("Viewing Products")

        # Top Bar
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))

        self.search_type = ctk.CTkOptionMenu(top_bar, values=["name", "category", "supplier"])
        self.search_type.pack(side="left", padx=(0, 10))

        # Search as you type
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.search)
        self.search_entry = ctk.CTkEntry(top_bar, placeholder_text="Search...", textvariable=self.search_var, width=200)
        self.search_entry.pack(side="left", padx=(0, 10))

        self.btn_refresh = ctk.CTkButton(top_bar, text="Refresh", command=self.load_data)
        self.btn_refresh.pack(side="right", padx=10)

        # Table Setup
        self.tree_frame = ctk.CTkFrame(self)
        self.tree_frame.pack(fill="both", expand=True)

        columns = ("ID", "Name", "Category", "Supplier", "Price", "Stock")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.load_data()

        # Action Buttons
        if auth.Session.role in ["Admin", "Manager"]:
            act_bar = ctk.CTkFrame(self, fg_color="transparent")
            act_bar.pack(fill="x", pady=(10, 0))

            ctk.CTkButton(act_bar, text="Add Product", command=self.add_product_window).pack(side="left", padx=5)
            ctk.CTkButton(act_bar, text="Update Selected", command=self.update_product_window).pack(side="left", padx=5)
            if auth.Session.role == "Admin":
                ctk.CTkButton(act_bar, text="Delete Selected", fg_color="red", command=self.delete_product).pack(side="left", padx=5)

    def load_data(self, data=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        items = data if data is not None else products.get_all_products()
        for item in items:
            tags = ()
            if item[5] <= LOW_STOCK_THRESHOLD:
                tags = ('low_stock',)
            self.tree.insert("", "end", values=item, tags=tags)
            
        self.tree.tag_configure('low_stock', background='lightcoral')

    def search(self, *args):
        query = self.search_var.get()
        if not query:
            self.load_data()
            return
        res = products.search_products(self.search_type.get(), query)
        self.load_data(res)

    def delete_product(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select", "Please select a product to delete.")
            return
        item_vals = self.tree.item(selected, "values")
        pid = item_vals[0]
        
        if messagebox.askyesno("Confirm", f"Delete product {item_vals[1]}?"):
            success, msg = products.delete_product(pid)
            if success:
                self.main_app.set_status(msg)
                self.load_data()
            else:
                messagebox.showerror("Error", msg)

    def add_product_window(self):
        w = ctk.CTkToplevel(self)
        w.title("Add Product")
        w.geometry("400x400")
        w.transient(self)

        entries = {}
        for i, field in enumerate(["Name", "Category", "Supplier", "Price", "Stock"]):
            ctk.CTkLabel(w, text=field).pack(pady=(10,0))
            e = ctk.CTkEntry(w)
            e.pack()
            entries[field] = e
            
        def submit():
            success, msg = products.add_product(
                entries["Name"].get(), entries["Category"].get(),
                entries["Supplier"].get(), entries["Price"].get(), entries["Stock"].get()
            )
            if success:
                self.main_app.set_status(msg)
                self.load_data()
                w.destroy()
            else:
                messagebox.showerror("Error", msg)

        ctk.CTkButton(w, text="Submit", command=submit).pack(pady=20)

    def update_product_window(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select", "Please select a product to update.")
            return
        item_vals = self.tree.item(selected, "values")

        w = ctk.CTkToplevel(self)
        w.title("Update Product")
        w.geometry("400x400")
        w.transient(self)

        entries = {}
        fields = ["Name", "Category", "Supplier", "Price", "Stock"]
        for i, field in enumerate(fields):
            ctk.CTkLabel(w, text=field).pack(pady=(5,0))
            e = ctk.CTkEntry(w)
            e.insert(0, item_vals[i+1])
            e.pack()
            entries[field] = e
            
        def submit():
            success, msg = products.update_product(
                item_vals[0], entries["Name"].get(), entries["Category"].get(),
                entries["Supplier"].get(), entries["Price"].get(), entries["Stock"].get()
            )
            if success:
                self.main_app.set_status(msg)
                self.load_data()
                w.destroy()
            else:
                messagebox.showerror("Error", msg)

        ctk.CTkButton(w, text="Update", command=submit).pack(pady=20)


class SalesView(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="transparent")
        self.main_app = main_app
        self.main_app.set_status("Viewing Sales")
        
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(form_frame, text="Product ID:").pack(side="left", padx=5)
        self.pid_entry = ctk.CTkEntry(form_frame, width=100)
        self.pid_entry.pack(side="left", padx=5)

        ctk.CTkLabel(form_frame, text="Quantity:").pack(side="left", padx=5)
        self.qty_entry = ctk.CTkEntry(form_frame, width=100)
        self.qty_entry.pack(side="left", padx=5)

        ctk.CTkButton(form_frame, text="Record Sale", command=self.record_sale).pack(side="left", padx=20)

        self.tree_frame = ctk.CTkFrame(self)
        self.tree_frame.pack(fill="both", expand=True)

        columns = ("Sale ID", "Product Name", "Quantity", "Date")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
        
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.load_data()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in sales.get_all_sales():
            self.tree.insert("", "end", values=row)

    def record_sale(self):
        pid = self.pid_entry.get()
        qty = self.qty_entry.get()
        success, msg = sales.record_sale(pid, qty)
        if success:
            self.main_app.set_status(msg)
            self.pid_entry.delete(0, 'end')
            self.qty_entry.delete(0, 'end')
            self.load_data()
        else:
            messagebox.showerror("Error", msg)

class PurchasesView(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="transparent")
        self.main_app = main_app
        self.main_app.set_status("Viewing Purchases")
        
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(form_frame, text="Product ID:").pack(side="left", padx=5)
        self.pid_entry = ctk.CTkEntry(form_frame, width=100)
        self.pid_entry.pack(side="left", padx=5)

        ctk.CTkLabel(form_frame, text="Quantity:").pack(side="left", padx=5)
        self.qty_entry = ctk.CTkEntry(form_frame, width=100)
        self.qty_entry.pack(side="left", padx=5)

        ctk.CTkButton(form_frame, text="Record Purchase", command=self.record_purch).pack(side="left", padx=20)

        self.tree_frame = ctk.CTkFrame(self)
        self.tree_frame.pack(fill="both", expand=True)

        columns = ("Purchase ID", "Product Name", "Quantity", "Date")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
        
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.load_data()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in purchases.get_all_purchases():
            self.tree.insert("", "end", values=row)

    def record_purch(self):
        pid = self.pid_entry.get()
        qty = self.qty_entry.get()
        success, msg = purchases.record_purchase(pid, qty)
        if success:
            self.main_app.set_status(msg)
            self.pid_entry.delete(0, 'end')
            self.qty_entry.delete(0, 'end')
            self.load_data()
        else:
            messagebox.showerror("Error", msg)


class ExportsView(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="transparent")
        self.main_app = main_app
        self.main_app.set_status("Viewing Exports")

        ctk.CTkLabel(self, text="Exports & Reports", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack()

        ctk.CTkButton(btn_frame, text="Export Products (CSV)", command=self.do_prod_csv).pack(pady=10)
        ctk.CTkButton(btn_frame, text="Export Sales (CSV)", command=self.do_sales_csv).pack(pady=10)
        ctk.CTkButton(btn_frame, text="Export Purchases (CSV)", command=self.do_purch_csv).pack(pady=10)
        ctk.CTkButton(btn_frame, text="Export Inventory Report (PDF)", command=self.do_inv_pdf).pack(pady=10)

    def handle_export(self, func, ext, filetype):
        path = filedialog.asksaveasfilename(defaultextension=ext, filetypes=[(filetype, f"*{ext}")])
        if not path: return
        self.main_app.set_status(f"Exporting to {path}...")
        
        # Run export in background so UI doesn't freeze
        def task():
            success, msg = func(path)
            if success:
                self.main_app.set_status("Export successful.")
                messagebox.showinfo("Success", msg)
            else:
                self.main_app.set_status("Export failed.")
                messagebox.showerror("Error", msg)
        
        threading.Thread(target=task).start()

    def do_prod_csv(self): self.handle_export(exports.export_products_csv, ".csv", "CSV Files")
    def do_sales_csv(self): self.handle_export(exports.export_sales_csv, ".csv", "CSV Files")
    def do_purch_csv(self): self.handle_export(exports.export_purchases_csv, ".csv", "CSV Files")
    def do_inv_pdf(self): self.handle_export(exports.export_inventory_pdf, ".pdf", "PDF Files")


class AdminView(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="transparent")
        self.main_app = main_app
        self.main_app.set_status("Viewing Admin Tools")

        # Top section for DB management
        db_frame = ctk.CTkFrame(self)
        db_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(db_frame, text="Database Management").pack(side="left", padx=10)
        ctk.CTkButton(db_frame, text="Backup DB", command=self.backup_db).pack(side="left", padx=10, pady=10)
        ctk.CTkButton(db_frame, text="Restore DB", fg_color="orange", hover_color="darkorange", command=self.restore_db).pack(side="left", padx=10, pady=10)

        ctk.CTkLabel(self, text="User Management", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        # Form
        form = ctk.CTkFrame(self)
        form.pack(fill="x", pady=10)

        ctk.CTkLabel(form, text="Username:").pack(side="left", padx=5)
        self.uname_entry = ctk.CTkEntry(form, width=100)
        self.uname_entry.pack(side="left", padx=5)

        ctk.CTkLabel(form, text="Password:").pack(side="left", padx=5)
        self.pwd_entry = ctk.CTkEntry(form, width=100, show="*")
        self.pwd_entry.pack(side="left", padx=5)

        ctk.CTkLabel(form, text="Role:").pack(side="left", padx=5)
        self.role_menu = ctk.CTkOptionMenu(form, values=["Admin", "Manager", "Staff"])
        self.role_menu.pack(side="left", padx=5)

        ctk.CTkButton(form, text="Add User", command=self.add_user).pack(side="left", padx=10)
        ctk.CTkButton(form, text="Delete User", fg_color="red", command=self.delete_user).pack(side="left", padx=10)

        # Table
        self.tree_frame = ctk.CTkFrame(self)
        self.tree_frame.pack(fill="both", expand=True)

        columns = ("ID", "Username", "Role")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings")
        for col in columns: self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True)

        self.load_data()

    def load_data(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for row in database.get_all_users():
            self.tree.insert("", "end", values=row)

    def add_user(self):
        success, msg = database.add_user(self.uname_entry.get(), self.pwd_entry.get(), self.role_menu.get())
        if success:
            self.main_app.set_status(msg)
            self.load_data()
        else: messagebox.showerror("Error", msg)

    def delete_user(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select", "Please select a user to delete.")
            return
        uid = self.tree.item(selected, "values")[0]
        if messagebox.askyesno("Confirm", "Delete this user?"):
            success, msg = database.delete_user(uid, auth.Session.user_id)
            if success:
                self.main_app.set_status(msg)
                self.load_data()
            else: messagebox.showerror("Error", msg)

    def backup_db(self):
        path = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("Database Files", "*.db")], initialfile="inventory_backup.db")
        if path:
            success, msg = database.backup_db(path)
            if success: messagebox.showinfo("Success", msg)
            else: messagebox.showerror("Error", msg)

    def restore_db(self):
        path = filedialog.askopenfilename(filetypes=[("Database Files", "*.db")])
        if path:
            if messagebox.askyesno("Confirm", "Are you sure you want to restore the database? This will overwrite all current data."):
                success, msg = database.restore_db(path)
                if success: messagebox.showinfo("Success", msg)
                else: messagebox.showerror("Error", msg)
