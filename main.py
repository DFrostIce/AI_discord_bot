import discord
from discord.ext import commands
import yaml
import os

# ---- Load config ----
with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

TOKEN = config["discord_token"]

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ---- Load Cogs ----
@bot.event
async def on_ready():
    print(f"{bot.user} is online!")
    print(f"Connected to {len(bot.guilds)} servers")

async def load_cogs():
    for filename in os.listdir("./src/cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            await bot.load_extension(f"src.cogs.{filename[:-3]}")
            print(f"Loaded cog: {filename}")

async def main():
    await load_cogs()
    await bot.start(TOKEN)

import asyncio
asyncio.run(main())
