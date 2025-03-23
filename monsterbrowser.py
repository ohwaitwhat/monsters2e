import tkinter as tk
from tkinter import ttk, messagebox
from tkinterweb import HtmlFrame  # Using tkinterweb instead of tkinterhtml
import sqlite3

# Database connection
DB_PATH = 'db/monsters.db'

def get_monster_list():
    """Retrieve the list of monster titles from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM monsters")
    monsters = cursor.fetchall()
    conn.close()
    return monsters

def get_monster_details(monster_id):
    """Retrieve full details of a specific monster by ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT title, full_body FROM monsters WHERE id = ?", (monster_id,))
    monster = cursor.fetchone()
    conn.close()
    return monster

# Create the GUI application
class MonsterExplorer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Monster Data Explorer")
        self.geometry("800x600")
        
        # Create the main layout
        self.create_widgets()

    def create_widgets(self):
        # Create a frame for the monster list
        self.left_frame = ttk.Frame(self, width=200)
        self.left_frame.pack(side="left", fill="y")

        # Monster list label
        ttk.Label(self.left_frame, text="Monster List").pack(pady=10)

        # Listbox to display monster titles
        self.monster_listbox = tk.Listbox(self.left_frame)
        self.monster_listbox.pack(fill="y", expand=True, padx=10, pady=10)
        self.monster_listbox.bind("<<ListboxSelect>>", self.on_monster_select)

        # Populate the listbox with monster titles
        self.populate_monster_list()

        # Create a frame for monster details
        self.right_frame = ttk.Frame(self)
        self.right_frame.pack(side="right", fill="both", expand=True)

        # Title label
        self.title_label = ttk.Label(self.right_frame, text="Monster Title", font=("Arial", 16))
        self.title_label.pack(pady=10)

        # HTML frame to display full body text using tkinterweb's HtmlFrame
        self.html_frame = HtmlFrame(self.right_frame)
        self.html_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def populate_monster_list(self):
        """Populate the Listbox with monster titles."""
        monsters = get_monster_list()
        for monster in monsters:
            self.monster_listbox.insert(tk.END, f"{monster[0]}: {monster[1]}")

    def on_monster_select(self, event):
        """Load and display details of the selected monster."""
        try:
            # Get selected item
            selection = self.monster_listbox.curselection()
            if not selection:
                return

            index = selection[0]
            monster_id = int(self.monster_listbox.get(index).split(":")[0])

            # Fetch monster details
            monster = get_monster_details(monster_id)
            if monster:
                self.title_label.config(text=monster[0])
                self.html_frame.load_html(monster[1])  # Use load_html to load the HTML string

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

# Run the application
if __name__ == "__main__":
    app = MonsterExplorer()
    app.mainloop()
