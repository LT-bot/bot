from discord.ext import commands
import discord
from configparser import ConfigParser

conf = ConfigParser()
conf.read("main.conf")

R_manage_member_roles = conf['Roles']['manage member roles']

class Roles(commands.Cog):
    def __init__(self, Bot: commands.Bot) -> None:
        self.Bot = Bot
        self.R_verified = Bot.guilds[0].get_role(int(conf['Roles']['verified']))
    

    @commands.group(name="roles", aliases=['role', 'r'])
    async def roles(self, context: commands.Context):
        pass

    @roles.command(name="verify", aliases=['v'])
    @commands.check_any(commands.has_role(R_manage_member_roles),
                        commands.has_permissions(manage_roles=True))
    async def verify(self, context: commands.Context, 
            members: commands.Greedy[discord.Member]) -> None:
        """
        Shortcut for giving the verification role.
        """
        for member in members:
            await member.add_roles(self.R_verified,
                    reason=f"Added by {context.author}")

        await context.send("Ok.")

    @roles.command(name="give", aliases=['g', 'add'])
    async def give(self, context: commands.Context,
            members: commands.Greedy[discord.Member]) -> None:
        pass


def setup(Bot: commands.Bot) -> None:
    Bot.add_cog(Roles(Bot))
    
