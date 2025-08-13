import re
import aiohttp
from redbot.core import commands
from redbot.core.bot import Red
from redbot.cogs.audio.core import Audio

class Autoplay(commands.Cog):
    def __init__(self, bot: Red):
        self.bot = bot

    @commands.Cog.listener()
    async def on_audio_track_start(self, guild, track):
        """Kill Red's autoplay as soon as a track starts."""
        audio_cog: Audio = self.bot.get_cog("Audio")
        if not audio_cog:
            return
        try:
            player = await audio_cog.get_player(guild)
            if player.autoplay:
                player.autoplay = False
                print(f"[Autoplay] Disabled core autoplay for {guild.name}")
        except Exception as e:
            print(f"[Autoplay] Error disabling core autoplay: {e}")

    @commands.Cog.listener()
    async def on_audio_track_end(self, guild, track, reason):
        print(f"[Autoplay] Track ended in {guild.name}: {track.uri} (reason: {reason})")

        if reason not in ("FINISHED", "STOPPED"):
            print("[Autoplay] Ignored due to reason:", reason)
            return

        audio_cog: Audio = self.bot.get_cog("Audio")
        if not audio_cog:
            print("[Autoplay] Audio cog not found")
            return

        try:
            player = await audio_cog.get_player(guild)
            player.autoplay = False  # extra guarantee
        except Exception as e:
            print(f"[Autoplay] Could not get player: {e}")
            return

        if not player or not player.connected:
            print("[Autoplay] No active player")
            return

        if not player.queue.is_empty():
            print("[Autoplay] Queue not empty — skipping")
            return

        if not track.uri.startswith("https://www.youtube.com/watch"):
            print("[Autoplay] Track is not a YouTube video")
            return

        related = await self.get_related_youtube(track.uri)
        print(f"[Autoplay] Related video: {related}")
        if not related:
            return

        try:
            await audio_cog.play(guild, related)
            print(f"[Autoplay] Queued related track: {related}")
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

    @commands.command()
    async def testautoplay(self, ctx, url: str):
        """Force autoplay logic manually with a YouTube URL."""
        related = await self.get_related_youtube(url)
        if related:
            await ctx.send(f"Related video: {related}")
        else:
            await ctx.send("No related video found.")

async def setup(bot):
    await bot.add_cog(Autoplay(bot))
