import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from configparser import ConfigParser
from typing import Optional, List
from time import time

conf = ConfigParser()
conf.read("main.conf")
guild_ids = [int(i) for i in conf["Slash"]["guild"].split()]
default_avatar = conf["Slash"]["default avatar"]
# disclaimer: regex parsing and shasums would be "better", but this is faster
secret_num = int(conf["Slash"]["secret num"])
remove_fslash = str.maketrans("/", " ")


class Slash(commands.Cog):
    def __init__(self, Bot):
        self.Bot = Bot
        self.as_webhook = Bot.as_webhook
        # self.cog_before_invoke = self.find_webhooks

    @cog_ext.cog_slash(name="mock", guild_ids=guild_ids, description="Mock someone")
    async def _mock(self, context: SlashContext) -> None:
        await self.as_webhook(
            context.channel,
            "https://upload.wikimedia.org/wikipedia/commons/8/89/HD_transparent_picture.png",
            ".",
            conf["Slash"]["mock url"],
        )
        await context.send("ok", delete_after=0.01)

    @cog_ext.cog_slash(
        name="sarcasm",
        guild_ids=guild_ids,
        description="Unironically",
        options=[
            create_option(
                name="message",
                description="Say something sErIoUs.",
                option_type=3,
                required=True,
            )
        ],
    )
    async def _sarcasm(self, context: SlashContext, message: str) -> None:
        """
        Say something totally serious.
        """
        message = list(message.lower().translate(remove_fslash))
        # This seems like the quickest way to do it?
        for i in range((len(message) + 1) // 2):
            message[2 * i] = message[2 * i].upper()

        message = "".join(message)
        context.author.avatar_url

        name = context.author.nick or context.author.name

        await self.as_webhook(context.channel, context.author.avatar_url, name, message)
        await context.send("ok", delete_after=0.01)

    @cog_ext.cog_slash(
        name="anon",
        guild_ids=guild_ids,
        description="Send something anonymously, no links.",
        options=[
            create_option(
                name="message",
                description="Share your secret.",
                option_type=3,
                required=True,
            )
        ],
    )
    async def _anon(self, context: SlashContext, message: str) -> None:
        """
        Say something anonymously. ID changes every 17 minutes.
        """
        # this isn't cryptographically safe or anything, but it's faster
        id = (context.author.id + round(time(), -3)) % secret_num

        await self.as_webhook(
            context.channel,
            default_avatar,
            f"Anon {id}",
            message.translate(remove_fslash),
        )
        await context.send("ok", hidden=True)


def setup(Bot):
    Bot.add_cog(Slash(Bot))
