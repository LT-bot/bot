from discord.ext import commands
from typing import Literal
import logging
from configparser import ConfigParser
import discord
import aiofiles as af
from collections import deque 

logger = logging.getLogger('lt2b2')
conf = ConfigParser()
conf.read("main.conf")

#ID_owner = conf['General']['Owner ID']


class CogType(commands.Converter):
    """
    Parse cogs.
    """
    def __init__(self, *args, **kwargs):
        """
        Init super then add cogs list.
        """
        super().__init__(*args, **kwargs)
        self.cogs_list = conf['General']['Cog List'].split()

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
        #self.R_bot_ctrl = Bot.guilds[0].get_role(int(conf['Roles']['bot ctrl']))
        
    async def cog_check(self, context: commands.Context) -> bool:
        """
        Only bot owner and people with bot ctrl role can do this.
        """
        return await commands.check_any(commands.is_owner(), 
                commands.has_role(int(conf['Roles']['bot ctrl']))).predicate(context)

    async def cog_handler(self, context: commands.Context, 
            pre: Literal['re', 'un', ''], *cogs: str) -> None:
        """
        Sanitize list and handle [cogs] according to [pre]fix.
        Shameless code reuse, I know.
        """
        if not any(*cogs): return
        cogs = set(*cogs)
        loaded = set([i.lstrip("cogs.") for i in self.Bot.extensions.keys()])
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
                failed |= {cog}
                logging.exception(f"Can't {pre}load {cog}.")

        if failed:
            msg += f"Couldn't {pre}load {', '.join(failed)}. Check error log.\n"
        elif ok := cogs - failed:
            msg += f"Successfully {pre}loaded {', '.join(ok)}.\n"

        await context.send(msg)

    @commands.group(name='cogs', aliases=['cog', 'c'])
    async def _cogs(self, context: commands.Context) -> None:
        """
        A command group for cogs.
        """
        pass

    @_cogs.command(name='unload', aliases=['u', '-'])
    async def unload(self, context: commands.Context, *cogs: CogType) -> None:
        """
        Unload one or more cogs.
        """
        await self.cog_handler(context, 'un', cogs)

    @_cogs.command(name='reload', aliases=['r'])
    async def reload(self, context: commands.Context, *cogs: CogType) -> None:
        """
        Reload one or more cogs that are already loaded.
        """
        await self.cog_handler(context, 're', cogs)

    @_cogs.command(name='load', aliases=['l', '+'])
    async def load(self, context: commands.Context, *cogs: CogType) -> None:
        """
        Load one or more cogs.
        """
        await self.cog_handler(context, '', cogs)

    @_cogs.command(name='status', aliases=['s'])
    async def status(self, context: commands.Context) -> None:
        """
        Show list of loaded cogs.
        """
        loaded = [i.lstrip("cogs.") for i in self.Bot.extensions.keys()]
        await context.send(f'Cogs currently loaded: {", ".join(loaded)}.')

    @commands.group(name='debug', aliases=['d'])
    async def _debug(self, context: commands.Context) -> None:
        """
        Some debbuging commands.
        """
        pass

    @_debug.command(name='log', aliases=['l'])
    async def _log(self, context: commands.Context, num: int=-1) -> None:
        """
        Send log file or last num log entries.
        """
        if num == -1:
            await context.send('Cringe', file=discord.File('data/lt2b2.log'))
        elif num > 0:
            async with af.open('data/lt2b2.log', 'r') as f:
                last_n = deque(f.buffer, num)
            try:
                await context.send('```'+b''.join(last_n).decode()+'```')
            except:
                logger.error("Can't send log")

    @_debug.command(name='layout', aliases=['la'])
    async def _layout(self, context: commands.Context) -> None:
        """
        Write layout of channels and role permissions to file.
        """
        discord.CategoryChannel.changed_roles
        table = "```\n"
        for category in context.guild.categories:
            table += str(category) + "\t:\n"
            table += "\tCategory overwrites:\n"
            for role, overwrite in category.overwrites.items():
                table += f"\t\t{str(role)}:\n"
                for pair in list(iter(overwrite)):
                    if not pair[1] is None:
                        table += f"\t\t\t{pair[0]} :{str(pair[1])[0]}\n"

        table += "```"
        with open('data/table', 'w') as f:
            f.write(table)
            #for channel in category.channels:
            #    table += f"\t{str(channel)}\t:\n"
            #    for role in channel.changed_roles:
            #        pass

    @commands.group(name='settings', aliases=['s'])
    async def _settings(self, context: commands.Context) -> None:
        pass

    @_settings.command(name='nick', aliases=['n'])
    async def nick(self, context: commands.Context, new_nick: str=None) -> None:
        self_member = context.guild.get_member(self.Bot.user.id)
        await self_member.edit(nick=new_nick)

def setup(Bot: commands.Bot) -> None:
    Bot.add_cog(Ctrl(Bot))
