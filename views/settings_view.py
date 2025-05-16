import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
import json
from .base_view import BaseView

class SettingsView(BaseView):
    """Settings view for the application"""
    
    def _create_widgets(self):
        """Create all widgets for the settings view"""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(30,20))
        
        title = ctk.CTkLabel(header_frame, text="Settings", 
                           font=("Inter", 22, "bold"), text_color="#1F2937")
        title.pack(side="left", anchor="w")

        # Main settings content in a scrollable frame
        settings_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        settings_scroll.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0,30))
        settings_scroll.grid_columnconfigure(0, weight=1)

        # --- Appearance Settings ---
        self._create_appearance_section(settings_scroll)
        
        # --- Window Settings ---
        self._create_window_section(settings_scroll)
        
        # --- Notifications Settings ---
        self._create_notifications_section(settings_scroll)
        
        # --- Data Management ---
        self._create_data_management_section(settings_scroll)
        
        # --- About Section ---
        self._create_about_section(settings_scroll)

    def _create_appearance_section(self, parent):
        appearance_frame = ctk.CTkFrame(parent, fg_color="transparent")
        appearance_frame.pack(fill="x", pady=(0,20))
        
        ctk.CTkLabel(appearance_frame, text="Appearance", 
                    font=("Inter", 18, "bold"), text_color="#1F2937").pack(anchor="w", pady=(0,10))
        
        theme_frame = ctk.CTkFrame(appearance_frame, fg_color="transparent")
        theme_frame.pack(fill="x")
        
        ctk.CTkLabel(theme_frame, text="Theme:", 
                    font=("Inter", 13, "bold"), text_color="#6B7280").pack(side="left", padx=(0,10))
        
        self.theme_var = tk.StringVar(value=ctk.get_appearance_mode())
        theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=["Light", "Dark", "System"],
            variable=self.theme_var,
            command=self._change_theme,
            font=("Inter", 13),
            fg_color="#3B82F6",
            button_color="#3B82F6",
            button_hover_color="#2563EB"
        )
        theme_menu.pack(side="left")

    def _create_window_section(self, parent):
        window_frame = ctk.CTkFrame(parent, fg_color="transparent")
        window_frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(window_frame, text="Window", 
                    font=("Inter", 18, "bold"), text_color="#1F2937").pack(anchor="w", pady=(0,10))
        
        self.always_on_top_var = tk.BooleanVar(value=False)
        always_on_top_switch = ctk.CTkSwitch(
            window_frame,
            text="Keep window always on top",
            variable=self.always_on_top_var,
            command=self._toggle_always_on_top,
            font=("Inter", 13),
            progress_color="#3B82F6"
        )
        always_on_top_switch.pack(anchor="w")

    def _create_notifications_section(self, parent):
        notifications_frame = ctk.CTkFrame(parent, fg_color="transparent")
        notifications_frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(notifications_frame, text="Notifications", 
                    font=("Inter", 18, "bold"), text_color="#1F2937").pack(anchor="w", pady=(0,10))
        
        self.notifications_enabled_var = tk.BooleanVar(value=True)
        notifications_switch = ctk.CTkSwitch(
            notifications_frame,
            text="Enable desktop notifications",
            variable=self.notifications_enabled_var,
            command=self._toggle_notifications,
            font=("Inter", 13),
            progress_color="#3B82F6"
        )
        notifications_switch.pack(anchor="w")

    def _create_data_management_section(self, parent):
        data_frame = ctk.CTkFrame(parent, fg_color="transparent")
        data_frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(data_frame, text="Data Management", 
                    font=("Inter", 18, "bold"), text_color="#1F2937").pack(anchor="w", pady=(0,10))
        
        data_buttons_frame = ctk.CTkFrame(data_frame, fg_color="transparent")
        data_buttons_frame.pack(fill="x")
        
        export_button = ctk.CTkButton(
            data_buttons_frame,
            text="Export Journal Data",
            command=self._export_journal_data,
            font=("Inter", 13),
            fg_color="#3B82F6",
            hover_color="#2563EB"
        )
        export_button.pack(side="left", padx=(0,10))
        
        import_button = ctk.CTkButton(
            data_buttons_frame,
            text="Import Journal Data",
            command=self._import_journal_data,
            font=("Inter", 13),
            fg_color="#3B82F6",
            hover_color="#2563EB"
        )
        import_button.pack(side="left")

    def _create_about_section(self, parent):
        about_frame = ctk.CTkFrame(parent, fg_color="transparent")
        about_frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(about_frame, text="About", 
                    font=("Inter", 18, "bold"), text_color="#1F2937").pack(anchor="w", pady=(0,10))
        
        ctk.CTkLabel(about_frame, text="Code Journal - Version 1.0.0", 
                    font=("Inter", 13), text_color="#1F2937").pack(anchor="w")
        
        ctk.CTkLabel(about_frame, text="© 2024 Code Journal", 
                    font=("Inter", 13), text_color="#6B7280").pack(anchor="w", pady=(0,10))

    def _change_theme(self, new_theme):
        """Change the application theme"""
        ctk.set_appearance_mode(new_theme)
        
    def _toggle_always_on_top(self):
        """Toggle window always on top state"""
        self.app_instance.attributes('-topmost', self.always_on_top_var.get())
        
    def _toggle_notifications(self):
        """Toggle notification settings"""
        enabled = self.notifications_enabled_var.get()
        print(f"Notifications {'enabled' if enabled else 'disabled'}")
        
    def _export_journal_data(self):
        """Export journal data to a JSON file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Export Journal Data"
            )
            if filename:
                entries = self.database.get_entries()
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(entries, f, indent=4)
                messagebox.showinfo("Success", "Journal data exported successfully!")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {e}")
            
    def _import_journal_data(self):
        """Import journal data from a JSON file"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Import Journal Data"
            )
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    entries = json.load(f)
                
                if messagebox.askyesno("Confirm Import", 
                                     "This will add the imported entries to your journal. Continue?"):
                    for entry in entries:
                        self.database.add_entry(entry['content'], entry['date'])
                    messagebox.showinfo("Success", "Journal data imported successfully!")
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import data: {e}")

    def refresh(self):
        """Update the view's state"""
        self.theme_var.set(ctk.get_appearance_mode())
        self.always_on_top_var.set(self.app_instance.attributes('-topmost')) 