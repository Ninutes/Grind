from selfcord.ext import commands


class Tatsu(commands.Cog):
    """The description for Tatsu goes here."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(Tatsu(bot))
