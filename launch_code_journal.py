#!/usr/bin/env python3
"""
Code Journal Launcher
This script launches the Code Journal application and handles any startup errors.
"""

import sys
import subprocess
import os

def check_requirements():
    """Check if required packages are installed."""
    try:
        import customtkinter
        import tkinter
    except ImportError as e:
        print(f"Error: Missing required package - {e}")
        print("Please install required packages using: pip install -r requirements.txt")
        return False
    return True

def main():
    """Main launcher function."""
    print("Starting Code Journal...")
    
    # Check if we're in the correct directory
    if not os.path.exists("app_gui.py"):
        print("Error: Could not find app_gui.py")
        print("Please run this script from the Code Journal directory")
        return 1
    
    # Check requirements
    if not check_requirements():
        return 1
    
    try:
        # Launch the main application
        from app_gui import App
        import customtkinter as ctk
        
        ctk.set_appearance_mode("Light")
        app = App()
        app.mainloop()
        return 0
    except Exception as e:
        print(f"Error: Failed to start Code Journal - {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 