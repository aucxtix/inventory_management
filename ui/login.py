import customtkinter as ctk
from tkinter import messagebox
import auth

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, show_main_app_callback):
        super().__init__(parent)
        self.show_main_app_callback = show_main_app_callback
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.login_box = ctk.CTkFrame(self, width=350, corner_radius=15)
        self.login_box.grid(row=1, column=1, rowspan=4, pady=20, padx=20, sticky="nsew")

        self.title_lbl = ctk.CTkLabel(self.login_box, text="Inventory Login", font=ctk.CTkFont(size=26, weight="bold"))
        self.title_lbl.pack(pady=(40, 30), padx=20)

        self.username_entry = ctk.CTkEntry(self.login_box, placeholder_text="Username", width=250, height=40)
        self.username_entry.pack(pady=10, padx=20)
        self.username_entry.bind("<Return>", lambda e: self.attempt_login())

        self.password_entry = ctk.CTkEntry(self.login_box, placeholder_text="Password", show="*", width=250, height=40)
        self.password_entry.pack(pady=10, padx=20)
        self.password_entry.bind("<Return>", lambda e: self.attempt_login())

        self.show_pass_var = ctk.BooleanVar(value=False)
        self.show_pass_cb = ctk.CTkCheckBox(self.login_box, text="Show Password", variable=self.show_pass_var, command=self.toggle_password)
        self.show_pass_cb.pack(pady=10, padx=20, anchor="w")

        self.login_btn = ctk.CTkButton(self.login_box, text="Login", command=self.attempt_login, width=250, height=40, font=ctk.CTkFont(weight="bold"))
        self.login_btn.pack(pady=(20, 20), padx=20)
        
        self.version_lbl = ctk.CTkLabel(self.login_box, text="v2.0.0", font=ctk.CTkFont(size=10), text_color="gray")
        self.version_lbl.pack(side="bottom", pady=10)

    def toggle_password(self):
        if self.show_pass_var.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="*")

    def attempt_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        success, msg = auth.login(username, password)
        if success:
            self.show_main_app_callback()
        else:
            messagebox.showerror("Login Failed", msg)
