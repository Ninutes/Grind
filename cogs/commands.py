from selfcord.ext import commands
import selfcord

from config import GLOBAL
from modules.logger import LOG


class CMD(commands.Cog):
    """The description for CMD goes here."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    def cog_check(self, ctx: commands.Context):
        return ctx.author.id in GLOBAL.get_value('allowedID')

    @commands.command(aliases=['av'])
    async def avatar(self, ctx : commands.Context, user : selfcord.User):
        await ctx.message.delete()
        LOG.log_avatar(user)
    @commands.command()
    async def say(self, ctx: commands.Context, *, message: str):
        await ctx.message.delete()
        await ctx.send(f'{message}')
    @commands.command(aliases=['math', 'calc'])
    async def math_calc(self, ctx: commands.Context, *, expression):
        await ctx.message.delete()
        try:
            result = eval(expression)
        except Exception as e:
            return await ctx.send(f'`{e}`')
        return await ctx.send(f'{result:,}')
    @commands.command(aliases=['set'])
    async def set_mode(self, ctx: commands.Context, key: str, value: str = None):
        if value is not None:
            value = True if value.lower() == 'on' else False if value.lower() == 'off' else value
        await ctx.message.delete()
        GLOBAL.set_value(key, value)
        return LOG.success(f'Successfully set **{key}** to `{value}`')
    @commands.command()
    async def tes_embed(self, ctx: commands.Context, msgID: int):
        await ctx.message.delete()
        msg = await ctx.fetch_message(msgID)
        return LOG.battle(msg, 'win', 80)
    @commands.command(aliases=['config'], description='Show self-bot configuration')
    async def config_show(self, ctx):
        await ctx.message.delete()
        return LOG.log_config()
    @commands.command(aliases=['but'])
    async def click_button(self, ctx: commands.Context, key: str):
        await ctx.message.delete()
        async for msg in ctx.message.channel.history(limit=10):
            if msg.components:
                for i in range(len(msg.components)):
                    for comp in msg.components[i].children:
                        if isinstance(comp, selfcord.Button):
                            if comp.label:
                                if comp.label.lower() == key:
                                    await comp.click()
                                    break
                            elif comp.emoji.name:
                                if comp.emoji.name == key:
                                    await comp.click()
                                    break
    
async def setup(bot):
    await bot.add_cog(CMD(bot))
