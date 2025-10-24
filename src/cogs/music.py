from discord.ext import commands
from discord import FFmpegPCMAudio, PCMVolumeTransformer
import yt_dlp
import asyncio

music_queue = {}
default_volume = 0.5  # Default playback volume (50%)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.volumes = {}  # Store per-guild volume settings

    @commands.command(name="play")
    async def play(self, ctx, *, query: str):
        if not ctx.author.voice:
            await ctx.send("❌ You must be in a voice channel to play music.")
            return

        voice_client = ctx.voice_client
        if not voice_client:
            await ctx.author.voice.channel.connect()
            voice_client = ctx.voice_client

        guild_id = ctx.guild.id
        if guild_id not in music_queue:
            music_queue[guild_id] = []
        if guild_id not in self.volumes:
            self.volumes[guild_id] = default_volume

        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'default_search': 'ytsearch',
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            url = info['url']
            title = info['title']

        music_queue[guild_id].append((url, title))
        await ctx.send(f"🎵 Added **{title}** to the queue.")

        if not voice_client.is_playing():
            await self.play_next(ctx)

    async def play_next(self, ctx):
        guild_id = ctx.guild.id
        if guild_id not in music_queue or not music_queue[guild_id]:
            await ctx.send("✅ Music queue finished.")
            return

        url, title = music_queue[guild_id].pop(0)
        voice_client = ctx.voice_client
        volume = self.volumes.get(guild_id, default_volume)

        source = FFmpegPCMAudio(url)
        source = PCMVolumeTransformer(source, volume=volume)

        await ctx.send(f"🎶 Now playing: **{title}** (🔊 Volume: {int(volume * 100)}%)")
        voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))

    @commands.command(name="skip")
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏭ Skipped the current track.")

    @commands.command(name="pause")
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸ Paused playback.")

    @commands.command(name="resume")
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶ Resumed playback.")

    @commands.command(name="volume")
    async def set_volume(self, ctx, volume: float):
        """Adjust playback volume (0.0 - 2.0)."""
        if not ctx.voice_client:
            await ctx.send("❌ I must be connected to a voice channel.")
            return

        if volume < 0 or volume > 2:
            await ctx.send("⚠️ Volume must be between `0.0` (mute) and `2.0` (200%).")
            return

        guild_id = ctx.guild.id
        self.volumes[guild_id] = volume

        if ctx.voice_client.source and isinstance(ctx.voice_client.source, PCMVolumeTransformer):
            ctx.voice_client.source.volume = volume

        await ctx.send(f"🔊 Volume set to **{int(volume * 100)}%**.")

async def setup(bot):
    await bot.add_cog(Music(bot))
