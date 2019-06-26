import asyncio
from discord import Embed, Colour
from discord.ext.commands import Cog
from twitch import TwitchClient

import settings

class TwitchCog(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tw_client = TwitchClient(settings.TWITCH_CLIENT_ID)

        self.bot.loop.create_task(self.check_streams())


    async def check_streams(self, delay=20):
        await self.bot.wait_until_ready()
        main_chan    = self.bot.get_channel(settings.MAIN_CHANNEL)
        streams_chan = self.bot.get_channel(settings.STREAMS_CHANNEL)

        last_ids = []
        while not self.bot.is_closed():
            print("Checking streams...")
            streams = self.tw_client.streams.get_live_streams(game="Skywanderers")
            for stream in streams:
                if stream['id'] not in last_ids:
                    embed = Embed(
                        type = 'rich',
                        colour = Colour.purple(),
                        title       = stream['channel']['status'],
                        url         = stream['channel']['url'],
                        timestamp   = stream['created_at'],
                        description = stream['channel']['description'],
                    )
                    embed.set_image(url=stream['preview']['large'])
                    embed.set_author(
                        name = "{0} [{1}]".format(
                            stream['channel']['display_name'],
                            stream['channel']['language']
                        ),
                        url  =     stream['channel']['url'],
                        icon_url = stream['channel']['logo']
                    )
                    embed.set_footer(
                        text     = "Looks like someone is streaming some Skywanderers!",
                        icon_url = "https://image.noelshack.com/fichiers/2018/13/1/1522018829-twitch.png"
                    )
                    await streams_chan.send(embed=embed)
                    # await client.send_message(streams_channel, stream['channel']['url'])
                    await main_chan.send(f"Looks like someone is streaming some Skywanderers :eyes: Check out {streams_chan.mention}!")

                    last_ids.append(stream['id'])

            await asyncio.sleep(delay)


def setup(bot):
    bot.add_cog(TwitchCog(bot))
