import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from configparser import ConfigParser
from typing import Optional, List

conf = ConfigParser()
conf.read("main.conf")
guild_ids = [int(i) for i in conf['Slash']['Guild'].split()]

async def as_webhook(channel: discord.TextChannel, avatar_url: str, name: str, 
        message: str, attachments: Optional[List[discord.Attachment]]=None ) -> None:
    opts = {'content': message,
            'files': attachments,
            'avatar_url': avatar_url,
            'username': name
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
        Message = list(Message.lower())
        # This seems like the quickest way to do it?
        for i in range(len(Message)//2):
            Message[2*i] = Message[2*i].upper()

        Message = "".join(Message)
        context.author.avatar_url 

        await context.respond()
        await as_webhook(context.channel, context.author.avatar_url, 
                context.author.nick, Message)
        #await context.send(content=Message)

def setup(Bot):
    Bot.add_cog(Slash(Bot))
