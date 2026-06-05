import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import products
import sales
import billing

class POSView(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="transparent")
        self.main_app = main_app
        self.main_app.set_status("POS Checkout Mode")
        self.cart = {} # {product_id: {'name': str, 'qty': int, 'price': float, 'stock': int}}
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        
        self.setup_catalog()
        self.setup_cart()

    def setup_catalog(self):
        cat_frame = ctk.CTkFrame(self)
        cat_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Search Bar
        search_frame = ctk.CTkFrame(cat_frame, fg_color="transparent")
        search_frame.pack(fill="x", pady=10, padx=10)
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_products)
        ctk.CTkEntry(search_frame, placeholder_text="Search product by name...", textvariable=self.search_var).pack(fill="x")
        
        # Catalog Table
        columns = ("ID", "Name", "Price", "Stock", "SKU")
        self.tree = ttk.Treeview(cat_frame, columns=columns, show="headings")
        for col in columns: self.tree.heading(col, text=col)
        self.tree.column("ID", width=40)
        self.tree.column("Price", width=80)
        self.tree.column("Stock", width=60)
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<Double-1>", self.add_to_cart_event)
        
        self.load_catalog()

    def setup_cart(self):
        cart_frame = ctk.CTkFrame(self)
        cart_frame.grid(row=0, column=1, sticky="nsew")
        
        ctk.CTkLabel(cart_frame, text="Shopping Cart", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        
        self.cart_scroll = ctk.CTkScrollableFrame(cart_frame, fg_color="transparent")
        self.cart_scroll.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Summary
        summary_frame = ctk.CTkFrame(cart_frame, fg_color=("gray85", "gray25"))
        summary_frame.pack(fill="x", padx=10, pady=10)
        
        self.subtotal_lbl = ctk.CTkLabel(summary_frame, text="Subtotal: $0.00")
        self.subtotal_lbl.pack(anchor="e", padx=10, pady=2)
        
        self.tax_lbl = ctk.CTkLabel(summary_frame, text="Taxes (GST 18%): $0.00")
        self.tax_lbl.pack(anchor="e", padx=10, pady=2)
        
        self.total_lbl = ctk.CTkLabel(summary_frame, text="Grand Total: $0.00", font=ctk.CTkFont(weight="bold", size=18))
        self.total_lbl.pack(anchor="e", padx=10, pady=(5,10))
        
        checkout_btn = ctk.CTkButton(cart_frame, text="CHECKOUT", font=ctk.CTkFont(weight="bold", size=16), height=50, command=self.process_checkout)
        checkout_btn.pack(fill="x", padx=10, pady=10)

    def load_catalog(self, data=None):
        for item in self.tree.get_children(): self.tree.delete(item)
        items = data if data is not None else products.get_all_products()
        for item in items:
            # item: 0:id, 1:name, 2:cat, 3:sup, 4:price, 5:stock, 6:reorder, 7:desc, 8:sku
            vals = (item[0], item[1], f"${item[4]:.2f}", item[5], item[8])
            self.tree.insert("", "end", values=vals)

    def filter_products(self, *args):
        query = self.search_var.get()
        if not query: self.load_catalog()
        else: self.load_catalog(products.search_products("name", query))

    def add_to_cart_event(self, event):
        selected = self.tree.focus()
        if not selected: return
        vals = self.tree.item(selected, "values")
        pid = int(vals[0])
        name = vals[1]
        price = float(vals[2].replace("$",""))
        stock = int(vals[3])
        
        if stock <= 0:
            messagebox.showerror("Out of Stock", f"'{name}' is out of stock.")
            return
            
        if pid in self.cart:
            if self.cart[pid]['qty'] < stock:
                self.cart[pid]['qty'] += 1
            else:
                messagebox.showwarning("Limit", "Cannot exceed available stock.")
        else:
            self.cart[pid] = {'name': name, 'price': price, 'qty': 1, 'stock': stock}
            
        self.refresh_cart_ui()

    def change_qty(self, pid, delta):
        if pid not in self.cart: return
        new_qty = self.cart[pid]['qty'] + delta
        if new_qty <= 0:
            del self.cart[pid]
        elif new_qty > self.cart[pid]['stock']:
            messagebox.showwarning("Limit", "Cannot exceed available stock.")
        else:
            self.cart[pid]['qty'] = new_qty
        self.refresh_cart_ui()

    def refresh_cart_ui(self):
        for widget in self.cart_scroll.winfo_children(): widget.destroy()
        
        subtotal = 0.0
        for pid, data in self.cart.items():
            amt = data['qty'] * data['price']
            subtotal += amt
            
            row = ctk.CTkFrame(self.cart_scroll)
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row, text=data['name'][:20]).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"${amt:.2f}").pack(side="right", padx=5)
            
            ctk.CTkButton(row, text="+", width=30, command=lambda p=pid: self.change_qty(p, 1)).pack(side="right", padx=2)
            ctk.CTkLabel(row, text=str(data['qty'])).pack(side="right", padx=5)
            ctk.CTkButton(row, text="-", width=30, command=lambda p=pid: self.change_qty(p, -1)).pack(side="right", padx=2)

        from config import CGST_RATE, SGST_RATE
        tax = subtotal * ((CGST_RATE + SGST_RATE) / 100)
        grand = subtotal + tax
        
        self.subtotal_lbl.configure(text=f"Subtotal: ${subtotal:.2f}")
        self.tax_lbl.configure(text=f"Taxes (GST 18%): ${tax:.2f}")
        self.total_lbl.configure(text=f"Grand Total: ${grand:.2f}")

    def process_checkout(self):
        if not self.cart: return
        
        items_list = [{'product_id': k, 'qty': v['qty'], 'price': v['price']} for k, v in self.cart.items()]
        
        # Simple generic checkout (No specific customer id for demo)
        success, res = sales.process_checkout(items_list, customer_id=1) # 1 is Walk-in Customer
        
        if success:
            invoice_id = res
            self.cart.clear()
            self.refresh_cart_ui()
            self.load_catalog()
            
            if messagebox.askyesno("Success", "Checkout complete! Generate PDF Invoice?"):
                import billing, os, exports
                from config import EXPORT_DIR
                ts = exports._timestamp()
                path = os.path.join(EXPORT_DIR, f"Invoice_Auto_{ts}.pdf")
                ok, msg = billing.generate_invoice_pdf(invoice_id, path)
                if ok: messagebox.showinfo("Saved", msg)
                else: messagebox.showerror("Error", msg)
        else:
            messagebox.showerror("Checkout Failed", res)
