import re
import aiohttp
from redbot.core import commands
from redbot.core.bot import Red
from redbot.cogs.audio.core import Audio

class Autoplay(commands.Cog):
    def __init__(self, bot: Red):
        self.bot = bot

    @commands.Cog.listener()
    async def on_audio_track_end(self, guild, track, reason):
        print(f"[Autoplay] Track ended in {guild.name}: {track.uri} (reason: {reason})")

        if reason != "FINISHED":
            return

        audio_cog: Audio = self.bot.get_cog("Audio")
        if not audio_cog:
            print("[Autoplay] Audio cog not found")
            return

        player = audio_cog._player_manager.get(guild.id)
        if not player or not player.queue.is_empty():
            print("[Autoplay] Player missing or queue not empty")
            return

        if not track.uri.startswith("https://www.youtube.com/watch"):
            print("[Autoplay] Track is not a YouTube video")
            return
