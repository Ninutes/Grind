from typing import Optional
from selfcord.ext import commands
import selfcord

from config import GLOBAL
from modules.logger import LOG, send_tele

class Utility(commands.Cog):
    """The description for Utility goes here."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_check(self, ctx: commands.Context):
        return ctx.author.id in GLOBAL.get_value('allowedID')

    @commands.command(aliases=['pong'])
    async def ping(self, ctx: commands.Context):
        await ctx.message.delete()
        await ctx.send(f'🏓... pong `{round(self.bot.latency * 1000)}`ms', delete_after=10)

    @commands.command(aliases=['restart'])
    async def die(self, ctx: commands.Context):
        await ctx.message.delete()
        LOG.info(f'restarting self-bot')
        await self.bot.close()
    @commands.command()
    async def tes_tele(self, ctx: commands.Context, msg):
        await ctx.message.delete()
        return send_tele(msg)
    @commands.command()
    async def parse(self, ctx: commands.Context, msgID):
        await ctx.message.delete()
        msg = await ctx.channel.fetch_message(int(msgID))
        if msg.embeds:
            await ctx.send(f'```py\n{msg.embeds[0].to_dict()}```')
        else:
            await ctx.send(f'```py\n{msg.content}```')
    @commands.command()
    async def reload(self, ctx: commands.Context, *, cog: str):
        await ctx.message.delete()
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            await ctx.send(content=f"`✅` **{cog.upper()}** cog reloaded", delete_after=3)
        except Exception as e:
            await ctx.send(content=f"`❌` Failed to reload **{cog.upper()}** cog\n{e}", delete_after=3)
    @commands.command()
    async def load(self, ctx: commands.Context, *, cog: str):
        await ctx.message.delete()
        try:
            await self.bot.load_extension(f"cogs.{cog}")
            await ctx.send(content=f"`✅` **{cog.upper()}** cog loaded", delete_after=3)
        except Exception as e:
            await ctx.send(content=f"`❌` Failed to load **{cog.upper()}** cog\n{e}", delete_after=3)
    @commands.command()
    async def unload(self, ctx: commands.Context, *, cog: str):
        await ctx.message.delete()
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            await ctx.send(content=f"`✅` **{cog.upper()}** cog unloaded", delete_after=3)
        except Exception as e:
            await ctx.send(content=f"`❌` Failed to unload **{cog.upper()}** cog\n{e}", delete_after=3)
async def setup(bot):
    await bot.add_cog(Utility(bot))
