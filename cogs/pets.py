import re
from selfcord.ext import commands, tasks
import selfcord

from config import GLOBAL
from modules.logger import LOG

FABLED = [
    "dboar", 
    "deagle", 
    "dfrog", 
    "dgorilla", 
    "dwolf"
    ]
HIDDEN = [
    "hkoala", 
    "hlizard", 
    "hsnake", 
    "hsquid", 
    "hmonkey"
    ]
BOTRANK = [
    "dinobot",
    "giraffbot",
    "hedgebot",
    "lobbot",
    "slothbot",
]
DISTORTED = [
    "glitchparrot",
    "glitchotter",
    "glitchraccoon",
    "glitchflamingo",
    "glitchzebra",
]

class Pets(commands.Cog):
    """The description for Pets goes here."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.regex_found = r'You found:(.*?)\s*\<:blank:'
        self.regex_caught = r'caught.*(\S+)!'
        self.regex_win = r'Streak: ([1-9]+[0-9]*000$)'
        self.regex_lost = r'You lost your streak of (\d+) wins'
    
    async def detect_pets(self, message: selfcord.Message):
        ctx = await self.bot.get_context(message)
        pets = []
        if not ctx.me.display_name in message.content and '**🌱' in message.content:
            return
        if 'empowered' in message.content:
            pets = re.search(self.regex_found, message.content)
        elif 'caught' in message.content:
            pets = re.search(self.regex_caught, message.content)
        if pets:
            pets = pets.groups(1)
            if any(pet.strip() in HIDDEN for pet in pets[0].split()):
                return LOG.pets(message)
            if any(pet.strip() in FABLED for pet in pets[0].split()):
                return LOG.pets(message)
            if any(pet.strip() in DISTORTED for pet in pets[0].split()):
                return LOG.pets(message)
    @commands.Cog.listener()
    async def on_message(self, message: selfcord.Message):
        if not message.channel.id == GLOBAL.get_value('channelID'):
            return
        if not message.author.id == GLOBAL.owoID:
            return
        await self.detect_pets(message)
        if message.embeds:
            ctx = await self.bot.get_context(message)
            msg = message.embeds[0]
            author = msg.author.name if msg.author.name is not None else None
            footer = msg.footer.text if msg.footer.text else None
            if author and footer:
                if ctx.me.display_name in author:
                    match_win = re.search(self.regex_win, footer)
                    match_lost = re.search(self.regex_lost, footer)
                    if match_win:
                        return LOG.battle(message, 'win', int(match_win.group(1)) )
                    elif match_lost:
                        return LOG.battle(message, 'lost', int(match_lost.group(1)) )

async def setup(bot):
    await bot.add_cog(Pets(bot))