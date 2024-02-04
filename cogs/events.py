import selfcord
from selfcord.ext import commands
from config import GLOBAL
from modules.logger import LOG


class Events(commands.Cog):
    """The description for Events goes here."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        

    @commands.Cog.listener()
    async def on_command_error(self, ctx : commands.Context, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            LOG.failure(error)
        elif isinstance(error, commands.errors.MissingPermissions):
            LOG.failure(error)
        elif isinstance(error, commands.errors.CheckFailure):
            LOG.failure(error)
        elif isinstance(error, commands.errors.CommandNotFound):
            return
        elif isinstance(error, commands.errors.CommandOnCooldown):
            LOG.failure(error)
        elif isinstance(error, commands.errors.CommandInvokeError):
            LOG.failure(error)
    @commands.Cog.listener()
    async def on_message(self, message: selfcord.Message):
        if message.channel.type == selfcord.ChannelType.private:
            if message.author.id == GLOBAL.reactionID:
                if 'huntbot' in message.content:
                    return LOG.huntbot(message)
        if message.author.bot:return
        if self.bot.user.mentioned_in(message):
            user = message.author
            LOG.info(f'{user.mention} have mentioned you in {message.jump_url}\n```{message.content}```')
async def setup(bot):
    await bot.add_cog(Events(bot))
