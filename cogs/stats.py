import asyncio
from selfcord.ext import commands, tasks
import selfcord

from datetime import datetime, time
from config import GLOBAL
from modules.logger import LOG

class Stats(commands.Cog):
    """The description for Stats goes here."""

    def __init__(self, bot : commands.Bot):
        self.bot = bot
        self.reset_owostats.start()

    def cog_check(self, ctx: commands.Context):
        return ctx.author.id in GLOBAL.get_value('allowedID') or ctx.author.id == ctx.me.id
    async def _delete_msg(self, ctx: commands.Context):
        try:
            await ctx.message.delete()
        except Exception:
            return  
    @commands.command(aliases=['owostats'])
    async def stats(self, ctx: commands.Context, *args):
        await self._delete_msg(ctx)
        flag = None
        if args:
            flag = args[0].lower()
            if flag in ['daily', 'weekly', 'monthly', 'total']:
                flag = flag
        else:
            flag = None
        owo_stats = GLOBAL.get_value('OwO')
        msg = ''
        try:
            if flag is not None and owo_stats:
                stats = owo_stats.get(flag)
                msg = f"```py\nOwO : {stats['owo']}, Hunt : {stats['hunt']}, Battle : {stats['battle']}```"
            else:
                stats = GLOBAL.get_value('OwO')
                for i, v in stats.items():
                    msg += f"**{i.upper()}**```py\nOwO : {v['owo']}, Hunt : {v['hunt']}, Battle: {v['battle']}```"
            await LOG.info(f"**{flag.upper() if flag is not None else 'OWO'} STATS**\n{msg}")
        except Exception as e:
            await LOG.error(f'```py\n{e}```')
    @commands.Cog.listener()
    async def on_message(self, message : selfcord.Message):
        if message.author.id == GLOBAL.get_value('user.ID'):
            if message.content.lower() == 'owo':
                for key in ['OwO.daily.owo', 'OwO.weekly.owo', 'OwO.monthly.owo', 'OwO.total.owo']:
                    GLOBAL.set_owostats(key)
        
    @tasks.loop(time=time(hour=7))
    async def reset_owostats(self):
        await LOG.info(f"**Your Daily OwO**\n```py\nOwO : {GLOBAL.get_value('OwO.daily.owo')}, Hunt : {GLOBAL.get_value('OwO.daily.hunt')}, Battle : {GLOBAL.get_value('OwO.daily.battle')}```")
        await asyncio.sleep(1)
        GLOBAL.reset_owostats('daily')
        if datetime.now().weekday() == 0:
            await LOG.info(f"**Your Weekly OwO**\n```py\nOwO : {GLOBAL.get_value('OwO.weekly.owo')}, Hunt : {GLOBAL.get_value('OwO.weekly.hunt')}, Battle : {GLOBAL.get_value('OwO.weekly.battle')}```")
            await asyncio.sleep(1)
            GLOBAL.reset_owostats('weekly')
        if datetime.day == 1:
            await LOG.info(f"**Your Monthly OwO**\n```py\nOwO : {GLOBAL.get_value('OwO.monthly.owo')}, Hunt : {GLOBAL.get_value('OwO.monthly.hunt')}, Battle : {GLOBAL.get_value('OwO.monthly.battle')}```")
            await asyncio.sleep(1)
            GLOBAL.reset_owostats('monthly')
    @reset_owostats.before_loop
    async def reset_owostats_before_loop(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Stats(bot))
