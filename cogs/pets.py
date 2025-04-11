import re
from selfcord.ext import commands
import selfcord

from config import GLOBAL
from modules.logger import LOG

FABLED = ["dboar", "deagle", "dfrog", "dgorilla", "dwolf"]
HIDDEN = ["hkoala", "hlizard", "hsnake", "hsquid", "hmonkey"]
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
        self.regex_found = r"You found:(.*?)\s*\<:blank:"
        self.regex_caught = r"caught.*(\S+)!"
        self.regex_win = r"Streak: ([1-9]+[0-9]*000$)"
        self.regex_lost = r"You lost your streak of (\d+) wins"

    async def detect_pets(self, message: selfcord.Message):
        ctx = await self.bot.get_context(message)
        pets = []
        if ctx.me.display_name not in message.content and "**🌱" in message.content:
            return
        if "empowered" in message.content:
            for key in [
                "OwO.daily.hunt",
                "OwO.weekly.hunt",
                "OwO.monthly.hunt",
                "OwO.total.hunt",
            ]:
                GLOBAL.set_owostats(key)
            pets = re.search(self.regex_found, message.content)
        elif "caught" in message.content:
            for key in [
                "OwO.daily.hunt",
                "OwO.weekly.hunt",
                "OwO.monthly.hunt",
                "OwO.total.hunt",
            ]:
                GLOBAL.set_owostats(key)
            pets = re.search(self.regex_caught, message.content)
        if pets:
            pets = pets.groups(1)
            if any(pet.strip() in HIDDEN for pet in pets[0].split()):
                return await LOG.pets(message)
            if any(pet.strip() in FABLED for pet in pets[0].split()):
                return await LOG.pets(message)
            if any(pet.strip() in DISTORTED for pet in pets[0].split()):
                return await LOG.pets(message)

    def get_userid(self, url: str) -> int | None:
        """
        Ekstrak user ID dari URL avatar, jika menggunakan custom avatar.
        """
        if "embed/avatars/" in url:
            return 123  # default avatar, tidak ada ID
        match = re.search(r"avatars/(\d+)/", url)
        return int(match.group(1)) if match else None

    @commands.Cog.listener()
    async def on_message(self, message: selfcord.Message):
        if message.author.id != GLOBAL.owoID:
            return
        await self.detect_pets(message)
        if not message.embeds:
            return
        embed = message.embeds[0]

        author_icon = (
            str(embed.author.icon_url)
            if embed.author and embed.author.icon_url
            else None
        )
        author_name = (
            str(embed.author.name) if embed.author and embed.author.name else None
        )

        footer_text = embed.footer.text if embed.footer and embed.footer.text else None

        if not footer_text:
            return
        player_id = self.get_userid(author_icon)
        if player_id is None:
            return

        if player_id == self.bot.user.id or (
            player_id == 123
            and GLOBAL.get_value("user.username").lower()
            == author_name.split(" goes into battle!")[0].strip().lower()
        ):
            for key in [
                "OwO.daily.battle",
                "OwO.weekly.battle",
                "OwO.monthly.battle",
                "OwO.total.battle",
            ]:
                GLOBAL.set_owostats(key)
            # Hasil battle
            if match := re.search(self.regex_win, footer_text):
                return await LOG.battle(message, "win", int(match.group(1)))
            elif match := re.search(self.regex_lost, footer_text):
                return await LOG.battle(message, "lost", int(match.group(1)))


async def setup(bot):
    await bot.add_cog(Pets(bot))
