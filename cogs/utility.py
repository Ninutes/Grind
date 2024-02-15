import asyncio
import psutil
from selfcord.ext import commands

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
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=1)
        await ctx.send(f'```py\n🏓... pong, latency: {round(self.bot.latency * 1000)} ms, memory : {memory.percent}%, cpu : {cpu}%```', delete_after=10)
    @commands.command(aliases=['restart'])
    async def die(self, ctx: commands.Context):
        await self._delete_msg(ctx)
        await LOG.info(f'restarting self-bot')
        await self.bot.close()
        looper = asyncio.get_event_loop()
        looper.stop()
    @commands.command()
    async def tes_tele(self, ctx: commands.Context, msg):
        await self._delete_msg(ctx)
        return await send_tele(msg)
    @commands.command()
    async def parse(self, ctx: commands.Context, msgID):
        await self._delete_msg(ctx)
        msg = await ctx.channel.fetch_message(int(msgID))
        if msg.embeds:
            await LOG.info(f'```py\n{msg.embeds[0].to_dict()}```')
        else:
            await LOG.info(f'```py\n{msg.content}```')
    @commands.command()
    async def reload(self, ctx: commands.Context, *, cog: str):
        await self._delete_msg(ctx)
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            await LOG.info(f"`✅` **{cog.upper()}** cog reloaded")
        except Exception as e:
            await LOG.info(f"`❌` Failed to reload **{cog.upper()}** cog\n{e}")
    @commands.command()
    async def load(self, ctx: commands.Context, *, cog: str):
        await self._delete_msg(ctx)
        try:
            await self.bot.load_extension(f"cogs.{cog}")
            await LOG.info(f"`✅` **{cog.upper()}** cog loaded")
        except Exception as e:
            await LOG.info(f"`❌` Failed to load **{cog.upper()}** cog\n{e}")
    @commands.command()
    async def unload(self, ctx: commands.Context, *, cog: str):
        await self._delete_msg(ctx)
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            await LOG.info(f"`✅` **{cog.upper()}** cog unloaded")
        except Exception as e:
            await LOG.info(f"`❌` Failed to unload **{cog.upper()}** cog\n{e}")
async def setup(bot):
    await bot.add_cog(Utility(bot))
