# This example covers advanced startup options and uses some real world examples for why you may need them.

import asyncio
import logging
import logging.handlers
import os
from dotenv import find_dotenv, load_dotenv
import selfcord


from selfcord.ext import commands
from pycolorise.colors import *
from config import GLOBAL, Auth
from modules.logger import WB
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

    async def setup_hook(self) -> None:
        cog_dir = "./cogs"
        print(Green("Loading extensions..."))
        await asyncio.sleep(1)
        for foldername, _, filenames in os.walk(cog_dir):
            for filename in filenames:
                if filename.endswith(".py"):
                    cog_path = os.path.join(foldername, filename)
                    cog_name = os.path.relpath(cog_path, cog_dir)[:-3].replace(os.path.sep, ".")
                    try:
                        await self.load_extension(f"cogs.{cog_name}")
                        print(Blue(f"✅ {filename[:-3]}"))
                        self.loaded_cogs.append(f"`✅` {filename[:-3]}")
                    except commands.ExtensionError as e:
                        print(f"❌ Failed to load {filename[:-3]}  : {e}")
    
    async def on_ready(self):
        GLOBAL.set_value('userID', self.user.id)
        userID = self.user.id
        allowedID = GLOBAL.get_value('allowedID')
        if userID not in allowedID:
            allowedID.append(userID)
            GLOBAL.set_value('allowedID', allowedID)
        GLOBAL.set_value('username', self.user.display_name)
        GLOBAL.set_value('avatarURL', self.user.display_avatar.url)
        print(BrightBlue(f"{self.user.name} is online!"))
        await self.log_on_ready()
    
    
    async def log_on_ready(self):
        cogs = '\n'.join(self.loaded_cogs)
        embed = selfcord.Embed(
            description=f'\n**COGS:**\n{cogs}',
            color=selfcord.Color.magenta()
        )
        WB.send(
            username=self.user.display_name,
            avatar_url=self.user.display_avatar.url,
            embed=embed,  
        )

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
            await bot.start(os.getenv('TOKEN'))
    finally:
        await bot.close()
        asyncio.get_event_loop().stop()

# For most use cases, after defining what needs to run, we can just tell asyncio to run it:
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print(Green("Detected Ctrl + C, Exiting..."))
except RuntimeError:
    print(Red("Exiting..."))