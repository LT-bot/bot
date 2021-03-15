import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from configparser import ConfigParser
from typing import Optional, List
from time import time

conf = ConfigParser()
conf.read("main.conf")
guild_ids = [int(i) for i in conf['Slash']['Guild'].split()]
default_avatar = conf['Slash']['Default Avatar']
#disclaimer: regex parsing and shasums would be "better", but this is faster
secret_num = int(conf['Slash']['Secret Num'])
remove_fslash = str.maketrans("/", " ")

async def as_webhook(channel: discord.TextChannel, avatar_url: str, name: str, 
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
    webhook = await channel.webhooks()
    await webhook[0].send(**opts)

class Slash(commands.Cog):
    def __init__(self, Bot):
        self.Bot = Bot

    @cog_ext.cog_slash(name="sarcasm", guild_ids=guild_ids,
            description="Need some help getting the message accorss?",
            options=[
                create_option(
                    name="Message",
                    description="Say something serious!",
                    option_type=3,
                    required=True
                    )
                ]
            )
    async def _sarcasm(self, context: SlashContext, Message: str) -> None:
        """
        Say something totally serious.
        """
        Message = list(Message.lower().translate(remove_fslash))
        # This seems like the quickest way to do it?
        for i in range((len(Message)+1)//2):
            Message[2*i] = Message[2*i].upper()

        Message = "".join(Message)
        context.author.avatar_url 
        
        name = context.author.nick or context.author.name

        await context.respond(eat=True)
        await as_webhook(context.channel, context.author.avatar_url, 
                name, Message)
        #await context.send(content=Message)

    
    @cog_ext.cog_slash(name="anon", guild_ids=guild_ids,
            description="Say something anonymously, no links!",
            options=[
                create_option(
                    name="Message",
                    description="Share your secret",
                    option_type=3,
                    required=True
                    )
                ]
            )
    async def _anon(self, context: SlashContext, Message: str) -> None:
        """
        Say something anonymously. ID changes every 17 minutes.
        """
        #this isn't cryptographically safe or anything, but it's faster
        id = (context.author.id + round(time(),-3))%secret_num
        await context.respond(eat=True)
        await as_webhook(context.channel, default_avatar,
                f"Anon {id}", Message.translate(remove_fslash))

def setup(Bot):
    Bot.add_cog(Slash(Bot))
