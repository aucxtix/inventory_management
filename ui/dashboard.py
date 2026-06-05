import customtkinter as ctk
import reports

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="transparent")
        self.main_app = main_app
        self.main_app.set_status("Viewing Dashboard")

        self.lbl_title = ctk.CTkLabel(self, text="Dashboard Summary", font=ctk.CTkFont(size=24, weight="bold"))
        self.lbl_title.pack(pady=(10, 20), anchor="w", padx=20)

        # Content split: Cards on top, Charts/Activity below
        self.content_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)

        metrics = reports.get_dashboard_metrics()

        # Cards Frame
        cards_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        cards_frame.pack(fill="x", padx=10)
        
        # Store references for auto-update
        self.metrics_labels = {}
        
        # Row 1
        self.metrics_labels['total_products'] = self.create_card(cards_frame, "Total Products", str(metrics['total_products']), 0, 0)
        self.metrics_labels['total_stock'] = self.create_card(cards_frame, "Total Stock Units", str(metrics['total_stock']), 0, 1)
        self.metrics_labels['total_value'] = self.create_card(cards_frame, "Inventory Value", f"${metrics['total_value']:,.2f}", 0, 2)
        
        # Row 2
        low_color = "red" if metrics['low_stock'] > 0 else "black"
        out_color = "darkred" if metrics['out_of_stock'] > 0 else "black"
        
        self.metrics_labels['low_stock'] = self.create_card(cards_frame, "Low Stock Items", str(metrics['low_stock']), 1, 0, text_color=low_color)
        self.metrics_labels['out_stock'] = self.create_card(cards_frame, "Out of Stock", str(metrics['out_of_stock']), 1, 1, text_color=out_color)
        self.metrics_labels['sales_rev'] = self.create_card(cards_frame, "Sales Revenue", f"${metrics['sales_revenue']:,.2f}", 1, 2, text_color="green")

        # Bottom Frame (Chart and Activity)
        bottom_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        bottom_frame.pack(fill="both", expand=True, pady=20, padx=10)
        
        bottom_frame.grid_columnconfigure(0, weight=2)
        bottom_frame.grid_columnconfigure(1, weight=1)

        # Activity Log Panel
        act_frame = ctk.CTkFrame(bottom_frame)
        act_frame.grid(row=0, column=1, sticky="nsew", padx=10)
        
        ctk.CTkLabel(act_frame, text="Recent Activity", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        act_scroll = ctk.CTkScrollableFrame(act_frame, fg_color="transparent", height=250)
        act_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        activities = reports.get_activity_feed(limit=10)
        if not activities:
            ctk.CTkLabel(act_scroll, text="No recent activity.", text_color="gray").pack(pady=20)
        else:
            for act in activities:
                # act = (username, action, details, timestamp)
                user, action, details, ts = act
                time_str = ts.split()[1][:5] # just HH:MM
                log_text = f"[{time_str}] {user} ({action}):\n{details}"
                lbl = ctk.CTkLabel(act_scroll, text=log_text, justify="left", anchor="w", font=ctk.CTkFont(size=12))
                lbl.pack(fill="x", pady=5)

        # Chart Panel
        if MATPLOTLIB_AVAILABLE:
            chart_frame = ctk.CTkFrame(bottom_frame)
            chart_frame.grid(row=0, column=0, sticky="nsew", padx=10)
            
            fig = Figure(figsize=(5, 3), dpi=100)
            ax = fig.add_subplot(111)
            
            # Simple bar chart of top 5 products by stock
            import products
            prods = products.get_all_products()
            # Sort by stock descending (index 5 is stock)
            prods.sort(key=lambda x: x[5], reverse=True)
            top_prods = prods[:5]
            names = [p[1][:15]+"..." if len(p[1])>15 else p[1] for p in top_prods]
            stocks = [p[5] for p in top_prods]
            
            if names:
                ax.bar(names, stocks, color='#3b8ed0')
                ax.set_title("Top 5 Products by Stock Volume", fontsize=12)
                ax.set_ylabel("Stock Quantity")
                ax.tick_params(axis='x', rotation=45)
                fig.tight_layout()
                
                canvas = FigureCanvasTkAgg(fig, master=chart_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Start auto-refresh
        self.refresh_data()

    def refresh_data(self):
        try:
            metrics = reports.get_dashboard_metrics()
            self.metrics_labels['total_products'].configure(text=str(metrics['total_products']))
            self.metrics_labels['total_stock'].configure(text=str(metrics['total_stock']))
            self.metrics_labels['total_value'].configure(text=f"${metrics['total_value']:,.2f}")
            
            low_color = "red" if metrics['low_stock'] > 0 else "black"
            out_color = "darkred" if metrics['out_of_stock'] > 0 else "black"
            
            self.metrics_labels['low_stock'].configure(text=str(metrics['low_stock']), text_color=low_color)
            self.metrics_labels['out_stock'].configure(text=str(metrics['out_of_stock']), text_color=out_color)
            self.metrics_labels['sales_rev'].configure(text=f"${metrics['sales_revenue']:,.2f}")
        except Exception:
            pass
        self.after(15000, self.refresh_data) # refresh every 15 seconds

    def create_card(self, parent, title, value, row, col, text_color=None):
        card = ctk.CTkFrame(parent, corner_radius=10, fg_color=("gray85", "gray25"))
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)

        lbl_t = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14, weight="bold"))
        lbl_t.pack(pady=(15, 5), padx=20)
        
        t_color = text_color if text_color else ("black", "white")

        lbl_v = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=24, weight="bold"), text_color=t_color)
        lbl_v.pack(pady=(0, 15), padx=20)
        return lbl_v
