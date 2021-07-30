import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from configparser import ConfigParser
from typing import Optional, List
from time import time

conf = ConfigParser()
conf.read("main.conf")
guild_ids = [int(i) for i in conf['Slash']['guild'].split()]
default_avatar = conf['Slash']['default avatar']
#disclaimer: regex parsing and shasums would be "better", but this is faster
secret_num = int(conf['Slash']['secret num'])
remove_fslash = str.maketrans("/", " ")


class Slash(commands.Cog):
    def __init__(self, Bot):
        self.Bot = Bot
        self.webhooks = {}
        #self.cog_before_invoke = self.find_webhooks

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
        await webhook[0].send(**opts)
    
    @commands.command(name='init', aliases=['i'])
    async def _init(self, context: commands.Context):
        chan = context.channel
        hooks = await chan.webhooks()
        for hook in hooks:
            if hook.name == 'lt_bot_hooker':
                self.webhooks[chan.id] = hook
                return
        self.webhooks[chan.id] = await chan.create_webhook('lt_bot_hooker')

    async def find_webhooks(context):
        print('aaaaa')

    @cog_ext.cog_slash(name="sarcasm", guild_ids=guild_ids,
            description="Unironically",
            options=[
                create_option(
                    name="message",
                    description="Say something sErIoUs.",
                    option_type=3,
                    required=True
                    )
                ]
            )
    async def _sarcasm(self, context: SlashContext, message: str) -> None:
        """
        Say something totally serious.
        """
        message = list(message.lower().translate(remove_fslash))
        # This seems like the quickest way to do it?
        for i in range((len(message)+1)//2):
            message[2*i] = message[2*i].upper()

        message = "".join(message)
        context.author.avatar_url 
        
        name = context.author.nick or context.author.name

        await self.as_webhook(context.channel, context.author.avatar_url, 
                name, message)
        await context.send('ok', delete_after=0.01)

    
    @cog_ext.cog_slash(name="anon", guild_ids=guild_ids,
            description="Send something anonymously, no links.",
            options=[
                create_option(
                    name="message",
                    description="Share your secret.",
                    option_type=3,
                    required=True
                    )
                ]
            )
    async def _anon(self, context: SlashContext, message: str) -> None:
        """
        Say something anonymously. ID changes every 17 minutes.
        """
        #this isn't cryptographically safe or anything, but it's faster
        id = (context.author.id + round(time(),-3))%secret_num

        await self.as_webhook(context.channel, default_avatar,
                f"Anon {id}", message.translate(remove_fslash))
        await context.send('ok', hidden=True)

def setup(Bot):
    Bot.add_cog(Slash(Bot))
