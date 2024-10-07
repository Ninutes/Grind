import selfcord
from selfcord.ext import commands
from config import GLOBAL
from modules.logger import LOG


class Events(commands.Cog):
    """The description for Events goes here."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
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
        if message.author.bot:
            return
        if message.mention_everyone:
            return

        if (self.bot.user.mentioned_in(message)
                or any(name in message.content.lower() for name in [self.bot.user.display_name, str(self.bot.user.id)])
            ):
            await LOG.info(f'I\'ve found something in {message.jump_url}\n{message.author.mention} :\n```{message.content}```')
        spy = GLOBAL.get_value('spy')
        if spy['enable']:
            spy_member = self.bot.get_user(int(spy['ID']))
            if spy_member is None: return
            if (spy_member.mentioned_in(message)
                or any(name in message.content.lower() for name in [spy_member.name, str(spy_member.id), spy_member.display_name])
                ) or message.author.id == spy_member.id:
                await LOG.info(f'I\'ve got something in {message.jump_url}\n{message.author.mention} :\n```{message.content}```')


async def setup(bot):
    await bot.add_cog(Events(bot))
