import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime
import database # Your database module

# --- App Configuration ---
ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

APP_NAME = "Code Journal"
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 500

class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title(APP_NAME)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing) # Handle window close

        # --- Frameless Window Setup (and custom title bar) ---
        self.overrideredirect(True) # Remove default window decorations

        # Custom Title Bar
        self.title_bar = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.title_bar.pack(side="top", fill="x")

        self.title_label = ctk.CTkLabel(self.title_bar, text=APP_NAME, font=ctk.CTkFont(size=12, weight="bold"))
        self.title_label.pack(side="left", padx=10)

        self.close_button = ctk.CTkButton(self.title_bar, text="✕", width=30, height=25, command=self.on_closing)
        self.close_button.pack(side="right", padx=(0,5), pady=3)

        # Make the window draggable by the title bar
        self.title_bar.bind("<ButtonPress-1>", self.start_move)
        self.title_bar.bind("<ButtonRelease-1>", self.stop_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)
        self.title_label.bind("<ButtonPress-1>", self.start_move)
        self.title_label.bind("<ButtonRelease-1>", self.stop_move)
        self.title_label.bind("<B1-Motion>", self.do_move)

        # --- Main Content Area ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # --- Input Frame for New Entries ---
        self.input_frame = ctk.CTkFrame(self.main_frame)
        self.input_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(self.input_frame, text="What have you learned today?").pack(pady=(0,5), anchor="w")
        self.entry_content_text = ctk.CTkTextbox(self.input_frame, height=100, wrap="word")
        self.entry_content_text.pack(fill="x", expand=True, pady=(0,10))

        self.date_frame = ctk.CTkFrame(self.input_frame) # Frame to hold date label and entry side-by-side
        self.date_frame.pack(fill="x", pady=(0,10))
        ctk.CTkLabel(self.date_frame, text="Date (YYYY-MM-DD):").pack(side="left", padx=(0,5))
        self.entry_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.entry_date_entry = ctk.CTkEntry(self.date_frame, textvariable=self.entry_date_var, width=120)
        self.entry_date_entry.pack(side="left")

        self.add_button = ctk.CTkButton(self.input_frame, text="Add Entry", command=self.add_new_entry)
        self.add_button.pack(pady=5)

        # --- Entries Display Area ---
        ctk.CTkLabel(self.main_frame, text="Journal Entries:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10,5), anchor="w")

        self.entries_textbox = ctk.CTkTextbox(self.main_frame, state="disabled", wrap="word", height=200)
        self.entries_textbox.pack(pady=5, padx=0, fill="both", expand=True)

        # --- Initialize Database and Load Entries ---
        try:
            database.create_table()
            print("Database initialized.")
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not initialize database: {e}")
            self.destroy() # Close app if DB fails critically
            return

        self.load_entries()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def add_new_entry(self):
        content = self.entry_content_text.get("1.0", "end-1c").strip() # Get all text, remove trailing newline
        date_str = self.entry_date_var.get().strip()

        if not content:
            messagebox.showwarning("Input Error", "Entry content cannot be empty.")
            return
        if not date_str:
            messagebox.showwarning("Input Error", "Date cannot be empty.")
            return

        try:
            # Validate date format (optional but good)
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Input Error", "Invalid date format. Please use YYYY-MM-DD.")
            return

        try:
            database.add_entry(content, date_str)
            messagebox.showinfo("Success", "Entry added successfully!")
            self.entry_content_text.delete("1.0", "end") # Clear input
            # Optionally reset date to today or keep user's input
            # self.entry_date_var.set(datetime.now().strftime("%Y-%m-%d"))
            self.load_entries() # Refresh the display
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to add entry: {e}")

    def load_entries(self):
        self.entries_textbox.configure(state="normal") # Enable to modify
        self.entries_textbox.delete("1.0", "end")
        try:
            entries = database.get_entries()
            if not entries:
                self.entries_textbox.insert("end", "No entries yet. Add one above!")
            else:
                for entry in entries:
                    self.entries_textbox.insert("end", f"{entry['date']}\n", ("date_tag",))
                    self.entries_textbox.insert("end", f"{entry['content']}\n\n")
                # Simple styling for dates
                self.entries_textbox.tag_configure("date_tag", font=ctk.CTkFont(weight="bold"))

        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load entries: {e}")
            self.entries_textbox.insert("end", f"Error loading entries: {e}")
        self.entries_textbox.configure(state="disabled") # Disable to make read-only

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit Code Journal?"):
            database.close_connection() # Important: close DB connection
            self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()