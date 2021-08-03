import discord
from discord.ext import commands
import logging
from configparser import ConfigParser
from typing import Union, Literal, Optional, List
from os import walk
from discord_slash import SlashCommand

conf = ConfigParser()
conf.read("main.conf")

LOGGER_NAME = conf['Dev']['logger']
LOG_PATH = conf['Dev']['log path']

# Recommended logging setup
logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.INFO)
handler = logging.FileHandler(
        filename=LOG_PATH, encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logging.basicConfig(level=logging.INFO, handlers=[handler])

# Storing webhooks here is very useful
class My_Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.webhooks = {}

    async def as_webhook(self, channel: discord.TextChannel, avatar_url: str, name: str,
            message: str, attachments: Optional[List[discord.Attachment]]=None ) -> None:
        """
        Send a message through a webhook. May contain list of files. No mentions
        because webhooks can't be blocked and it's annoying.
        """
        opts = {'content': message,
                'files': attachments,
                'avatar_url': avatar_url,
                'username': name,
                'allowed_mentions': discord.AllowedMentions.none()
                }
        #webhook = await channel.webhooks()
        try:
            webhook = self.webhooks[channel.id]
        except KeyError:
            pass
        await webhook.send(**opts)

# Init bot
intents = discord.Intents(guild_messages=True, members=True, guilds=True)
Bot = My_Bot(command_prefix="##", intents=intents)#discord.Intents.all())
Slash = SlashCommand(Bot, override_type=True, sync_on_cog_reload=True, sync_commands=True)

# Always load Ctrl cog
default_cogs = set(conf['General']['default cogs'].split()) | {"Ctrl", }
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
    # Get webhooks for whatever channels it can
    for chan in Bot.get_all_channels():
        if not str(chan.type) == 'text':
            continue 
        hooks = await chan.webhooks()
        try:
            for hook in hooks:
                if hook.name == 'lt_bot_hooker':
                    Bot.webhooks[chan.id] = hook
                    raise GeneratorExit #hax jumps from here
            try:
                Bot.webhooks[chan.id] = await chan.create_webhook(name='lt_bot_hooker')
                logger.info(f'Webhook created for {str(chan)}.')
            except Exception as e:
                logger.error(f'Cannot create webhook for {str(chan)}:\n{e}')

        except GeneratorExit: #to here
            logger.info(f'Webhook found for {str(chan)}.')

    logger.info('Ready!')
    print("Ready!")

if __name__ == "__main__":
    with open('data/token') as f:
        token = f.read()[:-1]
    Bot.run(token)
