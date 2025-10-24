import json
import os

def load_history(file_path, user_id):
    """
    Load conversation history for a specific user.
    Always returns a list, even if the file or user entry doesn't exist.
    """
    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        data = {}

    # Ensure valid structure
    if not isinstance(data, dict):
        data = {}

    history = data.get(user_id, [])
    if not isinstance(history, list):
        history = []

    return history

def save_history(file_path, user_id, history):
    """Save conversation history for a specific user."""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}

    # Ensure data is a dictionary
    if not isinstance(data, dict):
        data = {}

    # Update user history
    data[user_id] = history

    # Save back to file
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
