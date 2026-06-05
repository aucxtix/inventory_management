import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import exports

class ExportsView(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="transparent")
        self.main_app = main_app
        self.main_app.set_status("Viewing Exports")

        ctk.CTkLabel(self, text="Exports & Reports", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)

        # Create two columns for CSV and PDF
        cols_frame = ctk.CTkFrame(self, fg_color="transparent")
        cols_frame.pack(fill="x", padx=50)
        
        csv_col = ctk.CTkFrame(cols_frame, fg_color="transparent")
        csv_col.pack(side="left", fill="both", expand=True, padx=20)
        
        pdf_col = ctk.CTkFrame(cols_frame, fg_color="transparent")
        pdf_col.pack(side="right", fill="both", expand=True, padx=20)

        ctk.CTkLabel(csv_col, text="CSV Exports", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        ctk.CTkButton(csv_col, text="Export Products (CSV)", command=self.do_prod_csv).pack(pady=10, fill="x")
        ctk.CTkButton(csv_col, text="Export Sales (CSV)", command=self.do_sales_csv).pack(pady=10, fill="x")
        ctk.CTkButton(csv_col, text="Export Purchases (CSV)", command=self.do_purch_csv).pack(pady=10, fill="x")

        ctk.CTkLabel(pdf_col, text="PDF Reports", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        ctk.CTkButton(pdf_col, text="Export Inventory Report (PDF)", command=self.do_inv_pdf).pack(pady=10, fill="x")
        ctk.CTkButton(pdf_col, text="Export Sales Report (PDF)", command=self.do_sales_pdf).pack(pady=10, fill="x")
        ctk.CTkButton(pdf_col, text="Export Purchases Report (PDF)", command=self.do_purchases_pdf).pack(pady=10, fill="x")

    def handle_export(self, func, ext, filetype, default_name="export"):
        timestamp = exports._timestamp()
        suggested = f"{default_name}_{timestamp}{ext}"
        
        path = filedialog.asksaveasfilename(
            initialfile=suggested,
            defaultextension=ext, 
            filetypes=[(filetype, f"*{ext}")]
        )
        if not path: return
        self.main_app.set_status(f"Exporting to {path}...")
        
        def task():
            success, msg = func(path)
            if success:
                self.main_app.set_status(msg)
                messagebox.showinfo("Success", msg)
            else:
                self.main_app.set_status("Export failed.")
                messagebox.showerror("Error", msg)
        
        threading.Thread(target=task, daemon=True).start()

    def do_prod_csv(self): self.handle_export(exports.export_products_csv, ".csv", "CSV Files", "products")
    def do_sales_csv(self): self.handle_export(exports.export_sales_csv, ".csv", "CSV Files", "sales")
    def do_purch_csv(self): self.handle_export(exports.export_purchases_csv, ".csv", "CSV Files", "purchases")
    
    def do_inv_pdf(self): self.handle_export(exports.export_inventory_pdf, ".pdf", "PDF Files", "inventory_report")
    def do_sales_pdf(self): self.handle_export(exports.export_sales_pdf, ".pdf", "PDF Files", "sales_report")
    def do_purchases_pdf(self): self.handle_export(exports.export_purchases_pdf, ".pdf", "PDF Files", "purchases_report")
