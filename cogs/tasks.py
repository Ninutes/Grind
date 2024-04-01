import asyncio

import json
from typing import Optional
import selfcord
import random
import os
from selfcord.ext import commands, tasks
from time import time
from random import choice, randrange

from config import GLOBAL
from modules.logger import LOG
from datetime import datetime


class Tasks(commands.Cog):
    """The description for Tasks goes here."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.next_daily = 0
        self.ohb_time = 0
        self.pray_time = 0
        self.exp_time = 0
        self.delay = random.randint(1,3)
        self.run_time = 0
        self.ch_change_time = time()
        self.next_sleep_time = 0
        self.custom_time = 0
        self.sleep = False
        self.custom_run = 0
        self._counter = 0
        self.random_cmd_time = 0
        self.on_delay = False
        self.cmd_count = 0
    
    def cog_check(self, ctx: commands.Context):
        return ctx.author.id in GLOBAL.get_value('allowedID') or ctx.author.id == ctx.me.id
    
    async def cog_reload(self):
        if self.runner.is_running():
            return self.runner.cancel()
        

    async def cog_unload(self):
        if self.runner.is_running():
            return self.runner.cancel()
    
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
        if self.custom_run != 0:
            return await LOG.info(f'`⛔` stopping self-bot after running **{self._counter}** battles in **{hours}H {minutes}M {seconds}S**')
        return await LOG.info(f'`⛔` stopping self-bot after running in **{hours}H {minutes}M {seconds}S**')
    
    def start_task(self):
        if self.runner.is_running():
            return
        self.runner.start()

    def delay_task(self):
        if self.runner.is_running():
            self.on_delay = True
            self.runner.cancel()
            self.on_delay = False
        return
    @commands.Cog.listener()
    async def on_message(self, message: selfcord.Message):
        if not self.runner.is_running():
            return
        if not message.channel.id == GLOBAL.get_value('channelID'):
            return
        if self.sleep or GLOBAL.is_captcha:return
        if message.author.id == GLOBAL.get_value('user.ID') and message.content.startswith('owoh'):
            try:
                await self.bot.wait_for(
                    'message',
                    timeout=30,
                    check= lambda message: message.author.id == GLOBAL.owoID and message.channel.id == GLOBAL.get_value('channelID')
                )
            except asyncio.TimeoutError:
                self.runner.cancel()
                await LOG.failure(f'self-bot stopped because OwO didn\'t respond after 30 seconds')
                pass
    
    @commands.command(aliases=['start', 'resume'])
    async def start_grind(self, ctx: commands.Context, count: Optional[int] = None):
        if self.runner.is_running():
            return
        self._counter = 0
        self.custom_run = 0
        self.run_time = datetime.now()
        await self._delete_msg(ctx)
        GLOBAL.set_channel(ctx.channel)
        GLOBAL.is_captcha = False
        
        self.start_task()
        
        desc = f'`🟢` starting self-bot in {ctx.channel.jump_url}'
        if count:
            self.custom_run = count
            desc += f'\nand will stop after {count} battles reached'
        await LOG.info(desc)
    
    @commands.command(aliases=['stop', 'pause'])
    async def stop_grinding(self, ctx: commands.Context):
        await self._delete_msg(ctx)
        if self.runner.is_running():
            return self.runner.cancel()
        return await LOG.info('Self-bot is not running yet.')
    
    @commands.command(aliases=['ch'])
    async def change_channel(self, ctx: commands.Context):
        await self._delete_msg(ctx)
        GLOBAL.set_channel(ctx.channel)
        return await LOG.success(f'change channel to {ctx.channel.jump_url}')
    
    @commands.command()
    async def cek(self, ctx: commands.Context):
        await self._delete_msg(ctx)
        channel = self.bot.get_channel(GLOBAL.get_value('channelID'))
        running = '`🟢`' if self.runner.is_running() else '`⛔`'
        await ctx.send(f'> {running} here {channel.jump_url}', delete_after=10)
    
    async def random_hunt_battle(self) -> None:
        if (
            time() - self.ohb_time >= randrange(14, 17)
            and not GLOBAL.is_captcha
        ):
            await GLOBAL.g_channel.typing()
            await GLOBAL.g_channel.send('owo')
            self.cmd_count += 1
            
            await asyncio.sleep(self.delay)
            
            cmd = random.choice(["h", "b"])
            cmd2 = 'h' if cmd == 'b' else 'b'
            prefix = GLOBAL.get_value('owoprefix')
            self._counter += 1
            
            if not GLOBAL.is_captcha:
                await GLOBAL.g_channel.typing()
                await GLOBAL.g_channel.send(f'{prefix}{cmd}')
                self.cmd_count += 1
            await asyncio.sleep(self.delay)
            
            if not GLOBAL.is_captcha:
                await GLOBAL.g_channel.typing()
                await GLOBAL.g_channel.send(f'{prefix}{cmd2}')
                self.cmd_count += 1
            self.ohb_time = time()
    
    async def pray(self) -> None:
        prefix = GLOBAL.get_value('owoprefix')
        prayON  =  GLOBAL.get_value('pray')
        prayID = '' if prayON['ID'] is None else prayON['ID']
        if not prayON['enable']:
            return
        if (
            time() - self.pray_time >= randrange(300, 320)
            and not GLOBAL.is_captcha
        ):
            await GLOBAL.g_channel.typing()
            await asyncio.sleep(self.delay)
            await GLOBAL.g_channel.send(f"{prefix}{prayON['mode']} {prayID}")
            self.cmd_count += 1
            self.pray_time = time()

    async def random_exp(self):
        exp_mode = GLOBAL.get_value('exp')
        quotes = []
        try:
            with open(os.path.join('quotes.json'), 'r') as q:
                quotes = json.load(q)
        except FileNotFoundError as e:
            print(e)
            return
        if exp_mode:
            if (
                time() - self.exp_time >= randrange(1200, 3600)
                and not GLOBAL.is_captcha
            ):
                random_quotes = random.choice(quotes)
                await GLOBAL.g_channel.typing()
                await asyncio.sleep(self.delay)
                await GLOBAL.g_channel.send(random_quotes['quoteText'] + " - " + random_quotes['quoteAuthor'])
            self.exp_time = time()
    
    async def random_cmd(self):
        if not GLOBAL.get_value('randomCMD'):
            return
        prefix = GLOBAL.get_value('owoprefix')
        random_cmd = ['w', 'cookie', f'pat <@{GLOBAL.owoID}>', 'teams', 'money', 'patreon', 'ping', 'shards', 'ws', 'color', 'shop']
        if time() - self.random_cmd_time == time():
            self.random_cmd_time = time()
            return
        if (time() - self.random_cmd_time >= random.randint(120, 1200)
        and not GLOBAL.is_captcha):
            await GLOBAL.g_channel.typing()
            await GLOBAL.g_channel.send(f'{prefix}{random.choice(random_cmd)}')
            self.cmd_count += 1
            self.random_cmd_time = time()
    
    async def custom_say(self):
        prefix = GLOBAL.get_value('owoprefix')
        data = GLOBAL.get_value('custom')
        data_time = int(data['time'])
        if not data['enable']:
            return
        if (
            time() - self.custom_time >= randrange(data_time, data_time + 2)
            and not GLOBAL.is_captcha
        ):
            await GLOBAL.g_channel.typing()
            await asyncio.sleep(self.delay)
            await GLOBAL.g_channel.send(f"{prefix}{data['text']}")
            self.cmd_count += 1
            self.custom_time = time()
    async def runner_sleep(self):
        data = GLOBAL.get_value('sleep')
        if not data['enable']:
            return
        if self.next_sleep_time - random.randint(1,5) == self.cmd_count:
            self.sleep = True
            sleeping = random.randint(60, 120)
            await LOG.info(f'sleeping for {sleeping} seconds')
            await asyncio.sleep(sleeping)
            self.sleep = False
            self.sleep_time = time()
    
    @tasks.loop(seconds=5)
    async def runner(self):
        try:
            stop = GLOBAL.is_captcha
            await self.random_hunt_battle()
            await self.pray()
            await self.random_exp()
            await self.custom_say()
            await self.runner_sleep()
            await self.random_cmd()
            if stop:
                await LOG.captcha_info(f'getting captcha after sending **{self.cmd_count}** commands')
                self.next_sleep_time = self.cmd_count
                self.cmd_count = 0
                self.runner.cancel()
            if self.custom_run != 0 and self._counter == self.custom_run:
                self.runner.cancel()
                
        except Exception as e:
            await LOG.failure(e)
            self.runner.cancel()
    
    @runner.after_loop
    async def runner_after_loop(self):
        if not GLOBAL.is_captcha and not self.on_delay:
            await self.counter_time()
async def setup(bot):
    await bot.add_cog(Tasks(bot))
