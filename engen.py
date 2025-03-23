import json
import random

# Load the JSON file
def load_monster_data(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

# Function to filter monsters based on environment or other criteria (e.g., setting)
def filter_monsters(monsters, environment=None, setting=None):
    filtered = []
    for monster in monsters:
        monster_data = monster.get("monster_data", {})
        statblock = monster_data.get("statblock", {})
        
        # Log the current monster being processed
        print(f"Checking monster: {monster_data.get('title', 'Unknown Monster')}")

        # Ensure statblock and other data exist before accessing it
        if not statblock:
            print("Statblock missing, skipping this monster.")
            continue
        
        # Check for environment
        climate_terrain = statblock.get("Climate/Terrain", "")
        if environment and environment.lower() not in climate_terrain.lower():
            print(f"Environment '{climate_terrain}' does not match '{environment}', skipping.")
            continue
        
        # Check for setting
        monster_setting = monster_data.get("setting", "")
        if setting and setting.lower() != monster_setting.lower():
            print(f"Setting '{monster_setting}' does not match '{setting}', skipping.")
            continue

        print(f"Monster '{monster_data.get('title', 'Unknown Monster')}' matches the criteria.")
        filtered.append(monster)
    
    return filtered

# Generate random encounters
def generate_encounter(monsters, num_monsters=1):
    encounter = random.sample(monsters, min(num_monsters, len(monsters)))
    return encounter

# Display the encounter details
def display_encounter(encounter):
    for monster in encounter:
        monster_data = monster.get("monster_data", {})
        title = monster_data.get("title", "Unknown Monster")
        statblock = monster_data.get("statblock", {})
        
        # Use .get() safely with default values to avoid NoneType errors
        print(f"\nMonster: {title}")
        print(f"  Armor Class: {statblock.get('Armor Class', 'N/A')}")
        print(f"  Hit Dice: {statblock.get('Hit Dice', 'N/A')}")
        print(f"  Number Appearing: {statblock.get('No. Appearing', 'N/A')}")
        print(f"  THAC0: {statblock.get('THAC0', 'N/A')}")
        print(f"  XP Value: {statblock.get('XP Value', 'N/A')}")
        print(f"  Setting: {monster_data.get('setting', 'N/A')}")
        print(f"  Environment: {statblock.get('Climate/Terrain', 'N/A')}")
        print()

# Main function to load the data and generate a random encounter
def main():
    # Load monster data
    monsters = load_monster_data('ALL_MONSTERS.json')
    
    # Filter monsters (optional)
    # Example: Only get monsters in the "desert" environment from the "Dark Sun" setting
    filtered_monsters = filter_monsters(monsters, environment="desert", setting="Dark Sun")
    
    if not filtered_monsters:
        print("No monsters found with the specified criteria.")
        return
    
    # Generate a random encounter
    encounter = generate_encounter(filtered_monsters, num_monsters=3)
    
    # Display the encounter details
    display_encounter(encounter)

if __name__ == "__main__":
    main()
