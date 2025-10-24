import os
import json
import yaml

# Load config
with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

PERSONALITY_FILE = config.get("personality_file", "memory/personality.json")
DEFAULT_PERSONALITY_ORIGINAL = "You are Nina, an introvert AI companion who doesn't like to talk much but is helpful and offers humanlike conversations."
DEFAULT_PERSONALITY = config.get("base_personality", DEFAULT_PERSONALITY_ORIGINAL)

def load_personality(guild_id):
    """Load personality prompt for a guild from file, or return default if not set."""
    guild_id = str(guild_id)
    if not os.path.exists(PERSONALITY_FILE):
        return DEFAULT_PERSONALITY

    try:
        with open(PERSONALITY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            data = {}
        return data.get(guild_id, {}).get("prompt", DEFAULT_PERSONALITY)
    except (json.JSONDecodeError, IOError):
        return DEFAULT_PERSONALITY

def save_personality(guild_id, prompt):
    """Save the personality prompt for a guild to file."""
    guild_id = str(guild_id)
    if os.path.exists(PERSONALITY_FILE):
        try:
            with open(PERSONALITY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}
    else:
        data = {}

    if not isinstance(data, dict):
        data = {}

    data[guild_id] = {"prompt": prompt}
    try:
        with open(PERSONALITY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"Error saving personality file: {e}")
