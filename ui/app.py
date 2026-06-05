import customtkinter as ctk
from datetime import datetime
import auth

from ui.dashboard import DashboardView
from ui.products import ProductsView
from ui.pos import POSView
from ui.sales import SalesView
from ui.purchases import PurchasesView
from ui.ai_insights import AIInsightsView
from ui.exports import ExportsView
from ui.admin import AdminView

class MainAppFrame(ctk.CTkFrame):
    def __init__(self, parent, logout_callback):
        super().__init__(parent)
        self.logout_callback = logout_callback
        
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar setup
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)

        from config import APP_NAME
        self.logo_lbl = ctk.CTkLabel(self.sidebar, text=APP_NAME, font=ctk.CTkFont(size=18, weight="bold"))
        self.logo_lbl.grid(row=0, column=0, padx=20, pady=(20, 5))

        self.role_lbl = ctk.CTkLabel(self.sidebar, text=f"User: {auth.Session.username}\nRole: {auth.Session.role}", font=ctk.CTkFont(size=12))
        self.role_lbl.grid(row=1, column=0, padx=20, pady=(0, 20))

        # Navigation Buttons
        self.nav_btns = []
        self._add_nav("Dashboard", DashboardView, 2)
        self._add_nav("POS Checkout", POSView, 3)
        self._add_nav("Products", ProductsView, 4)
        self._add_nav("Invoice History", SalesView, 5)

        if auth.Session.role in ["Admin", "Manager"]:
            self._add_nav("Purchases", PurchasesView, 6)
            self._add_nav("Reports & Exports", ExportsView, 7)
            self._add_nav("AI Assistant", AIInsightsView, 8)

        if auth.Session.role == "Admin":
            self._add_nav("Admin Tools", AdminView, 9)

        # Theme Switcher
        self.theme_menu = ctk.CTkOptionMenu(self.sidebar, values=["System", "Light", "Dark"], command=ctk.set_appearance_mode)
        self.theme_menu.grid(row=11, column=0, padx=20, pady=10)

        self.btn_logout = ctk.CTkButton(self.sidebar, text="Logout", fg_color="#c0392b", hover_color="#e74c3c", command=self.do_logout)
        self.btn_logout.grid(row=12, column=0, padx=20, pady=20)

        # Top Header (Clock)
        self.header = ctk.CTkFrame(self, height=40, corner_radius=0)
        self.header.grid(row=0, column=1, sticky="ew")
        self.clock_lbl = ctk.CTkLabel(self.header, text="", font=ctk.CTkFont(size=14))
        self.clock_lbl.pack(side="right", padx=20, pady=10)
        self.update_clock()

        # Main Content Area
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.grid(row=1, column=1, sticky="nsew", padx=20, pady=10)
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)

        # Bottom Status Bar
        self.status_bar = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.status_lbl = ctk.CTkLabel(self.status_bar, text="Ready", font=ctk.CTkFont(size=12))
        self.status_lbl.pack(side="left", padx=10)

        self.current_view = None
        self.show_view(DashboardView)

    def _add_nav(self, text, view_class, row):
        btn = ctk.CTkButton(self.sidebar, text=text, command=lambda: self.show_view(view_class))
        btn.grid(row=row, column=0, padx=20, pady=5)
        self.nav_btns.append(btn)

    def update_clock(self):
        self.clock_lbl.configure(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.after(1000, self.update_clock)

    def set_status(self, text):
        self.status_lbl.configure(text=text)

    def show_view(self, view_class):
        if self.current_view:
            self.current_view.destroy()
        self.current_view = view_class(self.content_area, self)
        self.current_view.grid(row=0, column=0, sticky="nsew")

    def do_logout(self):
        from database import log_activity
        log_activity(auth.Session.username, "Logout", "User logged out.")
        auth.logout()
        self.logout_callback()
