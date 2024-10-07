import asyncio
from base64 import b64encode
from datetime import datetime, timedelta
import re
from time import time

import concurrent.futures
import aiohttp
import selfcord
from selfcord.ext import commands
from twocaptcha import TwoCaptcha
from config import GLOBAL, Auth
from modules.logger import LOG


class Captcha(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.apikey = Auth.APIKEY
        self.owoDM = None
        self.captcha_image = None
        self.captcha_length = None
        self.regex_box = r'10 minutes:\s(.*)$'
        self.regex_ban = r'You have been banned for \*\*(\d+)H\*\*'
    
    def cog_check(self, ctx: commands.Context):
        return ctx.author.id in GLOBAL.get_value('allowedID') or ctx.author.id == ctx.me.id
    async def detect_captcha(self, m: selfcord.Message, key: str = None):
        user = self.bot.get_user(GLOBAL.get_value('user.ID'))
        dm_channel = False
        if m.channel.type == selfcord.ChannelType.private:
            dm_channel = True
        name = [user.name, user.display_name, user.mention, user.global_name, user.id]
        if not dm_channel:
            if any(n in m.content for n in name) and key in m.content:
                return True
            return False
        else:
            if key in m.content and not 'verified' in m.content:
                return True
            elif '3/3' in m.content:
                await LOG.captcha(m, 'last chance')
                return False
        return False
    
    async def get_captcha(self, message: selfcord.Message):
        await asyncio.sleep(10)
        user = self.bot.get_user(GLOBAL.get_value('user.ID'))
        async for msg in message.channel.history(limit=10):
            name = [user.name, user.display_name, user.mention, user.global_name, user.id]
            if 'link' in msg.content and any(n in msg.content for n in name):
                return await self.solver_link(message)
            if msg.attachments and 'captcha' in msg.content and any(n in msg.content for n in name):
                self.captcha_image = b64encode(await msg.attachments[0].read()).decode("utf-8")
                self.captcha_length = msg.content[msg.content.find("letter word") - 2]
                if GLOBAL.get_value('autosolve'):
                    return await self.get_result(msg, self.captcha_image, self.captcha_length)
                return await LOG.captcha(msg, 'detected')
            if 'captcha' in msg.content and any(string in msg.content for string in ['1/5', '2/5', '3/5']) and any(n in msg.content for n in name):
                await LOG.captcha(msg, 'detected')
    
    async def get_result(self, message : selfcord.Message, image, length):
        solve_time = time()
        while True:
            result = await self.solver(image, length)
            if result:
                if not result['code'].isalpha():
                    await LOG.captcha_failed(f"{result['code']} has an integer")
                    await self.report(result['captchaId'], False)
                    await asyncio.sleep(5)
                elif len(result['code']) != int(length):
                    await LOG.captcha_failed(f"{result['code']} has different length")
                    await self.report(result['captchaId'], False)
                    await asyncio.sleep(5)
                else:
                    return await self.send_result(message, result)
            if time() - solve_time > 180:
                await LOG.captcha_failed(f'180\'s have been left, probably captcha unsolvable')
                await LOG.captcha(message, 'not solved')
                break
            

    async def send_result(self, message, result):
        if len(result['code']) > 8:
            cookie = GLOBAL.get_value('cookies')
            try:
                async with aiohttp.ClientSession(headers={"Connection": "keep-alive"}) as session:
                    async with session.post("https://owobot.com/api/captcha/verify", json={"token": result['code']}, headers={"Cookie": cookie}) as response:
                        if response.status == 200:
                            await LOG.captcha_info('Try solve captcha link...')
                        else:
                            await LOG.captcha_failed(f'Error: {response.status}')
                            return await LOG.captcha(message, 'detected')
            except Exception as e:
                await LOG.failure(e)
                return await LOG.captcha(message, 'detected')
                        
        else:
            await self.owoDM.send(result['code'].lower())
        await asyncio.sleep(5)
        async for msg in self.owoDM.history(limit=1):
            if 'verified' in msg.content:
                GLOBAL.is_captcha = False
                dmcontent = re.search(self.regex_box, msg.content)
                if dmcontent:
                    box = dmcontent.group(1)
                    await LOG.captcha(message, 'solved', box)
                else:
                    await LOG.captcha(message,'solved')
                await self.report(result['captchaId'])
                await asyncio.sleep(10)
                runner = self.bot.get_cog('Tasks')
                if runner:
                    runner.start_task()
                return 
            elif 'Wrong' in msg.content:
                await LOG.captcha(message, 'not solved')
                await LOG.captcha_failed(msg.content)
                await self.report(result['captchaId'], False)
                GLOBAL.is_captcha = True
                if not '2/3' in msg.content:
                    await asyncio.sleep(10)
                    return await self.get_result(message, self.captcha_image, self.captcha_length)
                elif '2/3' in msg.content:
                    return await LOG.captcha_failed(f'Auto solve failed, after 2 attempts.')
            elif 'banned' in msg.content:
                ban = re.search(self.regex_ban, msg.content)
                ban_time = int(ban.group(1))
                ban_time = datetime.now() + timedelta(hours=ban_time) + timedelta(hours=7)
                ban_time = ban_time.strftime("%d %B %Y %H:%M")
                GLOBAL.is_captcha = True
                return await LOG.captcha_failed(f'You have been banned until **{ban_time}**')
            return await LOG.info(f'OwO didn\'t response')

    async def solver(self, image, length):
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            try:
                result = await loop.run_in_executor(
                    pool, lambda: TwoCaptcha(Auth.APIKEY).normal(
                        image,
                        numeric=2,
                        minLen=length,
                        maxLen=length,
                        phrase=0,
                        caseSensitive=0,
                        calc=0,
                        lang='en',
                        hintText=f'Please answer with only the following {length} letter word, NO NUMBER,',
                        )
                    )
                return result
            except Exception as e:
                await LOG.info(e)
                return None
    async def solver_link(self, message: selfcord.Message):
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            try:
                result = await loop.run_in_executor(
                    pool, lambda: TwoCaptcha(Auth.APIKEY, defaultTimeout=300).hcaptcha(sitekey="a6a1d5ce-612d-472d-8e37-7601408fbc09", url="https://owobot.com/captcha")
                )
                if result:
                    return await self.send_result(message, result)
                else:
                    return await LOG.captcha(message, 'detected')
            except Exception as e:
                await LOG.info(e)
                return await LOG.captcha(message, 'detected')
    async def report(self, ID, result: bool = True):
        loop = asyncio.get_running_loop()
        try:
            with concurrent.futures.ThreadPoolExecutor() as pool:
                captcha = await loop.run_in_executor(pool, lambda: TwoCaptcha(Auth.APIKEY))
                return captcha.report(ID, result)
        except Exception as e:
            return await LOG.info(e)
    async def balance(self):
        loop = asyncio.get_running_loop()
        try:
            with concurrent.futures.ThreadPoolExecutor() as pool:
                captcha = await loop.run_in_executor(pool, lambda: TwoCaptcha(Auth.APIKEY))
                return round(captcha.balance(), 1)
        except Exception as e:
            return await LOG.info(e)
    
    async def _delete_msg(self, ctx: commands.Context):
        try:
            await ctx.message.delete()
        except Exception:
            return  
    @commands.command()
    async def captcha_tes(self, ctx: commands.Context):
        if ctx.message.attachments:
            image = b64encode(await ctx.message.attachments[0].read()).decode("utf-8")
            length = ctx.message.content[ctx.message.content.find("letter word") - 2]
            result = await self.solver(image, length)
            await ctx.send(f'```{result}```')
    @commands.command()
    async def dms(self, ctx: commands.Context, text: str):
        await self._delete_msg(ctx)
        captcha_msg = None
        await self.owoDM.send(text.lower())
        await asyncio.sleep(5)
        async for message in GLOBAL.g_channel.history(limit=10):
            if 'captcha' in message.content.lower() and message.attachments:
                captcha_msg = message
        async for msg in self.owoDM.history(limit=1):
            if 'verified' in msg.content.lower():
                dmcontent = re.search(self.regex_box, msg.content)
                if dmcontent:
                    box = dmcontent.group(1)
                    await LOG.captcha(captcha_msg, 'solved', box)
                else:
                    await LOG.captcha(captcha_msg,'solved')
                GLOBAL.is_captcha = False
                await asyncio.sleep(10)
                runner = self.bot.get_cog('Tasks')
                if runner:
                    runner.start_task()
                return 
            elif 'wrong' in msg.content.lower():
                await LOG.captcha(captcha_msg, 'not solved')
                await LOG.captcha_failed(msg.content)
                GLOBAL.is_captcha = True
                return
            elif 'banned' in msg.content:
                ban = re.search(self.regex_ban, msg.content)
                ban_time = int(ban.group(1))
                ban_time = datetime.now() + timedelta(hours=ban_time)
                ban_time = ban_time.strftime("%d %B %Y %H:%M")
                GLOBAL.is_captcha = True
                return await LOG.captcha_failed(f'You have been banned until {ban_time}')
            return await LOG.info(f'OwO didn\'t response')
    @commands.command(aliases=['ccount'])
    async def captcha_count(self, ctx: commands.Context, amount: int, limit: int):
        await self._delete_msg(ctx)
        self.owoDM = self.bot.get_user(GLOBAL.owoID).dm_channel
        total = 0
        if amount >= 1:
            async for message in self.owoDM.history(limit=limit):
                if message.content.count('cross_box') == amount and 'captcha' in message.content:
                    total += 1
                if message.content.count('cross_box') != amount and 'captcha' in message.content:
                    break
        else:
            async for message in self.owoDM.history(limit=limit):
                if message.content.count('blank_box') == 3 and 'captcha' in message.content:
                    total += 1
                if message.content.count('blank_box') != 3 and 'captcha' in message.content:
                    break
        await LOG.info(f'total {amount} cross_box :{total}')
    
    @commands.command()
    async def s_link(self, ctx: commands.Context):
        await self._delete_msg(ctx)
        self.owoDM = self.bot.get_user(GLOBAL.owoID).dm_channel
        await self.solver_link(ctx.message)
        # web = "https://owobot.com/captcha"
        # solver = TwoCaptcha(apiKey=Auth.APIKEY)
        # try:
        #     hasil = solver.hcaptcha(sitekey="a6a1d5ce-612d-472d-8e37-7601408fbc09", url=web)
        #     if hasil:
        #         await LOG.info(f'```js\n{hasil}```')
        # except Exception as e:
        #     await LOG.info(e)
            
    
    @commands.command()
    async def cek_ban(self, ctx: commands.Context):
        await self._delete_msg(ctx)
        self.owoDM = self.bot.get_user(GLOBAL.owoID).dm_channel
        async for message in self.owoDM.history():
            if 'banned' in message.content.lower():
                ban = re.search(self.regex_ban, message.content)
                ban_time = int(ban.group(1))
                ban_time = message.created_at + timedelta(hours=ban_time)
                ban_time = ban_time.strftime("%d %B %Y %H:%M")
                return await LOG.captcha_failed(f'You have been banned until {ban_time}')
    @commands.Cog.listener()
    async def on_message(self, message : selfcord.Message):
        if not message.channel.id == GLOBAL.get_value('channelID'):return
        if GLOBAL.is_captcha:return
        if message.author.id == GLOBAL.owoID and 'captcha' in message.content:
            self.owoDM = self.bot.get_user(GLOBAL.owoID).dm_channel
            detect = await self.detect_captcha(message, '⚠️')
            if detect:
                GLOBAL.is_captcha = True
                return await self.get_captcha(message)
async def setup(bot):
    await bot.add_cog(Captcha(bot))