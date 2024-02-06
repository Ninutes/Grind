from os import getenv
from dotenv import load_dotenv, find_dotenv
import json
from selfcord.ext import commands
load_dotenv(find_dotenv(raise_error_if_not_found=True))

def is_me():
    async def predicate(ctx: commands.Context):
        return ctx.author.id == GLOBAL.get_value('user.ID') or ctx.author.id in GLOBAL.get_value('allowedID')
    return commands.check(predicate)

class Config:
    
    def __init__(self, filename="config.json"):
        self.filename = filename
        self.config = {}
        self.g_channel = None
        self.owoID = 408785106942164992
        self.reactionID = 519287796549156864
        self.load_config()
    
    @property
    def is_captcha(self) -> bool:
        return self.get_value('is_captcha')
    
    @is_captcha.setter
    def is_captcha(self, value):
        self.set_value('is_captcha', value)

    def load_config(self):
        try:
            with open(self.filename, 'r') as file:
                self.config = json.load(file)
        except FileNotFoundError:
            # Create an empty config file if it doesn't exist
            self.save_config()

    def save_config(self):
        with open(self.filename, 'w') as file:
            json.dump(self.config, file, indent=4)

    def set_channel(self, channel):
        self.set_value('channelID', channel.id)
        self.g_channel = channel

    def get_value(self, key, default=None):
        keys = key.split('.')  # Split nested keys by '.'
        current_value = self.config

        for k in keys:
            if isinstance(current_value, dict) and k in current_value:
                current_value = current_value[k]
            else:
                return default

        return current_value
    def get_all_data(self):
        return self.config
    def set_value(self, key, value):
        keys = key.split('.')  # Split nested keys by '.'
        current_dict = self.config

        # Traverse the nested structure to find the appropriate dictionary
        for k in keys[:-1]:
            if k not in current_dict:
                current_dict[k] = {}
            current_dict = current_dict[k]

        # Set the value in the final nested dictionary
        current_dict[keys[-1]] = value

        # Save the updated configuration
        self.save_config()

    def set_owostats(self, key, value = 1):
        keys = key.split('.')  # Split nested keys by '.'
        current_dict = self.config

        # Traverse the nested structure to find the appropriate dictionary
        for k in keys[:-1]:
            if k not in current_dict:
                current_dict[k] = {}
            current_dict = current_dict[k]

        # Set the value in the final nested dictionary
        final_key = keys[-1]
        current_dict[final_key] = current_dict.get(final_key, 0) +value

        # Save the updated configuration
        self.save_config()
    def reset_owostats(self, key : str):
        self.set_value(f'OwO.{key}', {})

GLOBAL = Config()

class Auth:
    # Make sure to add all details in '.env' file
    TOKEN = getenv("TOKEN")
    PREFIXES = GLOBAL.get_value('prefix')
    APIKEY = getenv("2captchaApiKey")
    TELEAPI = getenv("TELEAPI")