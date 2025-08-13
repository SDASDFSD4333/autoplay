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
        if reason != "FINISHED":
            return

        audio_cog: Audio = self.bot.get_cog("Audio")
        if not audio_cog:
            return

        player = audio_cog._player_manager.get(guild.id)
        if not player or not player.queue.is_empty():
            return

        if not track.uri.startswith("https://www.youtube.com/watch"):
            return

        related = await self.get_related_youtube(track.uri)
        if not related:
            return

        try:
            await audio_cog.play(guild, related)
        except Exception as e:
            print(f"[Autoplay] Failed to play related track: {e}")

    async def get_related_youtube(self, url):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    html = await resp.text()
            matches = re.findall(r'watch\?v=([\w-]{11})', html)
            seen = set()
            for vid in matches:
                if vid not in url and vid not in seen:
                    seen.add(vid)
                    return f"https://www.youtube.com/watch?v={vid}"
        except Exception as e:
            print(f"[Autoplay] Error fetching related video: {e}")
        return None

async def setup(bot):
    await bot.add_cog(Autoplay(bot))

