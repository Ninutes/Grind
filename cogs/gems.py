import asyncio
from re import findall
from selfcord.ext import commands
import selfcord

from config import GLOBAL
from modules.logger import LOG

class Gems(commands.Cog):
    """The description for Gems goes here."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.regex = r"gem(\d):\d+>`\[(\d+)"
        self.checking_gems = False
        self.available = [1, 3, 4]
        self.gemtypes = [1, 3, 4]
    
    def is_myhunt(self, message):
        return GLOBAL.get_value('gem') and message.channel == GLOBAL.g_channel and message.author.id == GLOBAL.owoID and '**🌱' in message.content
    
    async def _delete_msg(self, ctx: commands.Context):
        try:
            await ctx.message.delete()
        except Exception:
            return
    @commands.command(name='gem')
    async def set_gem(self, ctx: commands.Context):
        await self._delete_msg(ctx)
        if GLOBAL.get_value('gem'):
            GLOBAL.set_value('gem', False)
        else:
            GLOBAL.set_value('gem', True)
        LOG.success(f'**GEMS MODE** set to: %s' % GLOBAL.get_value('gem'))
    @commands.Cog.listener()
    async def on_message(self, message: selfcord.Message):
        if self.is_myhunt(message):
            await self.detect_gems(message)
    
    async def detect_gems(self, message : selfcord.Message):
        if not self.bot.user.display_name in message.content:
            return
        current_gems = [gem for gem in findall(self.regex, message.content) if not gem[1] == '0']
        use = [1,3,4]
        if len(current_gems) == 3:
            self.checking_gems = False
            return

        for gem in current_gems:
            use.remove(int(gem[0]))
        use  = [gem for gem in use if gem in self.available]
        if not GLOBAL.is_captcha and use:
            await self.use_gems(use)

    async def use_gems(self, target = [1,3,4]):
        for index, value in  enumerate(target):
            match value:
                case 1:
                    target[index] = 0
                case 3:
                    target[index] = 1
                case 4:
                    target[index] = 2
        if GLOBAL.is_captcha:
            return
        await GLOBAL.g_channel.typing()
        self.checking_gems = True
        runner = self.bot.get_cog('Tasks')
        if runner:
            await runner.delay_task()
        await GLOBAL.g_channel.send('winv')
        await asyncio.sleep(5)
        async for msg in GLOBAL.g_channel.history(limit=5):
            inv = []
            if msg.author.id == GLOBAL.owoID and self.bot.user.display_name in msg.content and 'Inventory' in msg.content:
                inv = findall(r"`(.*?)`", msg.content)
                break
        if inv == []:
            self.checking_gems = False
            return
        
        if not GLOBAL.is_captcha and ('050') in inv:
            await GLOBAL.g_channel.send('wlb all')
            await asyncio.sleep(5)
            self.available = [1,3,4]
            await self.use_gems(target)
        
        inv = [
            item
            for item in inv
            if item.isdigit() and int(item) < 100 and int(item) > 50
        ]
        
        types = [[], [], []]
        for gem in inv:
            gem = int(gem)
            if 50 < gem < 58:
                types[0].append(gem)
            elif 64 < gem < 72:
                types[1].append(gem)
            elif 71 < gem < 79:
                types[2].append(gem)
                
        self.available =  []
        if types[0]:
            self.available.append(1)
        if types[1]:
            self.available.append(3)
        if types[2]:
            self.available.append(4)
        use = []
        for level in target:
            if types[level]:
                use.append(str(min(types[level])))
        if not GLOBAL.is_captcha and use:
            await GLOBAL.g_channel.send(f'wuse {" ".join(use)}')
            await asyncio.sleep(5)
            self.checking_gems = False
            return
    
    
async def setup(bot):
    await bot.add_cog(Gems(bot))
