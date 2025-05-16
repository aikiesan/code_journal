import customtkinter as ctk
from .base_view import BaseView

class LibraryView(BaseView):
    """Library view for the application"""
    
    def _create_widgets(self):
        """Create all widgets for the library view"""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(30,20))
        
        title = ctk.CTkLabel(header_frame, text="Library", 
                           font=("Inter", 22, "bold"), text_color="#1F2937")
        title.pack(side="left", anchor="w")

        # Content
        content_label = ctk.CTkLabel(self, 
                                     text="Library View - Modular Content Under Construction",
                                     font=("Inter", 13), 
                                     text_color="#6B7280")
        content_label.grid(row=1, column=0, padx=30, pady=20, sticky="nsew")

    def refresh(self):
        """Refresh the library view (if needed in the future)"""
        pass 