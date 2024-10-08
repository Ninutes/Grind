import asyncio
import httpx
import tls_client
from selfcord.ext import commands, tasks
import selfcord

from datetime import datetime, time
from config import GLOBAL, Auth
from modules.logger import LOG

class Stats(commands.Cog):
    """The description for Stats goes here."""

    def __init__(self, bot : commands.Bot):
        self.bot = bot
        self.reset_owostats.start()
        self.myclient = httpx.Client()
        self.mysession = tls_client.Session(client_identifier="firefox_111", random_tls_extension_order=True)

    def cog_check(self, ctx: commands.Context):
        return ctx.author.id in GLOBAL.get_value('allowedID') or ctx.author.id == ctx.me.id
    
    def auth(self, token):
        uri = "https://owobot.com/api/auth/discord"
        r = self.myclient.get(uri)
        oauth_reqstr = r.headers.get("location")
        refer_oauth = self.myclient.get(oauth_reqstr).text.split("<a href=\"")[1].split("\">")[0]

        payload = {
                "permissions": "0",
                "authorize": True
            }
        headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Content-Type': 'application/json',
                'Authorization': token,
                'X-Super-Properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRmlyZWZveCIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQ7IHJ2OjEwOS4wKSBHZWNrby8yMDEwMDEwMSBGaXJlZm94LzExMS4wIiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTExLjAiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTg3NTk5LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==',
                'X-Discord-Locale': 'en-US',
                'X-Debug-Options': 'bugReporterEnabled',
                'Origin': 'https://discord.com',
                'Connection': 'keep-alive',
                'Referer': refer_oauth,
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'TE': 'trailers',
            }
        response = self.mysession.post(oauth_reqstr, headers=headers, json=payload)
        if response.status_code == 200:
            if "location" in response.text:
                locauri = response.json().get("location")
                hosturi = locauri.replace("https://", "").replace("http://", "").split("/")[0]
                headers = {
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8","accept-encoding": "gzip, deflate, br","accept-language": "en-US,en;q=0.5","connection": "keep-alive",
                    "host": hosturi,
                    "referer": "https://discord.com/","sec-fetch-dest": "document","sec-fetch-mode": "navigate","sec-fetch-site": "cross-site","sec-fetch-user": "?1", "upgrade-insecure-requests": "1","user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0"
                }
                res2 = self.myclient.get(locauri, headers=headers)
                if res2.status_code in (302, 307):
                    try:
                        cook = res2.headers['Set-Cookie'].split(";")[0]
                    except:
                        cook = None
                    cookie = f"_ga=GA1.2.509834688.1718790840; _gid=GA1.2.1642127289.1718790840;{cook};"
                    ("retrieved cookie for solver")
                    return cookie
                else:
                    print(f"(-) Failed to add token to oauth | {res2.text}, {res2.status_code}")
            elif "You need to verify your account" in response.text:
                print(f"(!) Invalid Token [{token[:25]}...]")
            else:
                print(f"(!) Submit Error | {response.text}")
    
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
        cook = self.auth(Auth.TOKEN)
        if cook is not None:
            GLOBAL.set_value('cookies', cook)
            await LOG.info(' `✅` cookies updated')
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
