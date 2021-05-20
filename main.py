import discord
from discord.ext import commands
import logging
from configparser import ConfigParser
from typing import Union, Literal
from os import walk
from discord_slash import SlashCommand

conf = ConfigParser()
conf.read("main.conf")

# Recommended logging setup
logger = logging.getLogger('lt2b2')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='data/lt2b2.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
#logger.addHandler(handler)
logging.basicConfig(level=logging.INFO, handlers=[handler])

intents = discord.Intents(guild_messages=True, members=True, guilds=True)
Bot = commands.Bot(command_prefix="##", intents=intents)#discord.Intents.all())
#Slash = SlashCommand(Bot, override_type=True, sync_on_cog_reload=True, sync_commands=True)

# Always load Ctrl cog
default_cogs = set(conf['General']['Default Cogs'].split()) | {"Ctrl", }
available_cogs = set(i[:-3] for i in next(walk('cogs/'))[2])


@Bot.check
def global_check(context: commands.Context) -> bool:
    """
    Global check, prevent bots from using commands.
    """
    return not context.author.bot

@Bot.event
async def on_ready() -> None:
    # Unnecessary
    logger.info("Logger begins here:")
    # Only load cogs after connection established
    # Avoid unnecessary errors
    for cog in default_cogs & available_cogs:
        try:
            Bot.load_extension('cogs.' + cog.capitalize())
            logger.info(f"Loaded cog {cog.capitalize()}")
        except Exception as e:
            logger.exception(e)
    print("Ready!")

if __name__ == "__main__":
    with open('data/token') as f:
        token = f.read()[:-1]
    Bot.run(token)
