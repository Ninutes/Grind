# This example covers advanced startup options and uses some real world examples for why you may need them.

import asyncio
from datetime import datetime
import logging
import logging.handlers
import os
from dotenv import find_dotenv, load_dotenv
import httpx
import tls_client
import selfcord


from selfcord.ext import commands
from pycolorise.colors import *
from config import GLOBAL, Auth
from modules.logger import _webhook
from modules.help import MyHelp

load_dotenv(find_dotenv(raise_error_if_not_found=True))

class Grind(commands.Bot):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.loaded_cogs = []
        self.myclient = httpx.Client()
        self.mysession = tls_client.Session(client_identifier="firefox_111", random_tls_extension_order=True)

    async def setup_hook(self) -> None:
        cog_dir = "./cogs"
        # print(Green("Loading extensions..."))
        # await asyncio.sleep(1)
        for foldername, _, filenames in os.walk(cog_dir):
            for filename in filenames:
                if filename.endswith(".py"):
                    cog_path = os.path.join(foldername, filename)
                    cog_name = os.path.relpath(cog_path, cog_dir)[:-3].replace(os.path.sep, ".")
                    try:
                        await self.load_extension(f"cogs.{cog_name}")
                        # print(Blue(f"✅ {filename[:-3]}"))
                        self.loaded_cogs.append(f"`✅` {filename[:-3]}")
                    except commands.ExtensionError as e:
                        self.loaded_cogs.append(f"`❌` {filename[:-3]}")
                        print(f"❌ Failed to load {filename[:-3]}  : {e}")

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

    async def on_ready(self):
        GLOBAL.set_value('user.ID', self.user.id)
        # userID = self.user.id
        # allowedID = GLOBAL.get_value('allowedID')
        # if userID not in allowedID:
        #     allowedID.append(userID)
        #     GLOBAL.set_value('allowedID', allowedID)
        GLOBAL.set_value('user.username', self.user.display_name)
        GLOBAL.set_value('user.avatarURL', self.user.display_avatar.url)
        print(f"\033[1m[ \033[0m{BrightYellow(self.user.name)}\033[1m ]\033[0m is \033[1m{BrightBlue('Online')}\033[0m ")
        cook = self.auth(Auth.TOKEN)
        if cook is not None:
            GLOBAL.set_value('cookies', cook)
        await self.log_on_ready()
    
    async def on_message(self, message: selfcord.Message) -> None:
        if message.author.id in GLOBAL.get_value('allowedID') or message.author.id == GLOBAL.owoID or message.author.id == GLOBAL.reactionID or message.author.id == self.user.id:
            await self.process_commands(message)
    
    async def log_on_ready(self):
        cogs = '\n'.join(self.loaded_cogs)
        servers = len(self.guilds)
        embed = selfcord.Embed(
            color=selfcord.Color.light_gray(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/1230304058405814332.gif')
        embed.add_field(name='Self-Bot', value=f'connected to **{servers} guilds**', inline=False)
        embed.add_field(name='Loaded Cogs', value=cogs)
        embed.set_footer(text=f"my prefix : {GLOBAL.get_value('prefix')}")
        await _webhook(
            embed=embed,  
        )

looper = asyncio.get_event_loop()

async def main():

    logger = logging.getLogger('selfcord')
    logger.setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(
        filename='selfcord.log',
        encoding='utf-8',
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,  # Rotate through 5 files
    )
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    try:
        async with Grind(
            command_prefix=Auth.PREFIXES,
            help_command = MyHelp(),
            self_bot = False,
            user_bot = True
            ) as bot:
            await bot.start(Auth.TOKEN)
    finally:
        await bot.close()

# For most use cases, after defining what needs to run, we can just tell asyncio to run it:
try:
    asyncio.run(main())
except (KeyboardInterrupt, asyncio.exceptions.CancelledError) as e:
    print(Green(f"{e}\nDetected Ctrl + C, Exiting..."))
except RuntimeError:
    print(Red("Exiting..."))