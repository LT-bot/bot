from discord.ext import commands
import discord

class Replace_me(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
    

def setup(client: commands.Bot) -> None:
    client.add_cog(Replace_me(client))
    
