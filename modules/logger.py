
import datetime
from typing import Optional
import selfcord
from selfcord import Embed

from config import GLOBAL, Auth
from twocaptcha import TwoCaptcha
from requests import post
WB = selfcord.SyncWebhook.from_url(GLOBAL.get_value('webhook.URL'))

def get_balance():
    try:
        two_captcha = TwoCaptcha(Auth.APIKEY)
        if two_captcha:
            balance = two_captcha.balance()
            return round(balance, 1)
    except Exception as e:
        LOG.failure(e)

def send_tele(content):
    try:
        post(url=f"https://api.telegram.org/{Auth.TELEAPI}/sendMessage?chat_id={GLOBAL.get_value('tele.chatID')}&text={content}&parse_mode=MarkdownV2")
    except Exception as e:
        LOG.failure(e)

class Log:
    
    def __init__(self):
        self.username = GLOBAL.get_value('username')
        self.avatarURL = GLOBAL.get_value('avatarURL')
        self.wb_ping = GLOBAL.get_value('webhook.ping')
        pass
    
    def captcha(self, message: selfcord.Message, key : str, fail: Optional[str] = None):
        balance = get_balance()
        flag = '✅' if key == 'solved' else '❌' if key == 'not solved' else '⚠️'
        color = selfcord.Color.green() if key == 'solved' else selfcord.Color.red()
        embed = Embed(
            description=f'`{flag}` Captcha **{key}** in {message.jump_url}',
            timestamp=datetime.datetime.now(),
            color=color
        )
        if fail:
            embed.description += f'\n10 minutes failed: {fail}'
        if balance:
            embed.set_footer(text=f'balance: $ {balance}', icon_url='https://cdn.discordapp.com/emojis/1179649531927863397.webp')

        if message.attachments:
            embed.set_image(url=message.attachments[0].url)
        if key in ['not solved', 'detected']:
            send_tele('⚠️ Captcha detected')
        return WB.send(
            content=f'<@{self.wb_ping}>',
            username=self.username,
            avatar_url=self.avatarURL,
            embed=embed,  
        )
    
    def battle(self, message : selfcord.Message, key:str, value: int):
        b_embed = message.embeds[0]
        embed = Embed(
            color=b_embed.color
        )
        embed.add_field(name=b_embed.fields[0].name, value=b_embed.fields[0].value)
        embed.add_field(name=b_embed.fields[1].name, value=b_embed.fields[1].value)
        embed.set_author(name=b_embed.author.name, url=b_embed.author.url)
        embed.set_footer(text=b_embed.footer.text)
        WB.send(
            content=f'<@{self.wb_ping}>',
            username=message.author.name,
            avatar_url=message.author.avatar.url,
            embed=embed,
        )
        if key ==  'lost':
            return LOG.failure(f'You\'ve lost your streak of **{value}** win')
        return LOG.success(f'You\'ve reach **{value}** win streak!')
    def pets(self, message : selfcord.Message):
        embed = Embed(
            description=message.content,
            timestamp=message.created_at,
            color=selfcord.Color.green()
        )
        WB.send(
            content=f'<@{self.wb_ping}>',
            username=message.author.name,
            avatar_url=message.author.display_avatar.url,
            embed=embed,
        )
    
    def huntbot(self, message: selfcord.Message):
        embed = Embed(
            description=message.content,
            timestamp=message.created_at,
            color=selfcord.Color.blue()
        )
        WB.send(
            content=f'<@{self.wb_ping}>',
            username=message.author.name,
            avatar_url=message.author.display_avatar.url,
            embed=embed,
        )
    def success(self, reason : str):
        color = selfcord.Color.green()
        embed = Embed(
            description=reason,
            timestamp=datetime.datetime.now(),
            color=color
        )
        return WB.send(
            username=self.username,
            avatar_url=self.avatarURL,
            embed=embed,  
        )
    def failure(self, reason : str):
        color = selfcord.Color.red()
        embed = Embed(
            description=reason,
            timestamp=datetime.datetime.now(),
            color=color
        )
        return WB.send(
            username=self.username,
            avatar_url=self.avatarURL,
            embed=embed,  
        )
    def info(self, reason : str):
        color = selfcord.Color.green()
        embed = Embed(
            description=reason,
            timestamp=datetime.datetime.now(),
            color=color
        )
        return WB.send(
            username=self.username,
            avatar_url=self.avatarURL,
            embed=embed,  
        )
    def warning(self, reason : str):
        color = selfcord.Color.gold()
        embed = Embed(
            description=reason,
            timestamp=datetime.datetime.now(),
            color=color
        )
        return WB.send(
            username=self.username,
            avatar_url=self.avatarURL,
            embed=embed,  
        )

    def log_config(self):
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
        WB.send(
            content=f'> **I am here : [ <#{channel}> ] **',
            username=self.username,
            avatar_url=self.avatarURL,
            embed=embed
        )
    
    def log_avatar(self, user : selfcord.Member):
        embed = Embed(
            color=selfcord.Color.random()
        )
        embed.set_author(name=f'avatar')
        embed.set_image(url=user.display_avatar.url)
        WB.send(
            username=user.name,
            avatar_url=user.display_avatar.url,
            embed=embed
        )
LOG = Log()