
import datetime
from typing import Optional
import selfcord
from selfcord import Embed, Webhook

from config import GLOBAL, Auth
from twocaptcha import TwoCaptcha
from requests import post
import aiohttp


async def _webhook(msg: selfcord.Message = None, content: str = None, embed: Embed = None, type: str = 'log'):
    url = GLOBAL.get_value('webhook.URL') if type == 'log' else GLOBAL.get_value('webhook.captchaURL')
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(url, session=session)
        await webhook.send(
            content=content,
            username=msg.author.name if msg else GLOBAL.get_value('user.username'),
            avatar_url=msg.author.avatar.url if msg else GLOBAL.get_value('user.avatarURL'),
            embed=embed
        )

async def get_balance():
    try:
        two_captcha = TwoCaptcha(Auth.APIKEY)
        if two_captcha:
            balance = two_captcha.balance()
            return round(balance, 1)
    except Exception as e:
        await LOG.failure(e)

async def send_tele(content):
    try:
        post(url=f"https://api.telegram.org/{Auth.TELEAPI}/sendMessage?chat_id={GLOBAL.get_value('tele.chatID')}&text={content}&parse_mode=MarkdownV2")
    except Exception as e:
        await LOG.failure(e)

class Log:
    
    def __init__(self):
        self.username = GLOBAL.get_value('user.username')
        self.avatarURL = GLOBAL.get_value('user.avatarURL')
        self.wb_ping = GLOBAL.get_value('webhook.ping', GLOBAL.get_value('user.ID'))
        pass
    
    async def captcha(self, message: selfcord.Message, key : str, fail: Optional[str] = None):
        balance = await get_balance()
        flag = '✅' if key == 'solved' else '❌' if key == 'not solved' else '⚠️'
        color = selfcord.Color.green() if key == 'solved' else selfcord.Color.red()
        embed = Embed(
            description=f'`{flag}` Captcha **{key}** in {message.jump_url}',
            timestamp=datetime.datetime.now(),
            color=color
        )
        if fail:
            embed.description += f'\n`⚠️` 10 minutes failed: {fail}'
        if balance:
            embed.set_footer(text=f'balance: $ {balance}', icon_url='https://cdn.discordapp.com/emojis/1179649531927863397.webp')

        if message.attachments:
            embed.set_image(url=message.attachments[0].url)
        if key in ['not solved', 'detected']:
            await send_tele('⚠️ Captcha detected')
        
        await _webhook(
            content=f'<@{self.wb_ping}>',
            embed=embed,
            type='captcha'
        )

    async def captcha_failed(self, reason: str):
        embed = Embed(
            description=reason,
            color=selfcord.Color.red()
        )
        await _webhook(
            embed=embed,
            type='captcha'
        )
    
    async def battle(self, message : selfcord.Message, key:str, value: int):
        b_embed = message.embeds[0]
        embed = Embed(
            color=b_embed.color
        )
        embed.add_field(name=b_embed.fields[0].name, value=b_embed.fields[0].value)
        embed.add_field(name=b_embed.fields[1].name, value=b_embed.fields[1].value)
        embed.set_footer(text=b_embed.footer.text)
        await _webhook(
            msg=message,
            content=f'<@{self.wb_ping}> I\'ve got something in {message.jump_url}',
            embed=embed,
        )
        if key ==  'lost':
            return await LOG.failure(f'You\'ve lost your streak of **{value}** win')
        return await LOG.success(f'You\'ve reach **{value}** win streak!')

    async def pets(self, message : selfcord.Message):
        embed = Embed(
            description=message.content,
            timestamp=message.created_at,
            color=selfcord.Color.green()
        )
        await _webhook(
            msg=message,
            content=f'<@{self.wb_ping}>',
            embed=embed,
        )
    
    async def huntbot(self, message: selfcord.Message):
        embed = Embed(
            description=message.content,
            timestamp=message.created_at,
            color=selfcord.Color.blue()
        )
        await _webhook(
            msg=message,
            content=f'<@{self.wb_ping}>',
            embed=embed,
        )
    async def success(self, reason : str):
        color = selfcord.Color.green()
        embed = Embed(
            description=reason,
            timestamp=datetime.datetime.now(),
            color=color
        )
        await _webhook(
            embed=embed,  
        )
    async def failure(self, reason : str):
        color = selfcord.Color.red()
        embed = Embed(
            description=reason,
            timestamp=datetime.datetime.now(),
            color=color
        )
        await _webhook(
            embed=embed,  
        )
    async def info(self, reason : str):
        color = selfcord.Color.green()
        embed = Embed(
            description=reason,
            timestamp=datetime.datetime.now(),
            color=color
        )
        await _webhook(
            embed=embed,  
        )
    async def warning(self, reason : str):
        color = selfcord.Color.gold()
        embed = Embed(
            description=reason,
            timestamp=datetime.datetime.now(),
            color=color
        )
        await _webhook(
            embed=embed,  
        )

    async def log_config(self):
        data = GLOBAL.get_all_data()
        if data:
            channel = GLOBAL.g_channel.id if GLOBAL.g_channel is not None else GLOBAL.get_value('channelID')
            pray = '✅' if data['pray']['enable'] else '❌'
            gem = '✅' if data['gem'] else '❌'
            exp = '✅' if data['exp'] else '❌'
            sleep = '✅' if data['sleep']['enable'] else '❌'
            solve = '✅' if data['autosolve'] else '❌'
            custom = '✅' if data['custom']['enable'] else '❌'
        config = f"`{pray}` pray\n`{gem}` gem\n`{exp}` exp\n`{sleep}` sleep\n`{solve}` solve\n`{custom}` custom text"
        embed = Embed(
            description=f'**CONFIG**\n{config}',
            color=selfcord.Color.blue()
        )
        await _webhook(
            content=f'> **I am here : [ <#{channel}> ] **',
            embed=embed
        )
    
    async def log_avatar(self, user : selfcord.Member):
        embed = Embed(
            color=selfcord.Color.random()
        )
        embed.set_author(name=f'{user.name} avatar')
        embed.set_image(url=user.display_avatar.url)
        await _webhook(
            embed=embed
        )
LOG = Log()