import customtkinter as ctk
from database import init_db, log_activity
from ui.login import LoginFrame
from ui.app import MainAppFrame
from config import APP_NAME

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.current_frame = None
        self.center_window(1200, 800)
        self.bind("<Control-q>", lambda e: self.destroy())
        self.show_login()

    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def show_login(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = LoginFrame(self, self.show_main_app)
        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def show_main_app(self):
        if self.current_frame:
            self.current_frame.destroy()
        from auth import Session
        log_activity(Session.username, "Login", "User logged in successfully.")
        self.current_frame = MainAppFrame(self, self.show_login)
        self.current_frame.grid(row=0, column=0, sticky="nsew")

if __name__ == "__main__":
    print("Initializing Database...")
    init_db()
    print(f"Launching {APP_NAME} GUI...")
    app = App()
    app.mainloop()