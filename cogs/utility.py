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
        return ctx.author.id in GLOBAL.get_value('allowedID') or ctx.author.id == ctx.me.id
    async def _delete_msg(self, ctx: commands.Context):
        try:
            await ctx.message.delete()
        except Exception:
            return
    
    @commands.command(aliases=['pong'])
    async def ping(self, ctx: commands.Context):
        await self._delete_msg(ctx)
        await ctx.send(f'🏓... pong `{round(self.bot.latency * 1000)}`ms', delete_after=10)

    @commands.command(aliases=['restart'])
    async def die(self, ctx: commands.Context):
        await self._delete_msg(ctx)
        LOG.info(f'restarting self-bot')
        await self.bot.close()
    @commands.command()
    async def tes_tele(self, ctx: commands.Context, msg):
        await self._delete_msg(ctx)
        return send_tele(msg)
    @commands.command()
    async def parse(self, ctx: commands.Context, msgID):
        await self._delete_msg(ctx)
        msg = await ctx.channel.fetch_message(int(msgID))
        if msg.embeds:
            LOG.info(f'```py\n{msg.embeds[0].to_dict()}```')
        else:
            LOG.info(f'```py\n{msg.content}```')
    @commands.command()
    async def reload(self, ctx: commands.Context, *, cog: str):
        await self._delete_msg(ctx)
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            LOG.info(f"`✅` **{cog.upper()}** cog reloaded")
        except Exception as e:
            LOG.info(f"`❌` Failed to reload **{cog.upper()}** cog\n{e}")
    @commands.command()
    async def load(self, ctx: commands.Context, *, cog: str):
        await self._delete_msg(ctx)
        try:
            await self.bot.load_extension(f"cogs.{cog}")
            LOG.info(f"`✅` **{cog.upper()}** cog loaded")
        except Exception as e:
            LOG.info(f"`❌` Failed to load **{cog.upper()}** cog\n{e}")
    @commands.command()
    async def unload(self, ctx: commands.Context, *, cog: str):
        await self._delete_msg(ctx)
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            LOG.info(content=f"`✅` **{cog.upper()}** cog unloaded")
        except Exception as e:
            LOG.info(f"`❌` Failed to unload **{cog.upper()}** cog\n{e}")
async def setup(bot):
    await bot.add_cog(Utility(bot))
