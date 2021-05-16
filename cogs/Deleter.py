from discord.ext import commands, tasks
import discord
from string import punctuation
from collections import deque
import re
from configparser import ConfigParser

conf = ConfigParser()
conf.read("main.conf")

#list of lists, [[channel id, max messages], ]
channel_list = [ch.split() for ch in conf['Deleter']['channel settings'].split(',')]
bad_words = conf['Deleter']['bad words'].split()
re_bad = re.compile('|'.join([re.escape(word) for word in bad_words]), re.I)
bad, main = 0, 1

class Deleter(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        """
        Use dict of channels with deque for rolling delete, and lists otherwise 
        and max number of messages.
        """
        self.client = client
        self.chan_dict = {}
        for id, n in channel_list:
            self.chan_dict[client.get_channel(id)] = {bad: [], main: ([], n)}
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """
        Add messages to the corresponding queues
        """
        try:
            queues = self.chan_dict[message.channel]
            obj = discord.Object(id=message.id)
            if re_bad.search(message.content):
                queues[bad].append(obj)
            else:
                queues[main].append(obj)
        except KeyError:
            pass
        except discord.HTTPException:
            pass
        except discord.NotFound:
            pass
    
    @tasks.loop(minutes=10)
    async def deleter(self):
        """
        Runs every 10 minutes and deletes from the queues.
        """
        for channel, queues in self.chan_dict.items():
            if queues[bad]:
                to_delete, queues[bad] = queues[bad], []  #fairly atomic
                while to_delete:
                    await channel.delete_messages(to_delete[:100])
                    del(to_delete[:100])
            queue, n = queues[main]
            if (num := len(queue) - n) > 0:
                to_delete, queues[main] = queues[:num], queues[num:]
                while to_delete:
                    await channel.delete_messages(to_delete[:100])
                    del(to_delete[:100])

    @deleter.before_loop
    async def load_existing(self):
        for channel, queues in self.chan_dict.items():
            queues[main] = [discord.Object(id=m.id)
                    async for m in channel.history(limit=5000)]


def setup(client: commands.Bot) -> None:
    client.add_cog(Deleter(client))
