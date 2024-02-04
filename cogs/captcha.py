import asyncio
from base64 import b64encode
from datetime import datetime, timedelta
import re
from time import time

import selfcord
from selfcord.ext import commands
from twocaptcha import TwoCaptcha
from config import GLOBAL, Auth, is_me
from modules.logger import LOG


class Captcha(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.apikey = Auth.APIKEY
        self.owoDM = None
        self.captcha_image = None
        self.captcha_length = None
        self.regex_box = r':blank:427371936482328596>\s*\*\*\|\*\*\s*(.*)$'
        self.regex_ban = r'You have been banned for (\d+)H'
    
    def cog_check(self, ctx: commands.Context):
        return ctx.author.id in GLOBAL.get_value('allowedID')
    async def detect_captcha(self, m: selfcord.Message, key: str = None):
        user = self.bot.get_user(GLOBAL.get_value('userID'))
        dm_channel = False
        if m.channel.type == selfcord.ChannelType.private:
            dm_channel = True
        name = [user.name, user.display_name, user.mention, user.global_name, user.id]
        for n in name:
            if not dm_channel:
                if n in m.content and key in m.content:
                    return True
                return False
            else:
                if key in m.content and not 'verified' in m.content:
                    return True
                elif '3/3' in m.content:
                    LOG.captcha(m, 'last chance')
                    return False
            return False
    
    async def get_captcha(self, message: selfcord.Message):
        await asyncio.sleep(5)
        async for msg in message.channel.history(limit=10):
            if 'link' in msg.content:
                return LOG.captcha(msg, 'link')
            if 'captcha' in msg.content and msg.attachments:
                self.captcha_image = b64encode(await msg.attachments[0].read()).decode("utf-8")
                self.captcha_length = msg.content[msg.content.find("letter word") - 2]
                if GLOBAL.get_value('autosolve'):
                    return await self.get_result(msg, self.captcha_image, self.captcha_length)
                return LOG.captcha(msg, 'detected')
            return LOG.captcha(msg, 'detected')
    
    async def get_result(self, message : selfcord.Message, image, length):
        solve_time = time()
        while True:
            result = await self.solver(image, length)
            if result:
                if isinstance(result['code'], int):
                    LOG.info(f"{result['code']} has integer")
                    self.report(result['captchaId'], False)
                    await asyncio.sleep(5)
                elif len(result['code']) != int(length):
                    LOG.info(f"{result['code']} has different length")
                    self.report(result['captchaId'], False)
                    await asyncio.sleep(5)
                else:
                    return await self.send_result(message, result)
            if time() - solve_time > 180:
                LOG.failure(f'180\'s have been left, probably captcha unsolvable')
                LOG.captcha(message, 'not solved')
                break
            

    async def send_result(self, message, result):
        await self.owoDM.send(result['code'].lower())
        await asyncio.sleep(5)
        async for msg in self.owoDM.history(limit=1):
            if 'verified' in msg.content:
                GLOBAL.is_captcha = False
                LOG.captcha(message, 'solved')
                dmcontent = re.search(self.regex_box, msg.content)
                if dmcontent:
                    box = dmcontent.group(1)
                    LOG.success(box)
                self.report(result['captchaId'])
                await asyncio.sleep(10)
                runner = self.bot.get_cog('Tasks')
                if runner:
                    runner.start_task()
            elif 'Wrong' in msg.content:
                LOG.captcha(message, 'not solved')
                LOG.failure(msg.content)
                self.report(result['captchaId'], False)
                GLOBAL.is_captcha = True
                if not '2/3' in msg.content:
                    await asyncio.sleep(10)
                    return await self.get_result(message, self.captcha_image, self.captcha_length)
            elif 'banned' in msg.content:
                ban = re.search(self.regex_ban, msg.content)
                ban_time = int(ban.group(1))
                ban_time = datetime.now() + timedelta(hours=ban_time)
                ban_time = ban_time.strftime("%d %B %Y %H:%M")
                LOG.failure(f'You have been banned until {ban_time}')
                GLOBAL.is_captcha = True

    async def solver(self, image, length):
        try:
            captcha = TwoCaptcha(self.apikey, defaultTimeout=180)
            response = captcha.normal(
                image, 
                numeric=2,
                minLen=length,
                maxLen=length,
                phrase=0,
                caseSensitive=0,
                calc=0,
                lang='en',
                hintText=f'Please answer with only the following {length} letter word, NO NUMBER,',)
            await asyncio.sleep(10)
            return response
        except Exception as e:
            LOG.info(e)
            return None
    def report(self, ID, result: bool = True):
        try:
            captcha = TwoCaptcha(self.apikey)
            return captcha.report(ID, result)
        except Exception as e:
            return LOG.info(e)
    def balance(self):
        try:
            captcha = TwoCaptcha(self.apikey)
            return round(captcha.balance(), 1)
        except Exception as e:
            return LOG.info(e)
    
    @commands.command()
    async def captcha_tes(self, ctx: commands.Context):
        if ctx.message.attachments:
            image = b64encode(await ctx.message.attachments[0].read()).decode("utf-8")
            length = ctx.message.content[ctx.message.content.find("letter word") - 2]
            result = await self.solver(image, length)
            await ctx.send(f'```{result}```')
    @commands.command()
    async def dms(self, ctx: commands.Context, text: str):
        await ctx.message.delete()
        captcha_msg = None
        await self.owoDM.send(text.lower())
        await asyncio.sleep(5)
        async for msg in self.owoDM.history(limit=1):
            async for message in GLOBAL.g_channel.history(limit=10):
                if 'captcha' in message.content.lower() and message.attachments:
                    captcha_msg = message
            if 'verified' in msg.content.lower():
                LOG.captcha(captcha_msg, 'solved')
                dmcontent = re.search(self.regex_box, msg.content)
                if dmcontent:
                    box = dmcontent.group(1)
                    LOG.success(box)
                GLOBAL.is_captcha = False
                await asyncio.sleep(10)
                runner = self.bot.get_cog('Tasks')
                if runner:
                    return runner.start_task()
            elif 'wrong' in msg.content.lower():
                LOG.captcha(captcha_msg, 'not solved')
                LOG.failure(msg.content)
                GLOBAL.is_captcha = True
                return
            elif 'banned' in msg.content:
                ban = re.search(self.regex_ban, msg.content)
                ban_time = int(ban.group(1))
                ban_time = datetime.now() + timedelta(hours=ban_time)
                ban_time = ban_time.strftime("%d %B %Y %H:%M")
                LOG.failure(f'You have been banned until {ban_time}')
                GLOBAL.is_captcha = True
    @commands.Cog.listener()
    async def on_message(self, message : selfcord.Message):
        if not message.channel.id == GLOBAL.get_value('channelID'):return
        if message.author.id == GLOBAL.owoID and 'captcha' in message.content:
            self.owoDM = self.bot.get_user(GLOBAL.owoID).dm_channel
            detect = await self.detect_captcha(message, '⚠️')
            if detect:
                GLOBAL.is_captcha = True
                return await self.get_captcha(message)
async def setup(bot):
    await bot.add_cog(Captcha(bot))