import asyncio
from selfcord.ext import commands, tasks
import selfcord

from datetime import datetime, time
from config import GLOBAL
from modules.logger import LOG

commands_mapping = {
    'owo': ['OwO.daily.owo', 'OwO.weekly.owo', 'OwO.monthly.owo', 'OwO.total.owo'],
    'wh': ['OwO.daily.hunt', 'OwO.weekly.hunt', 'OwO.monthly.hunt', 'OwO.total.hunt'],
    'owoh': ['OwO.daily.hunt', 'OwO.weekly.hunt', 'OwO.monthly.hunt', 'OwO.total.hunt'],
    'wb': ['OwO.daily.battle', 'OwO.weekly.battle', 'OwO.monthly.battle', 'OwO.total.battle'],
    'owob': ['OwO.daily.battle', 'OwO.weekly.battle', 'OwO.monthly.battle', 'OwO.total.battle']
}

class Stats(commands.Cog):
    """The description for Stats goes here."""

    def __init__(self, bot : commands.Bot):
        self.bot = bot
        self.reset_owostats.start()

    def cog_check(self, ctx: commands.Context):
        return ctx.author.id in GLOBAL.get_value('allowedID') or ctx.author.id == ctx.me.id

    @commands.command(aliases=['owostats'])
    async def stats(self, ctx: commands.Context, *args):
        flag = None
        if args:
            flag = args[0].lower()
            if flag in ['daily', 'weekly', 'monthly', 'total']:
                flag = flag
        else:
            flag = None
        owo_stats = GLOBAL.get_value('OwO')
        msg = ''
        if flag is not None and owo_stats:
            stats = owo_stats.get(flag)
            msg = f"```py\nOwO : {stats['owo']}, Hunt : {stats['hunt']}, Battle : {stats['battle']}```"
        else:
            stats = GLOBAL.get_value('OwO')
            for i, v in stats.items():
                msg += f"**{i.upper()}**\n```py\nOwO : {v['owo']}, Hunt : {v['hunt']}, Battle: {v['battle']}```"
        await LOG.info(f"**{flag.upper() if flag is not None else 'OWO'} STATS**\n\n{msg}")
    @commands.Cog.listener()
    async def on_message(self, message : selfcord.Message):
        if message.author.id == GLOBAL.get_value('user.ID'):
            command = message.content.lower()
            if command in commands_mapping:
                for key in commands_mapping[command]:
                    GLOBAL.set_owostats(key)
        
    @tasks.loop(time=time(hour=7))
    async def reset_owostats(self):

        await LOG.info(f"**Your Daily OwO**\n```{GLOBAL.get_value('OwO.daily')}```")
        await asyncio.sleep(1)
        GLOBAL.reset_owostats('daily')
        if datetime.now().weekday() == 0:
            await LOG.info(f"**Your Weekly OwO**\n```{GLOBAL.get_value('OwO.weekly')}```")
            await asyncio.sleep(1)
            GLOBAL.reset_owostats('weekly')
        if datetime.day == 1:
            await LOG.info(f"**Your Monthly OwO**\n```{GLOBAL.get_value('OwO.monthly')}```")
            await asyncio.sleep(1)
            GLOBAL.reset_owostats('monthly')
    @reset_owostats.before_loop
    async def reset_owostats_before_loop(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Stats(bot))
