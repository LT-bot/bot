from discord.ext import commands, tasks
import discord
from string import punctuation
from collections import deque
import re
from configparser import ConfigParser
import logging 
from datetime import datetime, timedelta

logger = logging.getLogger('lt2b2')
conf = ConfigParser()
conf.read("main.conf")

#list of lists, [[channel id, max messages], ]
channel_list = [ch.split() for ch in conf['Deleter']['channel settings'].split(',')]
bad_words = conf['Deleter']['bad words'].split()
bad_replace = conf['Deleter']['bad replace']
re_bad = re.compile('|'.join([re.escape(word) for word in bad_words]), re.I)
bad, main, limit = 0, 1, 2
interval = int(conf['Deleter']['interval'])

class Deleter(commands.Cog):
    def __init__(self, Bot: commands.Bot) -> None:
        """
        Use dict of channels with deque for rolling delete, and lists otherwise 
        and max number of messages.
        """
        logger.info('Deleter init.')
        self.Bot = Bot
        self.as_webhook = Bot.as_webhook
        self.chan_dict = {}
        for chan_id, n in channel_list:
            self.chan_dict[Bot.get_channel(int(chan_id))] = {bad: [], main: [], limit: int(n)}
        logger.info(f'Working on the following channels:\n{self.chan_dict}')
        self.deleter.start()


    @commands.command(name='bad_replace', aliases=['br'])
    async def _bad_replace(self, context: commands.Context, new_word: str='***') -> None:
        conf['Deleter']['bad replace'] = new_word
        with open('main.conf', 'w') as f:
            conf.write(f)
        bad_replace = new_word

    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """
        Add messages to the corresponding queues
        """
        try:
            queues = self.chan_dict[message.channel]
            obj = discord.Object(id=message.id)
            if (text := re_bad.sub(bad_replace, message.content)) != message.content:
                logger.info(f'Bad message:\n{message.content}')
                await self.as_webhook(
                        message = text,
                        channel = message.channel,
                        avatar_url = message.author.avatar_url,
                        name = message.author.nick or message.author.name,
                        attachments = [await att.to_file() for att in message.attachments]
                        )
                await message.delete()
                #queues[bad].append(obj)
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
        for channel, queues in self.chan_dict.items():
            logger.info(f'Running deletion for {str(channel)}')
            pinned = [discord.Object(id=m.id) for m in await channel.pins()]
            logger.info(f'Found {len(pinned)} pins.') #:\n{pinned}')
            for m in pinned:
                try:
                    queues[main].remove(m)
                except ValueError:
                    #logger.info(f'Pinned message {m} already excluded.')
                    pass

            if queues[bad]:
                to_delete, queues[bad] = queues[bad], []  #fairly atomic
                logger.info(f'Trying to delete {len(to_delete)} messages bad.')
                try:
                    for _ in range(-(-len(to_delete)//100)):
                        await channel.delete_messages(to_delete[:100])
                        del(to_delete[:100])
                except Exception as e:
                    logger.info(f'Exception caught, bad:\n{e}')
                    #queues[bad] = to_delete + queues[bad]

            queue, n = queues[main], queues[limit]
            if (num := len(queue) - n) > 0:
                to_delete, queues[main] = queues[main][:num], queues[main][num:]
                logger.info(f'Trying to delete {len(to_delete)} messages in {str(channel)}, main.')
                try:
                    for _ in range(-(-len(to_delete)//100)):
                        await channel.delete_messages(to_delete[:100])
                        del(to_delete[:100])
                except Exception as e:
                    logger.info(f'Exception caught, main.\n{e}')
                    #queues[main] = to_delete + queues[main]

    @deleter.before_loop
    async def load_existing(self):
        bulk_limit = datetime.now() - timedelta(days=14)
        for channel, queues in self.chan_dict.items():
            logger.info(f'Fetching messages from f{str(channel)}')
            queues[main] = [discord.Object(id=m.id)
                    async for m in channel.history(limit=10000, oldest_first=True, 
                        after=bulk_limit)]
            # Take care of older messages too (i.e. unpinned)
            pinned_ids = {m.id for m in await channel.pins()}
            async for message in channel.history(limit=20, oldest_first=True, 
                    before=bulk_limit):
                if not message.id in pinned_ids:
                    try:
                        await message.delete()
                    except:
                        pass


def setup(client: commands.Bot) -> None:
    client.add_cog(Deleter(client))
