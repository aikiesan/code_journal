import os
import sys
import subprocess
import shutil
from pathlib import Path

def cleanup():
    """Clean up build artifacts before running PyInstaller"""
    print("Cleaning up previous build artifacts...")
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    # Clean up views/__pycache__
    views_pycache = Path('views') / '__pycache__'
    if views_pycache.exists():
        shutil.rmtree(views_pycache)

def verify_views_structure():
    """Verify that all required view files exist"""
    required_files = [
        'views/__init__.py',
        'views/base_view.py',
        'views/settings_view.py',
        'views/library_view.py'
    ]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        raise FileNotFoundError(f"Missing required view files: {', '.join(missing_files)}")

def verify_build(dist_dir):
    """Verify the build output exists and contains necessary files"""
    exe_path = os.path.join(dist_dir, 'CodeJournal.exe')
    if not os.path.exists(exe_path):
        raise Exception("Build failed: Executable not found")
    return exe_path

def run_pyinstaller():
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(current_dir, 'dist')
    
    try:
        # Pre-build checks
        cleanup()
        verify_views_structure()
        
        # Define PyInstaller command using Python -m
        cmd = [
            sys.executable,  # Use the current Python interpreter
            '-m',
            'PyInstaller',
            '--name=CodeJournal',
            '--onefile',
            '--windowed',
            '--clean',
            '--noconfirm',
            '--add-data=database.py:.',
            '--add-data=views;views',  # Correct syntax for views directory on Windows
            '--add-data=code_journal_icon.ico:.',
            '--icon=code_journal_icon.ico',
            # Core dependencies
            '--hidden-import=win32gui',
            '--hidden-import=win32con',
            '--hidden-import=win32api',
            '--hidden-import=ctypes',
            '--hidden-import=sqlite3',
            # Views module and its components
            '--hidden-import=views',
            '--hidden-import=views.base_view',
            '--hidden-import=views.settings_view',
            '--hidden-import=views.library_view',
            # Additional data files
            '--add-data=data.db:.',
            '--add-data=requirements.txt:.',
            '--add-data=README.md:.',
            'app_gui.py'
        ]
        
        # Run PyInstaller
        print("Running PyInstaller...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Handle output
        if result.stdout:
            print("Build Output:")
            print(result.stdout)
        if result.stderr:
            print("Warnings/Errors:")
            print(result.stderr)
            
        # Verify build
        exe_path = verify_build(dist_dir)
        print("Build completed successfully!")
        print(f"Executable created at: {exe_path}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error during build: {e}")
        if e.stdout:
            print("Output:", e.stdout)
        if e.stderr:
            print("Error details:", e.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_pyinstaller() 