import customtkinter as ctk
import threading
from tkinter import messagebox
import ai_assistant

class AIInsightsView(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="transparent")
        self.main_app = main_app
        self.main_app.set_status("AI Assistant Active")
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=10)
        
        ctk.CTkLabel(header, text="✨ Gemini Business Assistant", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left", padx=20)
        
        # Status Check
        ok, msg = ai_assistant.check_ai_status()
        color = "green" if ok else "red"
        ctk.CTkLabel(header, text=f"Status: {msg}", text_color=color).pack(side="right", padx=20)
        
        # Chat History
        self.textbox = ctk.CTkTextbox(self, wrap="word", font=ctk.CTkFont(size=14))
        self.textbox.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.textbox.insert("end", "Welcome to the AI Assistant! Ask me about your inventory, sales, or business health.\n\n")
        self.textbox.configure(state="disabled")
        
        # Input Area
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        input_frame.grid_columnconfigure(0, weight=1)
        
        self.query_var = ctk.StringVar()
        self.entry = ctk.CTkEntry(input_frame, textvariable=self.query_var, placeholder_text="e.g., Summarize my business health, or What should I reorder?", height=40)
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0,10))
        self.entry.bind("<Return>", lambda e: self.send_query())
        
        self.btn_send = ctk.CTkButton(input_frame, text="Ask AI", width=100, height=40, command=self.send_query)
        self.btn_send.grid(row=0, column=1)

        self.btn_summary = ctk.CTkButton(input_frame, text="Auto Summary", fg_color="#8e44ad", hover_color="#9b59b6", width=120, height=40, command=self.auto_summary)
        self.btn_summary.grid(row=0, column=2, padx=10)

    def _append_text(self, text):
        self.textbox.configure(state="normal")
        self.textbox.insert("end", text + "\n")
        self.textbox.see("end")
        self.textbox.configure(state="disabled")

    def send_query(self):
        query = self.query_var.get().strip()
        if not query: return
        self.query_var.set("")
        
        self._append_text(f"👤 You: {query}")
        self.btn_send.configure(state="disabled")
        self.main_app.set_status("AI is thinking...")
        
        def task():
            res = ai_assistant.get_smart_answer(query)
            self.after(0, lambda: self._append_text(f"🤖 Gemini: {res}\n"))
            self.after(0, lambda: self.btn_send.configure(state="normal"))
            self.after(0, lambda: self.main_app.set_status("AI Ready"))
            
        threading.Thread(target=task, daemon=True).start()

    def auto_summary(self):
        self._append_text("👤 You: Generate a full business executive summary.")
        self.btn_summary.configure(state="disabled")
        self.main_app.set_status("Generating complex AI summary...")
        
        def task():
            res = ai_assistant.generate_business_summary()
            self.after(0, lambda: self._append_text(f"🤖 Gemini: \n{res}\n"))
            self.after(0, lambda: self.btn_summary.configure(state="normal"))
            self.after(0, lambda: self.main_app.set_status("AI Ready"))
            
        threading.Thread(target=task, daemon=True).start()
