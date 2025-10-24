# AI_discord_bot

A Discord bot integrating AI chat via Ollama, voice synthesis, music playback, and image generation.

## Features

- **AI Chat**: Role-play as Nina using Ollama LLM with per-guild personalities
- **Voice Synthesis**: TTS using Coqui TTS, customizable per user speaker
- **Music Playback**: YouTube audio streaming via yt-dlp
- **Image Generation**: Generate images using Pollinations.ai
- **Personality Management**: Guild-specific personalities via commands

## Setup

1. Install Python 3.11+
2. `pip install -r requirements.txt`
3. Configure `config.yaml`
   - Discord token
   - Ollama model
   - Image parameters
   - TTS settings
4. Run Ollama with llama2:latest
5. `python main.py`

## Usage

Bot responds to mentions. Commands:
- `!create_img <prompt>` - Generate image
- `!set_personality <prompt>` - Set guild personality (manage_guild permission)
- `!forgetme` - Clear chat history

Music:
- `!play <query>` - Play from YouTube
- `!skip` - Skip track
- `!pause` - Pause
- `!resume` - Resume
- `!volume <0-2>` - Set volume

Voice:
- `!say <text>` - Speak in voice channel
- `!join` - Join voice channel
- `!leave` - Leave
- `!listspeakers` - List TTS speakers
- `!setspeaker <id>` - Set personal speaker

## Structure

- `main.py`: Bot entry point
- `src/ollama_nina2/`: Package
  - `cogs/`: Discord commands
  - `utils/`: Helper functions
  - `llm_call.py`: Ollama interface
- `config.yaml`: Configuration
- `requirements.txt`: Dependencies
- `data/`: Memory files, audio

## Contributing

Follow Python conventions.

## License

MIT
