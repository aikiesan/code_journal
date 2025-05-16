import sqlite3
from database import create_table, add_entry, get_entries

menu = """Please select one of the following options:
1) Add new entry for today.
2) View entries.
3) Exit.

Your Selection: """
welcome = "Welcome to the code Journal!"

def prompt_new_entry():
    entry_content = input("What have you learned today? ")
    entry_date = input("Enter the date (YYYY-MM-DD): ")
    add_entry(entry_content, entry_date)
    print("Entry added successfully!")

def view_entries(entries):
    if not entries:
        print("No entries found.")
        return
    for entry in entries:
        print(f"{entry['date']}\n{entry['content']}\n\n")

def main():
    print(welcome)
    try:
        create_table()
    except sqlite3.OperationalError as e:
        if "already exists" in str(e):
            print("Database initialized.")
        else:
            raise e

    while True:
        user_input = input(menu)
        if user_input == "1":
            prompt_new_entry()
        elif user_input == "2":
            view_entries(get_entries())
        elif user_input == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid option, please try again.")

if __name__ == "__main__":
    main()