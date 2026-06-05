import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import sales
import billing
import exports

class SalesView(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="transparent")
        self.main_app = main_app
        self.main_app.set_status("Viewing Invoice History")
        
        # Top Bar
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", pady=10)
        
        ctk.CTkLabel(top_bar, text="Sales & Invoice History", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left", padx=10)
        ctk.CTkButton(top_bar, text="Refresh", command=self.load_data).pack(side="right", padx=10)
        
        # Action Bar
        act_bar = ctk.CTkFrame(self, fg_color="transparent")
        act_bar.pack(fill="x", pady=(0, 10))
        ctk.CTkButton(act_bar, text="Generate PDF for Selected", command=self.generate_pdf).pack(side="left", padx=10)

        # Table Setup
        self.tree_frame = ctk.CTkFrame(self)
        self.tree_frame.pack(fill="both", expand=True)

        columns = ("Invoice ID", "Invoice Number", "Customer Name", "Grand Total ($)", "Payment", "Date")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings")
        for col in columns: self.tree.heading(col, text=col)
        self.tree.column("Invoice ID", width=60)
        
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.load_data()

    def load_data(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for row in sales.get_all_invoices():
            # row: id, inv_no, c_name, total, p_method, date
            row_fmt = list(row)
            row_fmt[2] = row_fmt[2] or "Walk-in"
            row_fmt[3] = f"${row_fmt[3]:.2f}"
            self.tree.insert("", "end", values=row_fmt)

    def generate_pdf(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select", "Please select an invoice first.")
            return
            
        vals = self.tree.item(selected, "values")
        inv_id = vals[0]
        inv_no = vals[1]
        
        path = filedialog.asksaveasfilename(
            initialfile=f"Invoice_{inv_no}.pdf",
            defaultextension=".pdf", 
            filetypes=[("PDF Files", "*.pdf")]
        )
        if not path: return
        
        success, msg = billing.generate_invoice_pdf(inv_id, path)
        if success:
            self.main_app.set_status(msg)
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)
