import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import products
from config import LOW_STOCK_THRESHOLD

class ProductsView(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="transparent")
        self.main_app = main_app
        self.main_app.set_status("Viewing Products")

        # Top Bar
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))

        self.search_type = ctk.CTkOptionMenu(top_bar, values=["name", "category", "supplier", "sku"])
        self.search_type.pack(side="left", padx=(0, 10))

        # Search as you type
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.search)
        self.search_entry = ctk.CTkEntry(top_bar, placeholder_text="Search...", textvariable=self.search_var, width=250)
        self.search_entry.pack(side="left", padx=(0, 10))

        self.btn_refresh = ctk.CTkButton(top_bar, text="Refresh", command=self.load_data)
        self.btn_refresh.pack(side="right", padx=10)

        # Table Setup
        self.tree_frame = ctk.CTkFrame(self)
        self.tree_frame.pack(fill="both", expand=True)

        self.columns = ("ID", "Name", "Category", "Supplier", "Price", "Stock", "Reorder Level", "Description", "SKU")
        self.tree = ttk.Treeview(self.tree_frame, columns=self.columns, show="headings")
        
        for col in self.columns:
            self.tree.heading(col, text=col)
            w = 50 if col == "ID" else 100
            self.tree.column(col, width=w)
        
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.load_data()

        # Action Buttons
        import auth
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
            # item[5] is stock, item[6] is reorder_level
            if item[5] == 0:
                tags = ('out_of_stock',)
            elif item[5] <= item[6]:
                tags = ('low_stock',)
            self.tree.insert("", "end", values=item, tags=tags)
            
        self.tree.tag_configure('low_stock', background='#ffcccc')
        self.tree.tag_configure('out_of_stock', background='#ff9999', foreground='black')

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

    def _open_form_window(self, title, initial_vals=None):
        w = ctk.CTkToplevel(self)
        w.title(title)
        w.geometry("400x550")
        w.transient(self)
        w.after(100, w.grab_set)

        fields = ["Name", "Category", "Supplier", "Price", "Stock", "Reorder Level", "Description", "SKU"]
        entries = {}
        
        frame = ctk.CTkScrollableFrame(w, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        for i, field in enumerate(fields):
            ctk.CTkLabel(frame, text=field).pack(anchor="w", pady=(5,0))
            e = ctk.CTkEntry(frame, width=300)
            if initial_vals:
                e.insert(0, initial_vals[i+1])
            elif field == "Reorder Level":
                e.insert(0, "5") # default
            elif field in ["Stock", "Price"]:
                e.insert(0, "0")
            e.pack(anchor="w")
            entries[field] = e
            
        def submit():
            try:
                name = entries["Name"].get().strip()
                cat = entries["Category"].get().strip()
                sup = entries["Supplier"].get().strip()
                price = entries["Price"].get()
                stock = entries["Stock"].get()
                rl = entries["Reorder Level"].get()
                desc = entries["Description"].get().strip()
                sku = entries["SKU"].get().strip()

                if initial_vals:
                    success, msg = products.update_product(initial_vals[0], name, cat, sup, price, stock, rl, desc, sku)
                else:
                    success, msg = products.add_product(name, cat, sup, price, stock, rl, desc, sku)
                
                if success:
                    self.main_app.set_status(msg)
                    self.load_data()
                    w.destroy()
                else:
                    messagebox.showerror("Error", msg)
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(frame, text="Save", command=submit, width=300).pack(pady=20)

    def add_product_window(self):
        self._open_form_window("Add Product")

    def update_product_window(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select", "Please select a product to update.")
            return
        item_vals = self.tree.item(selected, "values")
        self._open_form_window("Update Product", initial_vals=item_vals)
