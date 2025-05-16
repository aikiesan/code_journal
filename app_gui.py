import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
import database # Your database module
import signal # <<< IMPORT SIGNAL MODULE
import win32gui # Add this import for Windows-specific functionality
import win32con # Add this import for Windows-specific functionality
import win32api # Add this import for Windows-specific functionality
import ctypes
from ctypes import wintypes
import json
# from PIL import Image # Uncomment if you add icons (and install Pillow: pip install Pillow)
from views import SettingsView, LibraryView # Updated import

# --- App Configuration ---
APP_NAME = "Code Journal"
APP_VERSION = "1.0.0"
APP_COPYRIGHT = "© 2024 Code Journal"
WINDOW_WIDTH = 950 
WINDOW_HEIGHT = 650 

# Theme Colors
COLOR_APP_BACKGROUND = "#F0F2F5"
COLOR_SIDEBAR_BACKGROUND = "#FFFFFF"
COLOR_CONTENT_BACKGROUND = "#FFFFFF" 
COLOR_PRIMARY = "#3B82F6"
COLOR_PRIMARY_HOVER = "#2563EB"
COLOR_TEXT_PRIMARY = "#1F2937"
COLOR_TEXT_SECONDARY = "#6B7280"
COLOR_BORDER = "#E5E7EB"
COLOR_TITLE_BAR = "#FFFFFF"
COLOR_CARD_BORDER = "#E0E0E0" 
COLOR_DATE_TEXT = "#4B5563" 

# Win32 Constants
GWL_STYLE = -16
WS_MINIMIZEBOX = 0x00020000
WS_MAXIMIZEBOX = 0x00010000
WS_SYSMENU = 0x00080000
WS_CAPTION = 0x00C00000
WS_VISIBLE = 0x10000000
GWLP_HWNDPARENT = -8

