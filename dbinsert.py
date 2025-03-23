import json
import sqlite3

# Load the JSON file
def load_monster_data(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        return json.load(file)

# Create the SQLite database schema
def create_schema(conn):
    with conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS monsters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            monster_key TEXT,
            title TEXT,
            setting TEXT,
            full_body TEXT,
            sources TEXT
        );
        ''')

        conn.execute('''
        CREATE TABLE IF NOT EXISTS statblocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            monster_id INTEGER,
            name TEXT,
            activity_cycle TEXT,
            alignment TEXT,
            armor_class TEXT,
            climate_terrain TEXT,
            damage_attack TEXT,
            diet TEXT,
            frequency TEXT,
            hit_dice TEXT,
            intelligence TEXT,
            magic_resistance TEXT,
            morale TEXT,
            movement TEXT,
            no_appearing TEXT,
            no_of_attacks TEXT,
            organization TEXT,
            size TEXT,
            special_attacks TEXT,
            special_defenses TEXT,
            thac0 TEXT,
            treasure TEXT,
            xp_value TEXT,
            FOREIGN KEY(monster_id) REFERENCES monsters(id)
        );
        ''')

        conn.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            monster_id INTEGER,
            image_url TEXT,
            FOREIGN KEY(monster_id) REFERENCES monsters(id)
        );
        ''')

# Insert data into the monsters table
def insert_monster(conn, monster_data):
    with conn:
        cursor = conn.cursor()

        # Ensure that sources is a list and not None
        sources = monster_data.get('sources', [])
        if sources is None:
            sources = []
        elif isinstance(sources, str):
            sources = [sources]  # Convert string to a list

        cursor.execute('''
        INSERT INTO monsters (monster_key, title, setting, full_body, sources)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            monster_data.get('monster_key'),
            monster_data.get('title'),
            monster_data['monster_data'].get('setting'),
            monster_data['monster_data'].get('fullBody'),
            ','.join(sources)  # Join the sources list into a string
        ))
        return cursor.lastrowid  # Return the id of the newly inserted monster


# Insert data into the statblocks table
def insert_statblock(conn, monster_id, statblock_name, statblock):
    with conn:
        conn.execute('''
        INSERT INTO statblocks (monster_id, name, activity_cycle, alignment, armor_class, climate_terrain, 
                                damage_attack, diet, frequency, hit_dice, intelligence, magic_resistance, 
                                morale, movement, no_appearing, no_of_attacks, organization, size, 
                                special_attacks, special_defenses, thac0, treasure, xp_value)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            monster_id,
            statblock_name,
            statblock.get('Activity Cycle'),
            statblock.get('Alignment'),
            statblock.get('Armor Class'),
            statblock.get('Climate/Terrain'),
            statblock.get('Damage/Attack'),
            statblock.get('Diet'),
            statblock.get('Frequency'),
            statblock.get('Hit Dice'),
            statblock.get('Intelligence'),
            statblock.get('Magic Resistance'),
            statblock.get('Morale'),
            statblock.get('Movement'),
            statblock.get('No. Appearing'),
            statblock.get('No. of Attacks'),
            statblock.get('Organization'),
            statblock.get('Size'),
            statblock.get('Special Attacks'),
            statblock.get('Special Defenses'),
            statblock.get('THAC0'),
            statblock.get('Treasure'),
            statblock.get('XP Value')
        ))

# Insert data into the images table
def insert_images(conn, monster_id, images):
    with conn:
        for image_url in images:
            conn.execute('''
            INSERT INTO images (monster_id, image_url)
            VALUES (?, ?)
            ''', (monster_id, image_url))

# Process each monster from JSON and insert it into the database
def process_monster_data(conn, monsters):
    for monster in monsters:
        # Insert the monster
        monster_id = insert_monster(conn, monster)
        
        # Insert the statblock(s)
        statblocks = monster['monster_data'].get('statblock')
        if statblocks:
            # Ensure statblocks is a dictionary before proceeding
            if isinstance(statblocks, dict):
                for statblock_name, statblock in statblocks.items():
                    insert_statblock(conn, monster_id, statblock_name, statblock)
        
        # Insert images (if any)
        images = monster['monster_data'].get('images', [])
        if images:
            insert_images(conn, monster_id, images)

# Main function to load the JSON and insert into SQLite
def main():
    # Load the JSON data
    json_file = 'ALL_Monsters.json'  # Update this with your actual file path
    monsters = load_monster_data(json_file)

    # Create the SQLite database connection
    conn = sqlite3.connect('all_monsters.db')

    # Create the database schema
    create_schema(conn)

    # Process the monster data and insert into the database
    process_monster_data(conn, monsters)

    # Close the connection
    conn.close()
    print("Data has been successfully inserted into the SQLite database.")

if __name__ == "__main__":
    main()
