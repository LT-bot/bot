from discord.ext import commands
import discord
import logging
from configparser import ConfigParser

logger = logging.getLogger('lt2b2')
conf = ConfigParser()
conf.read("main.conf")


class Replace_me(commands.Cog):
    def __init__(self, Bot: commands.Bot) -> None:
        self.Bot = Bot
    
    @commands.group(name='')
    async def my_group(self, context: commands.Context) -> None:
        pass

    @my_group.command(name='a')
    async def my_command(self, context: commands.Context) -> None:
        pass


def setup(Bot: commands.Bot) -> None:
    Bot.add_cog(Replace_me(Bot))
    
