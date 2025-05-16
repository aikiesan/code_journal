import customtkinter as ctk

class BaseView(ctk.CTkFrame):
    """Base class for all views in the application"""
    
    def __init__(self, parent_tk, app_instance, database, **kwargs):
        super().__init__(parent_tk, fg_color="transparent", **kwargs)
        
        self.app_instance = app_instance
        self.database = database
        
        # Configure grid for the BaseView frame itself to expand within its parent_tk
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Assuming content is primarily in row 1 after a header in row 0
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create all widgets for the view. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement _create_widgets")
    
    def refresh(self):
        """Refresh the view's content. Should be implemented by subclasses if needed."""
        pass 