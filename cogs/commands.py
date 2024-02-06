from typing import Optional
from selfcord.ext import commands
import selfcord

from config import GLOBAL
from modules.logger import LOG, WB


class CMD(commands.Cog):
    """The description for CMD goes here."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    def cog_check(self, ctx: commands.Context):
        return ctx.author.id in GLOBAL.get_value('allowedID') or ctx.author.id == ctx.me.id
    async def _delete_msg(self, ctx: commands.Context):
        try:
            await ctx.message.delete()
        except Exception:
            return
    @commands.command(aliases=['av'])
    async def avatar(self, ctx : commands.Context, user : selfcord.User):
        await self._delete_msg(ctx)
        LOG.log_avatar(user)
    @commands.command()
    async def say(self, ctx: commands.Context, *, message: str):
        await self._delete_msg(ctx)
        await ctx.send(f'{message}')
    @commands.command(aliases=['prefix'])
    async def set_prefix(self, ctx : commands.Context, prefix : str):
        await self._delete_msg(ctx)
        GLOBAL.set_value('prefix', prefix)
        self.bot.command_prefix = prefix
        LOG.success(f'prefix set to `{prefix}`')
    @commands.command(aliases=['math', 'calc'])
    async def math_calc(self, ctx: commands.Context, *, expression):
        await self._delete_msg(ctx)
        try:
            result = eval(expression)
        except Exception as e:
            return await ctx.send(f'`{e}`')
        return await ctx.send(f'{result:,}')
    @commands.command(aliases=['set'])
    async def set_mode(self, ctx: commands.Context, key: str, value: str = None):
        if value is not None:
            value = True if value.lower() == 'on' else False if value.lower() == 'off' else value
        await self._delete_msg(ctx)
        GLOBAL.set_value(key, value)
        return LOG.success(f'Successfully set **{key}** to `{value}`')
    @commands.command()
    async def tes_embed(self, ctx: commands.Context, msgID: int):
        await self._delete_msg(ctx)
        msg = await ctx.fetch_message(msgID)
        return LOG.battle(msg, 'win', 80)
    @commands.command(aliases=['config'], description='Show self-bot configuration')
    async def config_show(self, ctx:commands.Context, all:Optional[str] = None):
        await self._delete_msg(ctx)
        if all == 'all':
            embed = selfcord.Embed(
                title=f'Configurations',
                color=selfcord.Color.blue()
            )
            data = GLOBAL.get_all_data()
            for key, value in data.items():
                inline = False if key in ['OwO', 'user', 'tasks', 'webhook'] else True
                if key == 'OwO':
                    owo = f'''```py\n
- Daily:   OwO: {value["daily"]["owo"]}, Hunt: {value["daily"]["hunt"]}, Battle: {value["daily"]["battle"]}
- Weekly:  OwO: {value["weekly"]["owo"]}, Hunt: {value["weekly"]["hunt"]}, Battle: {value["weekly"]["battle"]}
- Monthly: OwO: {value["monthly"]["owo"]}, Hunt: {value["monthly"]["hunt"]}, Battle: {value["monthly"]["battle"]}
- Total:   OwO: {value["total"]["owo"]}, Hunt: {value["total"]["hunt"]}, Battle: {value["total"]["battle"]}
```'''
                    embed.add_field(name=key, value=owo, inline=inline)
                elif key == 'tasks':
                    fstring = ''
                    for i, v in value.items():
                        fstring += f'[ Task {i}: - Enable: {v["enable"]} - Time: {v["time"]} ]\n💬 Text: {v["text"]}\n'
                    embed.add_field(name=key, value=f'```py\n{fstring}```', inline=inline)
                else:
                    embed.add_field(name=key, value=f'```py\n{value}```', inline=inline)
            
            return WB.send(
                username=ctx.me.display_name,
                avatar_url=ctx.me.display_avatar.url,
                embed=embed,
            )
        return LOG.log_config()
    @commands.command(aliases=['but'])
    async def click_button(self, ctx: commands.Context, key: str):
        await self._delete_msg(ctx)
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
