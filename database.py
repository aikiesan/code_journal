import sqlite3
import threading
from contextlib import contextmanager
from typing import List, Dict, Any
from datetime import datetime

DB_NAME = "data.db"
# Thread-local storage for database connections
_local = threading.local()

def get_connection() -> sqlite3.Connection:
    """Get a thread-local database connection."""
    if not hasattr(_local, 'connection'):
        _local.connection = sqlite3.connect(
            DB_NAME,
            check_same_thread=False,  # Allow connections from different threads
            timeout=30.0  # Wait up to 30 seconds for locks
        )
        # Enable foreign keys and set journal mode to WAL for better concurrency
        _local.connection.execute("PRAGMA foreign_keys = ON;")
        _local.connection.execute("PRAGMA journal_mode = WAL;")
    return _local.connection

@contextmanager
def get_db():
    """Context manager for database operations."""
    conn = get_connection()
    try:
        yield conn
    except sqlite3.Error as e:
        conn.rollback()
        raise e
    finally:
        # Don't close the connection, just commit
        conn.commit()

def create_table():
    """Create the entries table if it doesn't exist."""
    try:
        with get_db() as conn:
            # First, check if the table exists
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='entries';")
            table_exists = cursor.fetchone() is not None

            if not table_exists:
                # Create new table with all columns
                conn.execute("""
                    CREATE TABLE entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content TEXT NOT NULL,
                        date TEXT NOT NULL,
                        created_at TEXT
                    );
                """)
            else:
                # Check if created_at column exists
                cursor = conn.execute("PRAGMA table_info(entries);")
                columns = [column[1] for column in cursor.fetchall()]
                
                if 'created_at' not in columns:
                    # Add created_at column without default value
                    conn.execute("""
                        ALTER TABLE entries 
                        ADD COLUMN created_at TEXT;
                    """)
                    # Update existing rows with current timestamp
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    conn.execute("UPDATE entries SET created_at = ? WHERE created_at IS NULL;", (current_time,))
    except sqlite3.Error as e:
        print(f"Error creating/updating table: {e}")
        raise

def add_entry(entry_content: str, entry_date: str) -> None:
    """Add a new entry to the database."""
    if not entry_content or not entry_date:
        raise ValueError("Content and date cannot be empty")
    
    try:
        with get_db() as conn:
            # Ensure we have both date and time components
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # If entry_date is just a date, combine it with current time
            try:
                # Try to parse as datetime first
                datetime.strptime(entry_date, "%Y-%m-%d %H:%M:%S")
                formatted_date = entry_date
            except ValueError:
                # If that fails, assume it's just a date and add the current time
                date_obj = datetime.strptime(entry_date, "%Y-%m-%d")
                formatted_date = f"{date_obj.strftime('%Y-%m-%d')} {datetime.now().strftime('%H:%M:%S')}"
            
            print(f"Adding entry with date: {formatted_date}")  # Debug log
            
            conn.execute(
                "INSERT INTO entries (content, date, created_at) VALUES (?, ?, ?);",
                (entry_content, formatted_date, current_time)
            )
            print("Entry added successfully")  # Debug log
    except sqlite3.Error as e:
        print(f"Error adding entry: {e}")
        raise

def get_entries() -> List[Dict[str, Any]]:
    """Get all entries ordered by date descending."""
    try:
        with get_db() as conn:
            # First check if created_at column exists
            cursor = conn.execute("PRAGMA table_info(entries);")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'created_at' in columns:
                # Use created_at in ordering if it exists
                cursor = conn.execute(
                    "SELECT content, date FROM entries ORDER BY date DESC, created_at DESC;"
                )
            else:
                # Fallback to date-only ordering
                cursor = conn.execute(
                    "SELECT content, date FROM entries ORDER BY date DESC;"
                )
            
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Error getting entries: {e}")
        raise

def get_entries_by_date(date_str):
    """Get all entries for a specific date."""
    try:
        with get_db() as conn:
            # Convert date string to datetime for comparison
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            start_of_day = date_obj.strftime("%Y-%m-%d 00:00:00")
            end_of_day = date_obj.strftime("%Y-%m-%d 23:59:59")
            
            print(f"Querying entries between {start_of_day} and {end_of_day}")  # Debug log
            
            cursor = conn.execute("""
                SELECT content, date, created_at
                FROM entries
                WHERE date BETWEEN ? AND ?
                ORDER BY created_at DESC
            """, (start_of_day, end_of_day))
            
            entries = []
            for row in cursor.fetchall():
                entry = {
                    'content': row[0],
                    'date': row[1],
                    'created_at': row[2]
                }
                entries.append(entry)
                print(f"Found entry: {entry}")  # Debug log
            
            return entries
    except Exception as e:
        print(f"Error in get_entries_by_date: {e}")  # Debug log
        raise

def close_connection():
    """Close the database connection for the current thread."""
    if hasattr(_local, 'connection'):
        try:
            _local.connection.close()
        except sqlite3.Error as e:
            print(f"Error closing connection: {e}")
        finally:
            del _local.connection