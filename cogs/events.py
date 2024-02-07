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
            await LOG.failure(error)
        elif isinstance(error, commands.errors.MissingPermissions):
            await LOG.failure(error)
        elif isinstance(error, commands.errors.CheckFailure):
            return
        elif isinstance(error, commands.errors.CommandNotFound):
            return
        elif isinstance(error, commands.errors.CommandOnCooldown):
            await LOG.failure(error)
        elif isinstance(error, commands.errors.CommandInvokeError):
            await LOG.failure(error)
        raise error
    @commands.Cog.listener()
    async def on_message(self, message: selfcord.Message):
        if message.channel.type == selfcord.ChannelType.private:
            if message.author.id == GLOBAL.reactionID:
                if 'huntbot' in message.content:
                    return await LOG.huntbot(message)
        if message.author.bot:return
        if message.mention_everyone:return
        if self.bot.user.mentioned_in(message) or str(self.bot.user.id) in message.content or self.bot.user.display_name in message.content:
            user = message.author
            await LOG.info(f'{user.mention} have mentioned you in {message.jump_url}\n```{message.content}```')
async def setup(bot):
    await bot.add_cog(Events(bot))
