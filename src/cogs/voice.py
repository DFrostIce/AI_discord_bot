from discord.ext import commands
import os
from discord import FFmpegPCMAudio
from TTS.api import TTS
from ..utils.speakers import load_speaker, save_speaker
import yaml

# Load config
with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

TTS_MODEL = config.get("tts_model", "tts_models/en/vctk/vits")
tts_engine = TTS(TTS_MODEL)

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def play_tts_in_vc(self, text: str, ctx):
        voice_client = ctx.guild.voice_client
        if not voice_client or voice_client.is_playing():
            return

        os.makedirs("temp", exist_ok=True)
        tts_path = f"temp/reply_{ctx.author.id}.wav"

        # Clean text to skip non-normal language parts (e.g., *actions*)
        import re
        cleaned_text = re.sub(r'\*.*?\*', '', text).strip()

        if not cleaned_text:
            return  # Skip TTS if no normal text remains

        # Load user-specific speaker, fallback to default
        speaker = load_speaker(str(ctx.author.id)) or config.get("default_tts_speaker", "p225")

        tts_engine.tts_to_file(text=cleaned_text, file_path=tts_path, speaker=speaker)

        source = FFmpegPCMAudio(tts_path)
        voice_client.play(source)
        
    @commands.command(name="say")
    async def say(self, ctx, text: str):
        """Says whatever text you send"""
        if text:
            if ctx.voice_client:
                await self.play_tts_in_vc(text,ctx)
            else:
                await ctx.author.voice.channel.connect()
                await self.play_tts_in_vc(text,ctx)
        else:
            await ctx.send("❌ No text sent.")

    @commands.command(name="join")
    async def join(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.send(f"🎙 Joined {channel.name}!")
        else:
            await ctx.send("❌ You’re not in a voice channel.")

    @commands.command(name="leave")
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("👋 Left the voice channel.")
        else:
            await ctx.send("❌ I’m not connected to any voice channel.")

    @commands.command(name="stop")
    async def stop(self, ctx):
        """Stops playback and disconnects."""
        if ctx.voice_client:
            ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
            await ctx.send("🛑 Stopped all playback and left the voice channel.")
            
    @commands.command(name="listspeakers")
    async def list_speakers(self, ctx):
        """List all available TTS speakers."""
        speakers = tts_engine.speakers  # List of all speakers
        if not speakers:
            await ctx.send("❌ No speakers available.")
            return

        # Discord messages have a character limit, so we split if needed
        chunk_size = 1000
        message = ", ".join(speakers)
        for i in range(0, len(message), chunk_size):
            await ctx.send(message[i:i+chunk_size])
    
    @commands.command(name="setspeaker")
    async def set_speaker(self, ctx, speaker_id: str):
        """Set your preferred TTS speaker."""
        user_id = str(ctx.author.id)
        if speaker_id not in tts_engine.speakers:
            await ctx.send(f"❌ Invalid speaker. Available: {', '.join(tts_engine.speakers[:5])} ...")
            return

        save_speaker(user_id, speaker_id)
        await ctx.send(f"✅ Your TTS speaker is now set to `{speaker_id}`.")

async def setup(bot):
    await bot.add_cog(Voice(bot))
