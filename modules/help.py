import selfcord
from selfcord.ext import commands

from config import GLOBAL, Auth
from modules.logger import LOG, _webhook


class MyHelp(commands.HelpCommand):
    def __init__(self,):
        super().__init__()
        attributes = {
            'name': "help",
            'aliases': ["h"],
            'cooldown': commands.CooldownMapping.from_cooldown(2, 5.0, commands.BucketType.user)
        }
        self.command_attrs = attributes

    async def send_error_message(self, error):
        await LOG.failure(error)
    async def send_bot_help(self, mapping):
        ctx =  self.context
        if not (ctx.author.id == GLOBAL.get_value('user.ID') or ctx.author.id in GLOBAL.get_value('allowedID')):
            return
        embed = selfcord.Embed(
            color=selfcord.Color.blue()
            )
        embed.set_author(name=f"List Available Commands", icon_url="https://cdn.discordapp.com/emojis/1166733557482397758.webp?size=96&quality=lossless")
        embed.add_field(name="General", value="`help`, `ping`, `say`, `avatar` , `math`", inline=False)
        embed.add_field(name="Self-Bot", value="`start`, `stop`, `start_custom`, `stop_custom`", inline=False)
        embed.add_field(name="Captcha", value="`dms`", inline=False)
        embed.add_field(name="Settings", value="`config`, `set`, `die`, `load`, `unload`, `reload` ", inline=False)
        embed.set_footer(text=f"type {Auth.PREFIXES}help <command> for more info")
        await _webhook(
            embed=embed)
    
    async def send_cog_help(self, cog):
        embed = selfcord.Embed(title=cog.qualified_name,
                              color=selfcord.Color.blue())
        embed.description = cog.description or "No description provided for this category."

        # Add a field for each command in the cog
        for command in cog.get_commands():
            embed.add_field(
                name=command.name, value=command.short_doc or "No description available.", inline=False)

        await _webhook(
            embed=embed)

    async def send_command_help(self, command):
        embed = selfcord.Embed(title=command.qualified_name.upper(),
                              color=selfcord.Color.blue())
        embed.add_field(name="Description",
                        value=command.description, inline=False)
        embed.add_field(
            name="Usage", value=f"`{self.context.prefix}{command.qualified_name} {command.signature}`", inline=False)
        if command.aliases:
            embed.add_field(name="Aliases", value=", ".join(
                command.aliases), inline=False)
            embed.set_footer(
                text=f"type {Auth.PREFIXES}help <command> for more info")

        await _webhook(
            embed=embed)