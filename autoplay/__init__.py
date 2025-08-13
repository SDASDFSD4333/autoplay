# __init__.py
from .autoplay import Autoplay

async def setup(bot):
    await bot.add_cog(Autoplay(bot))
