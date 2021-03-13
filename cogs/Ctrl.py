from discord.ext import commands
from typing import Literal
import logging
from configparser import ConfigParser
import discord

logger = logging.getLogger('lt2b2')
conf = ConfigParser()
conf.read("main.conf")
lvl = "Debug"

class CogType(commands.Converter):
    """
    Parse cogs.
    """
    def __init__(self, *args, **kwargs):
        """
        Init super then add cogs list.
        """
        super().__init__(*args, **kwargs)
        self.cogs_list = conf[lvl]['Cog List'].split()

    async def convert(self, context: commands.Context, name: str) -> str:
        name = name.capitalize()
        if name in self.cogs_list:
            return name
        else:
            # there's no need to log this as errors aren't useful
            await context.send(f"No cog named {name}")


class Ctrl(commands.Cog):
    def __init__(self, Bot: commands.Bot) -> None:
        self.Bot = Bot


    async def cog_handler(self, context: commands.Context, 
            pre: Literal['re', 'un', ''], *cogs: str) -> None:
        """
        Sanitize list and handle [cogs] according to [pre]fix.
        Shameless code reuse, I know.
        """
        cogs = set(*cogs)
        loaded = set([i.strip("cogs.") for i in self.Bot.extensions.keys()])
        failed = set()
        msg = ""

        # If action requires cogs to be loaded, but some aren't
        if pre and (not_loaded := cogs - loaded):
            msg += f"Can't {pre}load cogs that aren't loaded: {', '.join(not_loaded)}.\n"
            cogs -= not_loaded

        # Also don't reload cogs that are alreay loaded
        elif not pre and (already_loaded := cogs & loaded):
            msg += f"These cogs are already loaded: {', '.join(already_loaded)}.\n"
            cogs -= already_loaded
    
        for cog in cogs:
            try:
                getattr(self.Bot, pre + "load_extension")("cogs." + cog)
            except:
                failed += cog
                logging.exception(f"Can't {pre}load {cog}.")

        if failed:
            msg += f"Couldn't {pre}load {', '.join(failed)}. Check error log.\n"
        elif ok := cogs - failed:
            msg += f"Successfully {pre}loaded {', '.join(ok)}.\n"

        await context.send(msg)

    @commands.group(name='cogs', aliases=['cog', 'c'])
    async def cogs(self, context: commands.Context) -> None:
        """
        A command group for cogs.
        """
        pass

    @cogs.command(name='unload', aliases=['u', '-'])
    async def unload(self, context: commands.Context, *cogs: CogType) -> None:
        """
        Unload one or more cogs.
        """
        await self.cog_handler(context, 'un', cogs)

    @cogs.command(name='reload', aliases=['r'])
    async def reload(self, context: commands.Context, *cogs: CogType) -> None:
        """
        Reload one or more cogs that are already loaded.
        """
        await self.cog_handler(context, 're', cogs)

    @cogs.command(name='load', aliases=['l', '+'])
    async def load(self, context: commands.Context, *cogs: CogType) -> None:
        """
        Load one or more cogs.
        """
        await self.cog_handler(context, '', cogs)

def setup(Bot: commands.Bot) -> None:
    Bot.add_cog(Ctrl(Bot))
