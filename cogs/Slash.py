import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from configparser import ConfigParser

conf = ConfigParser()
conf.read("main.conf")
guild_ids = conf['Slash']['Guild'].split()

class Slash(commands.Cog):
    def __init__(self, Bot):
        self.Bot = Bot

    @cog_ext.cog_slash(name="embed", guild_ids=guild_ids)
    async def _embed(self, context: SlashContext):
        embed = discord.Embed(title="embed test")
        await context.send(content="test", embeds=[embed])

def setup(Bot):
    Bot.add_cog(Slash(Bot))
