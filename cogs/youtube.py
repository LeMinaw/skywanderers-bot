from discord  import Embed, Colour
from discord.ext.commands import Cog
from datetime import datetime
import httpx
import asyncio
import json
import dateutil

import settings


class YoutubeCog(Cog):
    def __init__(self, bot):
        self._playlist_id = None
        self._discord_channel = None
        self.bot = bot
        self.bot.loop.create_task(self.check_playlist())
    

    @property
    async def playlist_id(self):
        if not self._playlist_id:
            async with httpx.AsyncClient() as client:
                r = await client.get(
                    'https://www.googleapis.com/youtube/v3/channels',
                    params = {
                        'key': settings.YOUTUBE_API_KEY,
                        'part': 'contentDetails',
                        'id': settings.YOUTUBE_CHANNEL_ID
                    }
                )
           
            if r.status_code == httpx.codes.OK:
                self._playlist_id = r.json()['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            else:
                print("Failed to get Youtube playlist id.")
        
        return self._playlist_id
    

    @property
    async def discord_channel(self):
        if not self._discord_channel:
            await self.bot.wait_until_ready()
            self._discord_channel = self.bot.get_channel(settings.MAIN_CHANNEL)
        
        return self._discord_channel


    async def get_playlist_vids(self, limit=5):
        async with httpx.AsyncClient() as client:
            r = await client.get(
                'https://www.googleapis.com/youtube/v3/playlistItems',
                params = {
                    'key': settings.YOUTUBE_API_KEY,
                    'part': 'snippet',
                    'playlistId': self.playlist_id,
                    'maxResults': limit
                }
            )
        
        if r.status_code == httpx.codes.OK:
            return r.json()['items']
        
        print("Failed to get Youtube playlist videos.")
        return ()
    

    video_url = lambda self, id: f'https://www.youtube.com/watch?v={id}'

    channel_url = lambda self, id: f'https://www.youtube.com/channel/{id}'
        

    async def check_playlist(self, delay=60):
        last_vid_dt = None
        while not self.bot.is_closed:
            await asyncio.sleep(delay)

            if not last_vid_dt:
                try:
                    last_vid = await self.get_playlist_vids(limit=1)[0]
                except IndexError:
                    continue
                last_vid_dt = dateutil.parser.parse(last_vid['snippet']['publishedAt'])

            else:
                last_vids = await self.get_playlist_vids()
                
                for vid in reversed(last_vids):
                    vid = vid['snippet']
                    
                    vid_dt = dateutil.parser.parse(vid['publishedAt'])
                    if vid_dt > last_vid_dt:
                        embed = Embed(
                            type = 'rich',
                            colour = Colour.green(),
                            title = vid['title'],
                            url = self.video_url(vid['resourceId']['videoId']),
                            timestamp = vid_dt,
                            description = vid['description'],
                        )
                        embed.set_image(
                            url = vid['thumbnails']['high']['url']
                        )
                        embed.set_author(
                            name = vid['channelTitle'],
                            url = self.channel_url(vid['channelId'])
                        )
                        embed.set_footer(
                            text = "New Youtube video!",
                            icon_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/YouTube_icon.png/320px-YouTube_icon.png"
                        )
                        
                        await self.discord_channel.send(embed=embed)
                        last_vid = vid


def setup(bot):
    bot.add_cog(YoutubeCog(bot))
