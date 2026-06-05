import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import purchases
import products

class PurchasesView(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="transparent")
        self.main_app = main_app
        self.main_app.set_status("Viewing Purchases")
        
        self.setup_form()
        self.setup_table()
        self.load_data()

    def setup_form(self):
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(form_frame, text="Select Product:").pack(side="left", padx=5)
        
        self.prod_list = products.get_product_names_ids()
        self.prod_map = {f"{p[1]} (Stock: {p[2]}) - ${p[3]:.2f}": p[0] for p in self.prod_list}
        values = list(self.prod_map.keys())
        
        self.prod_combo = ctk.CTkComboBox(form_frame, values=values, width=250, command=self.calc_total)
        self.prod_combo.pack(side="left", padx=5)
        if values:
            self.prod_combo.set(values[0])

        ctk.CTkLabel(form_frame, text="Quantity:").pack(side="left", padx=5)
        
        self.qty_var = tk.StringVar(value="1")
        self.qty_var.trace_add("write", self.calc_total)
        self.qty_entry = ctk.CTkEntry(form_frame, width=60, textvariable=self.qty_var)
        self.qty_entry.pack(side="left", padx=5)

        self.total_lbl = ctk.CTkLabel(form_frame, text="Total: $0.00", font=ctk.CTkFont(weight="bold"))
        self.total_lbl.pack(side="left", padx=15)

        ctk.CTkButton(form_frame, text="Record Purchase", command=self.record_purchase).pack(side="right", padx=10)

    def calc_total(self, *args):
        selection = self.prod_combo.get()
        if not selection: return
        
        try:
            price_str = selection.split("-$")[1]
            price = float(price_str)
            qty = int(self.qty_var.get())
            total = price * qty
            self.total_lbl.configure(text=f"Total: ${total:.2f}")
        except:
            self.total_lbl.configure(text="Total: $0.00")

    def setup_table(self):
        self.tree_frame = ctk.CTkFrame(self)
        self.tree_frame.pack(fill="both", expand=True)

        columns = ("Purchase ID", "Product Name", "Quantity", "Total Amount ($)", "Date")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
        
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in purchases.get_all_purchases():
            row_fmt = list(row)
            row_fmt[3] = f"{row[3]:.2f}"
            self.tree.insert("", "end", values=row_fmt)

    def refresh_dropdown(self):
        self.prod_list = products.get_product_names_ids()
        self.prod_map = {f"{p[1]} (Stock: {p[2]}) - ${p[3]:.2f}": p[0] for p in self.prod_list}
        values = list(self.prod_map.keys())
        self.prod_combo.configure(values=values)
        if values:
            self.prod_combo.set(values[0])
        else:
            self.prod_combo.set("")

    def record_purchase(self):
        selection = self.prod_combo.get()
        if not selection or selection not in self.prod_map:
            messagebox.showerror("Error", "Invalid product selection.")
            return
            
        pid = self.prod_map[selection]
        qty = self.qty_var.get()
        
        success, msg = purchases.record_purchase(pid, qty)
        if success:
            self.main_app.set_status(msg)
            self.qty_var.set("1")
            self.load_data()
            self.refresh_dropdown()
        else:
            messagebox.showerror("Error", msg)
