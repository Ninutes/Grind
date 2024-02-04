import random

from selfcord.ext import commands, tasks
from time import time
from random import randrange

from config import GLOBAL



class CustomTask(commands.Cog):
    """The description for Tasks goes here."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.delay = random.randint(1,3)
        self.c_time = 0
        self.c_cd = 0
        self.c_text = None
    
    def cog_check(self, ctx: commands.Context):
        return ctx.author.id == GLOBAL.get_value('userID') or ctx.author.id in GLOBAL.get_value('allowedID')
    
    @commands.command(aliases=['c', 'custom'])
    async def start_custom(self, ctx: commands.Context, text: str, cooldown: int ):
        GLOBAL.set_channel(ctx.channel)
        self.c_cd = cooldown
        self.c_text = text
        if self.custom_runner.is_running():
            return
        self.custom_runner.start()
    
    @commands.command(aliases=['cstop'])
    async def stop_custom(self, ctx: commands.Context):
        await ctx.message.delete()
        self.custom_runner.cancel()
    
    @tasks.loop(seconds=5)
    async def custom_runner(self):
        if (
            time() - self.c_time >= randrange(self.c_cd, self.c_cd + 2)
            and GLOBAL.g_channel is not None
        ):
            await GLOBAL.g_channel.typing()
            await GLOBAL.g_channel.send(self.c_text)
            self.c_time = time()

async def setup(bot):
    await bot.add_cog(CustomTask(bot))
