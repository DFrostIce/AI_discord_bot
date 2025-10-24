import ollama
from .utils.personality import load_personality
import asyncio
import yaml

# Load config
with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

MAX_TOKENS = config.get("max_new_tokens", 128)
TEMPERATURE = config.get("temperature", 0.7)

async def query_ollama(user_id, message, history, model, guild_id):

    messages = []

    # Start with the system prompt
    messages.append({"role": "system", "content": load_personality(guild_id)})

    # Add existing history
    messages.extend(history)

    # Add current user message
    messages.append({"role": "user", "content": message})

    try:
        print(f'Processing response to {user_id}')
        response = await asyncio.to_thread(ollama.chat, model, messages, options={'temperature': TEMPERATURE, 'num_predict': MAX_TOKENS})
        return response["message"]["content"]
    except Exception as e:
        return f"Error talking to Ollama: {e}"