class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set up window properties
        self.title(APP_NAME)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.configure(fg_color=COLOR_APP_BACKGROUND)
        
        # Center the window on screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - WINDOW_WIDTH) // 2
        y = (screen_height - WINDOW_HEIGHT) // 2
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

        # Force window to show in taskbar and Alt+Tab
        # self.after(100, self.setup_window_style) # Temporarily disabled for debugging double window issue

        try:
            database.create_table()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not initialize database: {e}")
            self.destroy()
            return

        # --- Fonts ---
        self.font_main = ctk.CTkFont(family="Inter", size=13)
        self.font_bold = ctk.CTkFont(family="Inter", size=13, weight="bold")
        self.font_large_bold = ctk.CTkFont(family="Inter", size=18, weight="bold")
        self.font_header = ctk.CTkFont(family="Inter", size=22, weight="bold")
        self.font_button = ctk.CTkFont(family="Inter", size=14, weight="bold")
        self.font_appname_sidebar = ctk.CTkFont(family="Inter", size=20, weight="bold")
        self.font_custom_title = ctk.CTkFont(family="Inter", size=12, weight="bold")
        self.font_entry_date = ctk.CTkFont(family="Inter", size=12, weight="bold")
        self.font_entry_content = ctk.CTkFont(family="Inter", size=13)

        # --- Main Application Structure ---
        self.setup_main_content()

    def setup_window_style(self):
        """Force window to show in taskbar and Alt+Tab"""
        try:
            # Get window handle
            hwnd = self.winfo_id()
            
            # Set the window's parent to None (forces it to be a top-level window)
            ctypes.windll.user32.SetWindowLongPtrW(hwnd, GWLP_HWNDPARENT, 0)
            
            # Get current window style
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
            
            # Add necessary window styles
            style |= WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_SYSMENU | WS_CAPTION | WS_VISIBLE
            
            # Apply the new style
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style)
            
            # Force window to update
            ctypes.windll.user32.SetWindowPos(
                hwnd, 0, 0, 0, 0, 0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED
            )
            
            # Set the window's extended style
            ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            ex_style = ex_style & ~win32con.WS_EX_TOOLWINDOW  # Remove tool window style
            ex_style = ex_style | win32con.WS_EX_APPWINDOW    # Add app window style
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)
            
            # Update the taskbar
            self.update_idletasks()
            
        except Exception as e:
            print(f"Error setting window style: {e}")

    def setup_main_content(self):
        """Set up the main content area"""
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(fill="both", expand=True)
        
        self.main_content.grid_columnconfigure(1, weight=1)
        self.main_content.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.setup_main_content_area_and_views()
        
        self.show_new_entry_view()

    def setup_sidebar(self):
        """Setup the sidebar with navigation buttons"""
        self.sidebar_frame = ctk.CTkFrame(self.main_content, width=260, corner_radius=0, fg_color=COLOR_SIDEBAR_BACKGROUND)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsw", padx=0, pady=0)
        self.sidebar_frame.grid_propagate(False)
        self.sidebar_frame.grid_rowconfigure(1, weight=1)

        sidebar_header_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        sidebar_header_frame.grid(row=0, column=0, sticky="ew", padx=25, pady=(25,30))
        app_title_label = ctk.CTkLabel(sidebar_header_frame, text=APP_NAME, font=self.font_appname_sidebar,
                                     text_color=COLOR_TEXT_PRIMARY, anchor="w")
        app_title_label.pack(fill="x")

        nav_buttons_container = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        nav_buttons_container.grid(row=1, column=0, sticky="new", padx=25, pady=0)

        self.nav_buttons = {}
        nav_items = {
            "Today": self.show_today_view,
            "Entries": self.show_entries_view,
            "Library": self.show_library_view,
            "Settings": self.show_settings_view
        }
        for name, command_func in nav_items.items():
            button = ctk.CTkButton(nav_buttons_container, text=name, font=self.font_main,
                                   fg_color="transparent", hover_color=COLOR_APP_BACKGROUND, text_color=COLOR_TEXT_SECONDARY,
                                   anchor="w", height=40, corner_radius=8, command=command_func)
            button.pack(pady=4, fill="x")
            self.nav_buttons[name] = button
        
        self.new_entry_button_sidebar = ctk.CTkButton(self.sidebar_frame, text="New Entry",
                                            font=self.font_button,
                                            fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER, text_color="#FFFFFF",
                                            height=45, corner_radius=10, command=self.show_new_entry_view)
        self.new_entry_button_sidebar.grid(row=2, column=0, sticky="sew", padx=25, pady=(20,25))

    def setup_main_content_area_and_views(self):
        """Set up the main content area and initialize all views"""
        self.main_content_container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.main_content_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_content_container.grid_columnconfigure(0, weight=1)
        self.main_content_container.grid_rowconfigure(0, weight=1)

        self.current_view_frame = None
        self.views = {}

        # Initialize all views
        self.view_new_entry = ctk.CTkFrame(self.main_content_container, fg_color=COLOR_CONTENT_BACKGROUND, corner_radius=12)
        self.setup_new_entry_view_widgets(self.view_new_entry)
        self.views["new_entry"] = self.view_new_entry

        self.view_entries = ctk.CTkFrame(self.main_content_container, fg_color=COLOR_CONTENT_BACKGROUND, corner_radius=12)
        self.setup_entries_view_widgets(self.view_entries)
        self.views["entries"] = self.view_entries
        
        self.view_today = ctk.CTkFrame(self.main_content_container, fg_color=COLOR_CONTENT_BACKGROUND, corner_radius=12)
        self.setup_today_view(self.view_today)
        self.views["today"] = self.view_today

        # Initialize Library and Settings Views using their new classes
        self.view_library = LibraryView(parent_tk=self.main_content_container, app_instance=self, database=database)
        self.views["library"] = self.view_library

        self.view_settings = SettingsView(parent_tk=self.main_content_container, app_instance=self, database=database)
        self.views["settings"] = self.view_settings

        # Configure all views
        for view_key, view_frame in self.views.items():
            view_frame.grid(row=0, column=0, sticky="nsew", in_=self.main_content_container)
            view_frame.grid_remove()  # Hide them initially
        
        # Show initial view (Today view)
        self.show_today_view()

    def setup_today_view(self, parent_frame):
        """Setup the Today view to show today's entries."""
        print("Setting up Today view...")  # Debug print
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(1, weight=1)

        # Header with date and refresh button
        header_frame = ctk.CTkFrame(parent_frame, fg_color="transparent", height=40)
        header_frame.grid(row=0, column=0, padx=30, pady=(30,20), sticky="ew")
        header_frame.grid_propagate(False)  # Prevent frame from shrinking
        
        # Configure header frame columns
        header_frame.grid_columnconfigure(0, weight=1)  # Title takes available space
        header_frame.grid_columnconfigure(1, weight=0)  # Button takes only needed space

        # Title
        today = datetime.now()
        date_str = today.strftime("%B %d, %Y")
        title = ctk.CTkLabel(
            header_frame,
            text=f"Today - {date_str}",
            font=self.font_header,
            text_color=COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        title.grid(row=0, column=0, sticky="w")
        print("Title created and gridded")  # Debug print

        # Refresh button
        print("Creating refresh button...")  # Debug print
        self.refresh_button = ctk.CTkButton(
            header_frame,
            text="↻ Refresh",
            command=self.refresh_today_entries,
            font=self.font_button,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            width=100,
            height=32,
            corner_radius=8
        )
        self.refresh_button.grid(row=0, column=1, sticky="e", padx=(10, 0))
        print("Refresh button created and gridded")  # Debug print

        # Force update of header frame
        header_frame.update_idletasks()
        print(f"Header frame dimensions: {header_frame.winfo_width()}x{header_frame.winfo_height()}")  # Debug print
        print(f"Refresh button dimensions: {self.refresh_button.winfo_width()}x{self.refresh_button.winfo_height()}")  # Debug print

        # Main content area
        content_frame = ctk.CTkFrame(parent_frame, fg_color=COLOR_APP_BACKGROUND, corner_radius=12)
        content_frame.grid(row=1, column=0, padx=30, pady=(0,30), sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        # Header for entries
        entries_label = ctk.CTkLabel(
            content_frame,
            text="Today's Entries",
            font=self.font_large_bold,
            text_color=COLOR_TEXT_PRIMARY
        )
        entries_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20,10))

        # Scrollable frame for entries
        self.today_entries_scrollable = ctk.CTkScrollableFrame(
            content_frame,
            fg_color="transparent",
            border_width=0,
            corner_radius=0
        )
        self.today_entries_scrollable.grid(row=1, column=0, padx=20, pady=(0,20), sticky="nsew")
        self.today_entries_scrollable.grid_columnconfigure(0, weight=1)

        # Load today's entries
        self.load_today_entries()
        print("Today view setup complete")  # Debug print

    def refresh_today_entries(self):
        """Refresh today's entries with visual feedback"""
        # Disable button and show loading state
        self.refresh_button.configure(state="disabled", text="Refreshing...")
        
        # Schedule the actual refresh after a short delay to show the button state
        self.after(100, self._perform_refresh)

    def _perform_refresh(self):
        """Perform the actual refresh operation"""
        try:
            self.load_today_entries()
        finally:
            # Re-enable button and restore text
            self.refresh_button.configure(state="normal", text="↻ Refresh")
            
            # Show a subtle visual confirmation
            self.refresh_button.configure(fg_color=COLOR_PRIMARY_HOVER)
            self.after(200, lambda: self.refresh_button.configure(fg_color=COLOR_PRIMARY))

    def load_today_entries(self):
        """Load and display today's entries in the Today view."""
        # Clear existing entries
        for widget in self.today_entries_scrollable.winfo_children():
            widget.destroy()

        try:
            today = datetime.now().strftime("%Y-%m-%d")
            print(f"Loading entries for date: {today}")  # Debug log
            entries = database.get_entries_by_date(today)
            print(f"Found {len(entries)} entries")  # Debug log

            if not entries:
                no_entries_label = ctk.CTkLabel(self.today_entries_scrollable,
                                              text="No entries for today yet. Click 'New Entry' to add one!",
                                              font=self.font_main,
                                              text_color=COLOR_TEXT_SECONDARY)
                no_entries_label.pack(padx=10, pady=20)
            else:
                for entry in entries:
                    entry_card = ctk.CTkFrame(self.today_entries_scrollable,
                                            fg_color=COLOR_CONTENT_BACKGROUND,
                                            border_width=1,
                                            border_color=COLOR_CARD_BORDER,
                                            corner_radius=10)
                    entry_card.pack(fill="x", padx=0, pady=(0,10))

                    # Format time using created_at if available, otherwise use date
                    try:
                        time_str = entry.get('created_at', entry['date'])
                        time_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                        formatted_time = time_obj.strftime("%I:%M %p")
                    except (ValueError, TypeError) as e:
                        print(f"Error formatting time: {e}")  # Debug log
                        formatted_time = ""

                    time_label = ctk.CTkLabel(entry_card,
                                            text=formatted_time,
                                            font=self.font_entry_date,
                                            text_color=COLOR_DATE_TEXT,
                                            anchor="w")
                    time_label.pack(fill="x", padx=15, pady=(10,5))

                    content_label = ctk.CTkLabel(entry_card,
                                               text=entry['content'],
                                               font=self.font_entry_content,
                                               text_color=COLOR_TEXT_PRIMARY,
                                               wraplength=self.today_entries_scrollable.winfo_width() - 60,
                                               justify="left",
                                               anchor="w")
                    content_label.pack(fill="x", padx=15, pady=(0,10))

        except Exception as e:
            print(f"Error in load_today_entries: {e}")  # Debug log
            error_label = ctk.CTkLabel(self.today_entries_scrollable,
                                     text=f"Error loading entries: {e}",
                                     font=self.font_main,
                                     text_color="red")
            error_label.pack(padx=10, pady=20)

    def setup_new_entry_view_widgets(self, parent_frame):
        parent_frame.grid_columnconfigure(0, weight=1) 
        
        title = ctk.CTkLabel(parent_frame, text="Create New Journal Entry", font=self.font_header, text_color=COLOR_TEXT_PRIMARY)
        title.grid(row=0, column=0, columnspan=2, padx=30, pady=(30,10), sticky="w")
        
        ctk.CTkLabel(parent_frame, text="What have you learned or experienced today?", font=self.font_main, text_color=COLOR_TEXT_SECONDARY).grid(row=1, column=0, columnspan=2, padx=30, pady=(10,5), sticky="w")
        
        self.new_entry_content_textbox = ctk.CTkTextbox(parent_frame, height=200, wrap="word", font=self.font_entry_content,
                                               border_width=1, border_color=COLOR_BORDER, corner_radius=8,
                                               fg_color=COLOR_APP_BACKGROUND) 
        self.new_entry_content_textbox.grid(row=2, column=0, columnspan=2, padx=30, pady=(0,20), sticky="ew")
        parent_frame.grid_rowconfigure(2, weight=1) 

        date_frame_new_entry = ctk.CTkFrame(parent_frame, fg_color="transparent")
        date_frame_new_entry.grid(row=3, column=0, padx=30, pady=(0,20), sticky="w")
        
        ctk.CTkLabel(date_frame_new_entry, text="Date:", font=self.font_bold, text_color=COLOR_TEXT_SECONDARY).pack(side="left", padx=(0,10))
        self.new_entry_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.new_entry_date_entry = ctk.CTkEntry(date_frame_new_entry, textvariable=self.new_entry_date_var, width=130, font=self.font_main,
                                             border_width=1, border_color=COLOR_BORDER, corner_radius=8)
        self.new_entry_date_entry.pack(side="left")
        
        self.add_entry_submit_button = ctk.CTkButton(parent_frame, text="Save Entry", command=self.action_add_new_entry,
                                               font=self.font_button, fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER,
                                               height=40, corner_radius=8)
        self.add_entry_submit_button.grid(row=4, column=0, columnspan=2, padx=30, pady=(10,30), sticky="e")

    def setup_entries_view_widgets(self, parent_frame):
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(1, weight=1) 
        
        title = ctk.CTkLabel(parent_frame, text="Your Journal Entries", font=self.font_header, text_color=COLOR_TEXT_PRIMARY)
        title.grid(row=0, column=0, padx=30, pady=(30,15), sticky="w")
        
        self.entries_scrollable_frame = ctk.CTkScrollableFrame(parent_frame, fg_color="transparent",
                                                               border_width=0, corner_radius=0)
        self.entries_scrollable_frame.grid(row=1, column=0, padx=30, pady=(0,30), sticky="nsew")
        self.entries_scrollable_frame.grid_columnconfigure(0, weight=1)

    def switch_to_view(self, view_key_name):
        if self.current_view_frame:
            self.current_view_frame.grid_remove()
        
        self.current_view_frame = self.views.get(view_key_name)
        if self.current_view_frame:
            self.current_view_frame.grid()
            self.current_view_frame.lift()
            if hasattr(self.current_view_frame, 'refresh') and callable(self.current_view_frame.refresh):
                self.current_view_frame.refresh()
            self.update_active_nav_button_style(view_key_name)
        else:
            print(f"Error: View '{view_key_name}' not found.")

    def update_active_nav_button_style(self, active_view_key=None):
        view_key_to_nav_button_text = {
            "today": "Today",
            "entries": "Entries",
            "library": "Library",
            "settings": "Settings",
        }
        active_nav_text = view_key_to_nav_button_text.get(active_view_key)

        for btn_text, button_widget in self.nav_buttons.items():
            if btn_text == active_nav_text:
                button_widget.configure(fg_color=COLOR_APP_BACKGROUND, text_color=COLOR_PRIMARY, font=self.font_bold)
            else:
                button_widget.configure(fg_color="transparent", text_color=COLOR_TEXT_SECONDARY, font=self.font_main)
        
        if active_view_key == "new_entry":
            self.new_entry_button_sidebar.configure(fg_color=COLOR_PRIMARY_HOVER) 
        else:
            self.new_entry_button_sidebar.configure(fg_color=COLOR_PRIMARY)

    def show_new_entry_view(self): self.switch_to_view("new_entry")
    def show_entries_view(self): self.action_load_entries_into_display(); self.switch_to_view("entries")
    def show_today_view(self): 
        print("Switching to Today view...")  # Debug print
        self.switch_to_view("today")
        self.load_today_entries()  # Ensure entries are loaded when switching to Today view
        
        # Force update of the refresh button if it exists
        if hasattr(self, 'refresh_button'):
            print("Updating refresh button...")  # Debug print
            self.refresh_button.lift()  # Ensure button is on top
            self.refresh_button.update_idletasks()
            print("Refresh button updated")  # Debug print
    def show_library_view(self): self.switch_to_view("library")
    def show_settings_view(self): self.switch_to_view("settings")

    def action_add_new_entry(self):
        content = self.new_entry_content_textbox.get("1.0", "end-1c").strip()
        date_str = self.new_entry_date_var.get().strip()
        if not content: messagebox.showwarning("Input Error", "Entry content cannot be empty."); return
        if not date_str: messagebox.showwarning("Input Error", "Date cannot be empty."); return
        try: datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError: messagebox.showwarning("Input Error", "Invalid date format. Please use YYYY-MM-DD."); return
        
        try:
            database.add_entry(content, date_str)
            messagebox.showinfo("Success", "Entry added successfully!")
            self.new_entry_content_textbox.delete("1.0", "end")
            self.new_entry_date_var.set(datetime.now().strftime("%Y-%m-%d")) 
            
            if self.views["entries"] == self.current_view_frame: 
                self.action_load_entries_into_display()
            if self.views["today"] == self.current_view_frame:
                self.load_today_entries()
                
        except Exception as e: messagebox.showerror("Database Error", f"Failed to add entry: {e}")

    def action_load_entries_into_display(self):
        for widget in self.entries_scrollable_frame.winfo_children():
            widget.destroy()
        try:
            entries = database.get_entries() 
            if not entries:
                no_entries_label = ctk.CTkLabel(self.entries_scrollable_frame, text="No entries yet. Add your first one!",
                                                font=self.font_main, text_color=COLOR_TEXT_SECONDARY)
                no_entries_label.pack(padx=10, pady=20)
            else:
                # Calculate dynamic wraplength once, or bind to configure event for responsiveness
                # For simplicity here, we estimate based on typical window width and padding
                try:
                    # Ensure the scrollable frame has a width before calculating
                    self.entries_scrollable_frame.update_idletasks() 
                    base_wraplength = self.entries_scrollable_frame.winfo_width() - 60 # (padx 15*2 + some buffer)
                    if base_wraplength <= 0: base_wraplength = 500 # Fallback if width isn't available yet
                except tk.TclError: # Can happen if widget is not yet mapped
                    base_wraplength = 500


                for entry_data in entries:
                    entry_card = ctk.CTkFrame(self.entries_scrollable_frame, fg_color=COLOR_CONTENT_BACKGROUND,
                                              border_width=1, border_color=COLOR_CARD_BORDER, corner_radius=10)
                    entry_card.pack(fill="x", padx=0, pady=(0,10)) 

                    try:
                        date_obj = datetime.strptime(entry_data['date'], "%Y-%m-%d")
                        formatted_date = date_obj.strftime("%B %d, %Y") 
                    except ValueError:
                        formatted_date = entry_data['date'] 

                    date_label = ctk.CTkLabel(entry_card, text=formatted_date, font=self.font_entry_date,
                                              text_color=COLOR_DATE_TEXT, anchor="w")
                    date_label.pack(fill="x", padx=15, pady=(10, 5))

                    content_label = ctk.CTkLabel(entry_card, text=entry_data['content'], font=self.font_entry_content,
                                                 text_color=COLOR_TEXT_PRIMARY, wraplength=base_wraplength, 
                                                 justify="left", anchor="w")
                    content_label.pack(fill="x", padx=15, pady=(0, 10))
                    
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load entries: {e}")
            error_label = ctk.CTkLabel(self.entries_scrollable_frame, text=f"Error loading entries: {e}",
                                       font=self.font_main, text_color="red")
            error_label.pack(padx=10, pady=20)

    def on_closing(self, from_interrupt=False):
        do_close = False
        if from_interrupt:
            print("Closing application due to interrupt signal...")
            do_close = True # Force close without prompt for Ctrl+C
        else:
            if messagebox.askokcancel("Quit", "Do you want to quit Code Journal?"):
                do_close = True
        
        if do_close:
            print("Performing cleanup before exit...")
            try:
                # Assuming database.py has a close_connection for the current thread's connection
                database.close_connection() 
                print("Database connection for this thread closed (if one was active).")
            except AttributeError:
                print("database.close_connection() not found or not needed.") # In case it's not defined
            except Exception as e:
                print(f"Error during database.close_connection(): {e}")
            
            self.destroy() # This will terminate the mainloop

    def handle_sigint(self, signum, frame):
        """Handles SIGINT signal (e.g., Ctrl+C from terminal)."""
        print("\nCtrl+C detected. Initiating graceful shutdown...")
        # Schedule the on_closing method to be called safely in the Tkinter main thread
        # Pass True to indicate it's from an interrupt, bypassing the confirmation dialog.
        self.after(0, self.on_closing, True)


if __name__ == "__main__":
    ctk.set_appearance_mode("Light") 
    app = App()
    
    # <<< REGISTER SIGNAL HANDLER >>>
    # This will call app.handle_sigint when Ctrl+C (SIGINT) is pressed
    signal.signal(signal.SIGINT, app.handle_sigint)
    
    try:
        app.mainloop()
    except SystemExit: # Can be raised by app.destroy() or other exit mechanisms
        print("Application exited via SystemExit.")
    except Exception as e:
        print(f"Unhandled exception in main loop: {e}")
    finally:
        print("Application has shut down.")