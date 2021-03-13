from discord.ext import commands
import discord
from string import punctuation

punc_table = str.maketrans('', '', punctuation)
punc_table.update(str.maketrans('-',' '))

with open("data/responses", 'r') as f:
    raw = f.read()
    responses = raw.splitlines()
    searchlist = raw.translate(punc_table).lower().splitlines()

class Listener(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return None
        m = message.content.translate(punc_table).lower()
        if not m:
            return None
        try:
            i = searchlist.index(m)
            if response := responses[i+1]:
                await message.channel.send(response)
        except:
            pass

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        channel = member.guild.system_channel
        await channel.send(f"{responses[48]} {member.mention}!")

def setup(client: commands.Bot) -> None:
    client.add_cog(Listener(client))
    
