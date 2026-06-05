import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import database
import auth

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
        ctk.CTkButton(db_frame, text="Restore DB", fg_color="#d35400", hover_color="#e67e22", command=self.restore_db).pack(side="left", padx=10, pady=10)

        ctk.CTkLabel(self, text="User Management", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        # Action Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=5)
        ctk.CTkButton(btn_frame, text="Add New User", command=self.add_user_window).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Update Role", command=self.update_role_window).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Reset Password", command=self.reset_password_window).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Delete Selected User", fg_color="#c0392b", hover_color="#e74c3c", command=self.delete_user).pack(side="left", padx=5)

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

    def _get_selected(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select", "Please select a user from the table.")
            return None
        return self.tree.item(selected, "values")

    def add_user_window(self):
        w = ctk.CTkToplevel(self)
        w.title("Add New User")
        w.geometry("300x350")
        w.transient(self)
        w.after(100, w.grab_set)

        ctk.CTkLabel(w, text="Username:").pack(pady=(10,0))
        uname_entry = ctk.CTkEntry(w)
        uname_entry.pack(pady=5)

        ctk.CTkLabel(w, text="Password:").pack(pady=(10,0))
        pwd_entry = ctk.CTkEntry(w, show="*")
        pwd_entry.pack(pady=5)

        ctk.CTkLabel(w, text="Role:").pack(pady=(10,0))
        role_menu = ctk.CTkOptionMenu(w, values=["Admin", "Manager", "Staff"])
        role_menu.pack(pady=5)

        def submit():
            success, msg = database.add_user(uname_entry.get().strip(), pwd_entry.get().strip(), role_menu.get())
            if success:
                self.main_app.set_status(msg)
                self.load_data()
                w.destroy()
            else: messagebox.showerror("Error", msg)

        ctk.CTkButton(w, text="Add User", command=submit).pack(pady=20)

    def update_role_window(self):
        vals = self._get_selected()
        if not vals: return
        uid, uname, curr_role = vals

        w = ctk.CTkToplevel(self)
        w.title(f"Update Role for {uname}")
        w.geometry("300x200")
        w.transient(self)
        w.after(100, w.grab_set)

        ctk.CTkLabel(w, text="New Role:").pack(pady=(20,0))
        role_menu = ctk.CTkOptionMenu(w, values=["Admin", "Manager", "Staff"])
        role_menu.set(curr_role)
        role_menu.pack(pady=10)

        def submit():
            success, msg = database.update_user_role(uid, role_menu.get())
            if success:
                self.main_app.set_status(msg)
                self.load_data()
                w.destroy()
            else: messagebox.showerror("Error", msg)

        ctk.CTkButton(w, text="Update Role", command=submit).pack(pady=20)

    def reset_password_window(self):
        vals = self._get_selected()
        if not vals: return
        uid, uname, _ = vals

        w = ctk.CTkToplevel(self)
        w.title(f"Reset Password for {uname}")
        w.geometry("300x200")
        w.transient(self)
        w.after(100, w.grab_set)

        ctk.CTkLabel(w, text="New Password:").pack(pady=(20,0))
        pwd_entry = ctk.CTkEntry(w, show="*")
        pwd_entry.pack(pady=10)

        def submit():
            success, msg = database.reset_user_password(uid, pwd_entry.get().strip())
            if success:
                self.main_app.set_status(msg)
                w.destroy()
            else: messagebox.showerror("Error", msg)

        ctk.CTkButton(w, text="Reset Password", command=submit).pack(pady=20)

    def delete_user(self):
        vals = self._get_selected()
        if not vals: return
        uid, uname, _ = vals

        if messagebox.askyesno("Confirm", f"Delete user '{uname}'?"):
            success, msg = database.delete_user(uid, auth.Session.user_id)
            if success:
                self.main_app.set_status(msg)
                self.load_data()
            else: messagebox.showerror("Error", msg)

    def backup_db(self):
        import datetime
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("Database Files", "*.db")], initialfile=f"inventory_backup_{ts}.db")
        if path:
            success, msg = database.backup_db(path)
            if success: messagebox.showinfo("Success", msg)
            else: messagebox.showerror("Error", msg)

    def restore_db(self):
        path = filedialog.askopenfilename(filetypes=[("Database Files", "*.db")])
        if path:
            if messagebox.askyesno("Critical Warning", "Are you sure you want to restore the database? This will overwrite ALL current data with the backup file. This cannot be undone."):
                success, msg = database.restore_db(path)
                if success: messagebox.showinfo("Success", msg)
                else: messagebox.showerror("Error", msg)
