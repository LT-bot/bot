from discord.ext import commands
import discord

class Replace_me(commands.Cog):
    def __init__(self, Bot: commands.Bot) -> None:
        self.Bot = Bot
    

def setup(Bot: commands.Bot) -> None:
    Bot.add_cog(Replace_me(Bot))
    
