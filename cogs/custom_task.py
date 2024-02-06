import asyncio
from datetime import datetime
import random
import selfcord

from selfcord.ext import commands, tasks
from time import time
from random import randrange

from config import GLOBAL
from modules.logger import LOG, WB



class CustomTask(commands.Cog):
    """The description for Tasks goes here."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.delay = random.randint(1,3)
        self.c_time = {1:0,2:0,3:0,4:0,5:0}
        self.c_cd = 0
        self.c_text = None
        self.c_channel = None
        self.run_time = 0
    
    def cog_check(self, ctx: commands.Context):
        return ctx.author.id == GLOBAL.get_value('user.ID') or ctx.author.id in GLOBAL.get_value('allowedID')
    
    async def _delete_msg(self, ctx: commands.Context):
        try:
            await ctx.message.delete()
        except Exception:
            return
    async def counter_time(self):
        time = datetime.now() - self.run_time
        days, seconds = time.days, time.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return LOG.info(f'`⛔` stopping custom tasks after running in **{hours}H {minutes}M {seconds}S**')
    
    @commands.command(name='custom')
    async def custom_tasks(self, ctx :commands.Context, task_number:int, key: str, *, value: str):
        await self._delete_msg(ctx)
        data = GLOBAL.get_all_data('tasks')
        if task_number not in data:
            return LOG.failure(f'{task_number} is not a valid task. available tasks:{[task for task in data]}')
        if key not in data[task_number]:
            return LOG.failure(f'{key} is not a valid key. available keys:{[key for key in data[task_number]]}')
        GLOBAL.set_value(f'{task_number}.{key}', value)
        LOG.success(f'**TASK {task_number}** has been updated {key}  : {value}')
    
    @commands.command(aliases=['cstart', 'custom-start'])
    async def custom_start(self, ctx: commands.Context):
        await self._delete_msg(ctx)
        
        self.c_channel = ctx.channel
        self.run_time = datetime.now()
        
        if self.custom_looper.is_running():
            return
        
        self.custom_looper.start()
        
        LOG.info(f'Starting custom task in {self.c_channel.jump_url}')
    @commands.command(aliases=['cstop', 'custom-stop'])
    async def custom_stop(self, ctx: commands.Context):
        await self._delete_msg(ctx)
        self.custom_looper.cancel()
    @commands.command(name='show-tasks', aliases=['tasks'])
    async def show_tasks(self, ctx: commands.Context):
        await self._delete_msg(ctx)
        data = GLOBAL.get_value('tasks')
        embed = selfcord.Embed(
            color=selfcord.Color.blue()
        )
        value = ''
        for i, v in data.items():
            value += f'[ Task {i}: - Enable: {v["enable"]} - Time: {v["time"]} ]\n💬 Text: {v["text"]}\n\n'
        embed.add_field(name='Data Custom Tasks', value=f'```py\n{value}```')
        WB.send(
            username=ctx.me.display_name,
            avatar_url=ctx.me.display_avatar.url,
            embed=embed
        )
    async def custom_runner(self):
        data = GLOBAL.get_all_data()
        for num in data['tasks']:
            if data['tasks'][num]['enable']:
                c_time = int(data['tasks'][num]['time'])
                text = data['tasks'][num]['text'] if data['tasks'][num]['text'] else 'custom text'
                if time() - self.c_time[int(num)] >= c_time:
                    await self.c_channel.typing()
                    await asyncio.sleep(self.delay)
                    await self.c_channel.send(text)
                    self.c_time[int(num)] = time()
    @tasks.loop(seconds=5)
    async def custom_looper(self):
        await self.custom_runner()
    
    @custom_looper.after_loop
    async def after_loop_custom_looper(self):
        await self.counter_time()
async def setup(bot):
    await bot.add_cog(CustomTask(bot))
