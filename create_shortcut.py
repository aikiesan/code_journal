import os
import sys
import winshell
from win32com.client import Dispatch

def create_desktop_shortcut():
    desktop = winshell.desktop()
    path = os.path.join(desktop, "Code Journal.lnk")
    
    # Get the path to the executable
    if getattr(sys, 'frozen', False):
        # If running as compiled executable
        target = sys.executable
    else:
        # If running as script
        target = os.path.abspath("launch_code_journal.py")
    
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = os.path.dirname(target)
    shortcut.IconLocation = os.path.abspath("code_journal_icon.ico")
    shortcut.save()
    
    print(f"Desktop shortcut created at: {path}")

if __name__ == "__main__":
    try:
        create_desktop_shortcut()
    except Exception as e:
        print(f"Error creating shortcut: {e}")
        print("Please make sure you have the required packages installed:")
        print("pip install pywin32 winshell") 