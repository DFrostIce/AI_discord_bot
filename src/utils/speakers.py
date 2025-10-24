import json
import os
import yaml

# Load config
with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

SPEAKER_FILE = config.get("speaker_file", "data/memory/speakers.json")

# Make sure the folder exists
os.makedirs(os.path.dirname(SPEAKER_FILE), exist_ok=True)

def load_speaker(user_id):
    """Load a user's speaker. Returns None if not set."""
    if not os.path.exists(SPEAKER_FILE):
        return None
    with open(SPEAKER_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {}
    return data.get(user_id)

def save_speaker(user_id, speaker):
    """Save a user's speaker choice."""
    if os.path.exists(SPEAKER_FILE):
        with open(SPEAKER_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}
    data[user_id] = speaker
    with open(SPEAKER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
