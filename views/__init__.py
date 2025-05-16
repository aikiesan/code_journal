"""
Code Journal Views Package

This package contains all the view classes for the Code Journal application.
Each view is implemented as a separate class inheriting from BaseView.
"""

from .base_view import BaseView
from .settings_view import SettingsView
from .library_view import LibraryView

__all__ = ['BaseView', 'SettingsView', 'LibraryView'] 