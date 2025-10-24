import discord
from discord.ext import commands
import re
from ..utils.memory import load_history, save_history
from ..llm_call import query_ollama
import yaml
import os
from TTS.api import TTS
from discord import FFmpegPCMAudio
import asyncio
import requests
import io
from pollinations import Image

# Load config
with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

HISTORY_FILE = config["history_file"]
MODEL = config['model']
CHUNK_SIZE = 2000

# Initialize TTS model
TTS_MODEL = "tts_models/en/vctk/vits"
tts_engine = TTS(TTS_MODEL)

def clean_output(text: str) -> str:
    text = re.sub(r"\[.*?\]", "", text)
    return text.strip()

def chunk_message(message, max_length=500):
    chunks = []
    text = clean_output(message)
    while len(text) > max_length:
        split_index = text.rfind(" ", 0, max_length)
        if split_index == -1:
            split_index = max_length
        chunks.append(text[:split_index])
        text = text[split_index:].lstrip()
    if text:
        chunks.append(text)
    return chunks

class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="forgetme")
    async def clear_history(self, ctx):
        user_id = str(ctx.author.id)
        user_data = load_history(HISTORY_FILE, user_id)
        if user_data:
            save_history(HISTORY_FILE, user_id, [])
            await ctx.send("🧠 Your chat history has been cleared!")
        else:
            await ctx.send("ℹ You don’t have any chat history yet.")

    @commands.command(name="set_personality")
    async def set_personality(self, ctx, *, prompt: str):
        """Set the personality prompt for the AI (requires manage guild permission in servers)."""
        if ctx.guild and not ctx.author.guild_permissions.manage_guild:
            await ctx.send("❌ You don't have permission to change the personality.")
            return
        if not prompt:
            await ctx.send("❌ Please provide a personality prompt.")
            return
        from ..utils.personality import save_personality
        save_personality(ctx.guild.id if ctx.guild else ctx.author.id, prompt)
        await ctx.send("✅ Personality updated!")
            
    @commands.command(name="create_img")
    async def gen_image(self, ctx, *, prompt: str = None):
        """Generate an image using the pollinations SDK."""
        if not prompt or prompt.strip() == "":
            await ctx.send("❌ Please provide a image generation request.")
            return
        await ctx.send(f"🖼 Generating image for: *{prompt}* ...")
        for attempt in range(3):
            try:
                image_model = Image(model=config.get("image_model", "flux"), nologo=config.get("image_noLogo", True))
                img = await asyncio.to_thread(image_model, prompt)  # synchronous, but ran in thread
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                buffer.seek(0)
                await ctx.send(file=discord.File(buffer, filename="image.png"))
                return
            except Exception as e:
                if attempt < 2:
                    await asyncio.sleep(2)
                else:
                    await ctx.send(f"⚠️ Error generating image: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if self.bot.user.mentioned_in(message):
            ctx = await self.bot.get_context(message)
            user_id = str(message.author.id)
            message.content = message.content.replace(f"<@{self.bot.user.id}>", "").strip()

            user_history = load_history(HISTORY_FILE, user_id)
            message_chunks = chunk_message(message.content, CHUNK_SIZE)
            for chunk in message_chunks:
                user_history.append({"role": "user", "content": chunk})

            guild_id = message.guild.id if message.guild else message.author.id
            reply = await query_ollama(user_id, message.content, user_history, MODEL, guild_id)
            reply_chunks = chunk_message(reply, CHUNK_SIZE)
            for chunk in reply_chunks:
                user_history.append({"role": "assistant", "content": chunk})

            save_history(HISTORY_FILE, user_id, user_history)

            # Send text reply
            for chunk in reply_chunks:
                await message.reply(chunk)

            # 🎙 Play TTS using Voice cog
            if message.guild.voice_client:
                # Get the Voice cog instance
                voice_cog = self.bot.get_cog("Voice")
                if voice_cog:
                    await voice_cog.play_tts_in_vc(reply, ctx)


async def setup(bot):
    await bot.add_cog(Chat(bot))
