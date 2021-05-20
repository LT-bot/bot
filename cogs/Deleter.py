from discord.ext import commands, tasks
import discord
from string import punctuation
from collections import deque
import re
from configparser import ConfigParser
import logging 

logger = logging.getLogger('lt2b2')
conf = ConfigParser()
conf.read("main.conf")

#list of lists, [[channel id, max messages], ]
channel_list = [ch.split() for ch in conf['Deleter']['channel settings'].split(',')]
bad_words = conf['Deleter']['bad words'].split()
re_bad = re.compile('|'.join([re.escape(word) for word in bad_words]), re.I)
bad, main, limit = 0, 1, 2
interval = int(conf['Deleter']['interval'])

class Deleter(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        """
        Use dict of channels with deque for rolling delete, and lists otherwise 
        and max number of messages.
        """
        logger.info('Deleter init.')
        self.client = client
        self.chan_dict = {}
        for chan_id, n in channel_list:
            self.chan_dict[client.get_channel(int(chan_id))] = {bad: [], main: [], limit: int(n)}
        logger.info(f'Working on the following channels:\n{self.chan_dict}')
        self.deleter.start()
    
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
                logger.info(f'Bad message:\n{message.content}.')
            else:
                queues[main].append(obj)
        except KeyError:
            pass
        except discord.HTTPException:
            pass
        except discord.NotFound:
            pass
    
    @tasks.loop(minutes=interval)
    async def deleter(self):
        """
        Runs every interval minutes and deletes from the queues.
        """
        logger.info('Running deletion...')
        for channel, queues in self.chan_dict.items():
            pinned = [discord.Object(id=m.id) for m in await channel.pins()]
            logger.info(f'Found {len(pinned)} pins:\n{pinned}')
            for m in pinned:
                try:
                    queues[main].remove(m)
                except ValueError:
                    #logger.info(f'Pinned message {m} already excluded.')
                    pass

            if queues[bad]:
                to_delete, queues[bad] = queues[bad], []  #fairly atomic
                logger.info(f'Trying to delete {len(to_delete)} messages in {str(channel)}, bad.')
                try:
                    for _ in range(-(-len(to_delete)//100)):
                        await channel.delete_messages(to_delete[:100])
                        del(to_delete[:100])
                except:
                    logger.info('Exception caught, bad')
                    #queues[bad] = to_delete + queues[bad]

            queue, n = queues[main], queues[limit]
            if (num := len(queue) - n) > 0:
                to_delete, queues[main] = queues[main][:num], queues[main][num:]
                logger.info(f'Trying to delete {len(to_delete)} messages in {str(channel)}, main.')
                try:
                    for _ in range(-(-len(to_delete)//100)):
                        await channel.delete_messages(to_delete[:100])
                        del(to_delete[:100])
                except:
                    logger.info('Exception caught, main.')
                    #queues[main] = to_delete + queues[main]

    @deleter.before_loop
    async def load_existing(self):
        for channel, queues in self.chan_dict.items():
            logger.info(f'Fetching messages from f{str(channel)}')
            queues[main] = [discord.Object(id=m.id)
                    async for m in channel.history(limit=5000, oldest_first=True)]


def setup(client: commands.Bot) -> None:
    client.add_cog(Deleter(client))
