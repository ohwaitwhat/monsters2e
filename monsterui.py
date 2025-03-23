import tkinter as tk
from tkinter import ttk, messagebox
from tkinterweb import HtmlFrame
import sqlite3
import random
import re
from PIL import Image, ImageTk
import os

# Database connection
DB_PATH = 'db/monsters.db'

def get_monster_images(monster_id):
    """Retrieve images associated with a specific monster by its ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT image_url FROM images WHERE monster_id = ?", (monster_id,))
    images = cursor.fetchall()
    conn.close()
    return [image[0] for image in images]  # Extract image URLs from the tuples
    
def load_image(image_path):
    """Load an image from the local img directory and return a PhotoImage."""
    if os.path.exists(image_path):
        try:
            image = Image.open(image_path)
            image = image.resize((150, 150), Image.ANTIALIAS)  # Resize the image if needed
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return None
    else:
        print(f"Image path does not exist: {image_path}")
        return None

def get_monster_list(search_query=""):
    """Retrieve the list of monster titles from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = f"%{search_query.lower()}%"
    cursor.execute("SELECT id, title FROM monsters WHERE LOWER(title) LIKE ?", (query,))
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

def get_filtered_monsters(climate_terrain, num_monsters=1):
    """Retrieve monsters based on climate/terrain and randomly select num_monsters."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    climate_query = f"%{climate_terrain.lower()}%"
    cursor.execute("""
        SELECT m.id, m.title, sb.no_appearing 
        FROM monsters m
        JOIN statblocks sb ON m.id = sb.monster_id
        WHERE LOWER(sb.climate_terrain) LIKE ?
        ORDER BY RANDOM() LIMIT ?;
    """, (climate_query, num_monsters))
    monsters = cursor.fetchall()
    conn.close()
    print(f"Monsters found: {monsters}")  # Debugging
    return monsters

def parse_no_appearing(no_appearing_str):
    """Parse the 'No. Appearing' field (e.g., '1d6+1' or a number range) to generate the number of monsters."""
    if not no_appearing_str:
        print("No 'no_appearing' value provided. Defaulting to 1.")
        return 1

    try:
        # Try to match dice notation like 1d6+1 or similar
        match = re.match(r'(\d+)d(\d+)([+-]\d+)?', no_appearing_str)
        if match:
            num_dice = int(match.group(1))
            dice_size = int(match.group(2))
            modifier = int(match.group(3)) if match.group(3) else 0
            total = sum(random.randint(1, dice_size) for _ in range(num_dice)) + modifier
            return max(1, total)  # Ensure at least 1 appears
        else:
            # Fallback to a number or range like "1-3" or just "3"
            numbers = re.findall(r'\d+', no_appearing_str)
            if numbers:
                chosen_number = random.choice(list(map(int, numbers)))
                print(f"Choosing from range: {numbers}, selected: {chosen_number}")
                return chosen_number
            else:
                print(f"Unexpected format in 'no_appearing': {no_appearing_str}. Defaulting to 1.")
                return 1
    except Exception as e:
        print(f"Error parsing 'no_appearing': {no_appearing_str}, Exception: {e}")
        return 1

# Create the GUI application
class MonsterExplorer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Monster Data Explorer")
        self.geometry("800x600")
        
        # Create the main layout
        self.create_widgets()

    def create_widgets(self):
        # Create a frame for the search, monster list, and buttons
        self.left_frame = ttk.Frame(self, width=550)
        self.left_frame.pack(side="left", fill="y")

        # Search Box
        ttk.Label(self.left_frame, text="Search Monster").pack(pady=10)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.left_frame, textvariable=self.search_var)
        self.search_entry.pack(pady=5)
        self.search_entry.bind("<KeyRelease>", self.on_search)

        # "Generate Encounter" button
        self.generate_button = ttk.Button(self.left_frame, text="Generate Encounter", command=self.open_encounter_screen)
        self.generate_button.pack(pady=10)

        # Monster list label
        ttk.Label(self.left_frame, text="Monster List").pack(pady=10)

        # Listbox to display monster titles
        self.monster_listbox = tk.Listbox(self.left_frame)
        self.monster_listbox.pack(fill="y", expand=True, padx=10, pady=10)
        self.monster_listbox.bind("<<ListboxSelect>>", self.on_monster_select)

        # Populate the listbox with all monsters initially
        self.populate_monster_list()

        # Create a frame for monster details
        self.right_frame = ttk.Frame(self)
        self.right_frame.pack(side="right", fill="both", expand=True)

        # Title label
        self.title_label = ttk.Label(self.right_frame, text="Monster Title", font=("Arial", 16))
        self.title_label.pack(pady=10)
        
        # Display image
        self.image_label = ttk.Label(self.right_frame)
        self.image_label.pack(pady=10)

        # HTML frame to display full body text using tkinterweb's HtmlFrame
        self.html_frame = HtmlFrame(self.right_frame)
        self.html_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def populate_monster_list(self, search_query=""):
        """Populate the Listbox with monster titles filtered by search query."""
        monsters = get_monster_list(search_query)
        self.monster_listbox.delete(0, tk.END)
        for monster in monsters:
            self.monster_listbox.insert(tk.END, f"{monster[0]}: {monster[1]}")

    def on_search(self, event):
        """Handle real-time search in the monster list."""
        search_query = self.search_var.get()
        self.populate_monster_list(search_query)

    def on_monster_select(self, event):
        """Load and display details and image of the selected monster."""
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

                # Get associated images
                image_paths = get_monster_images(monster_id)
                if image_paths:
                    image_path = os.path.join("img", image_paths[0])  # Assuming first image
                    image = load_image(image_path)
                    if image:
                        self.image_label.config(image=image)
                        self.image_label.image = image  # Keep a reference to prevent GC

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")


    def open_encounter_screen(self):
        """Open the screen to configure and generate an encounter."""
        encounter_window = tk.Toplevel(self)
        encounter_window.title("Generate Encounter")
        encounter_window.geometry("400x300")

        # Label and input for Climate/Terrain
        ttk.Label(encounter_window, text="Climate/Terrain:").pack(pady=10)
        climate_terrain = tk.StringVar(value="")
        ttk.Entry(encounter_window, textvariable=climate_terrain).pack(pady=5)

        # Button to generate the encounter
        def generate_encounter():
            monsters = get_filtered_monsters(climate_terrain.get())
            if not monsters:
                print("No monsters found.")  # Debugging
                messagebox.showinfo("No Monsters Found", "No monsters found matching the criteria.")
                return
            
            # Monster is a tuple with id, title, and no_appearing fields, so unpack it
            monster_id, monster_title, no_appearing = monsters[0]  # Since you're fetching multiple monsters, access the first one
            print(f"Monster selected: {monster_title}, Appearing: {no_appearing}")  # Debugging

            # Use no_appearing field to determine number of monsters
            num_appearing = parse_no_appearing(no_appearing)  
            encounter_text = f"{monster_title} (x{num_appearing})"
            print(f"Encounter generated: {encounter_text}")  # Debugging
            messagebox.showinfo("Generated Encounter", encounter_text)

            # Automatically display the monster in the browser
            self.show_monster(monster_id)

        ttk.Button(encounter_window, text="Generate", command=generate_encounter).pack(pady=20)

    def show_monster(self, monster_id):
        """Show the monster in the monster browser."""
        # Select the monster in the listbox
        for i in range(self.monster_listbox.size()):
            if self.monster_listbox.get(i).startswith(f"{monster_id}:"):
                self.monster_listbox.select_clear(0, tk.END)
                self.monster_listbox.select_set(i)
                self.monster_listbox.event_generate("<<ListboxSelect>>")
                break

# Run the application
if __name__ == "__main__":
    app = MonsterExplorer()
    app.mainloop()
