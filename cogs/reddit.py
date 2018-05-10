from discord     import Embed, Colour
import requests
import asyncio
import json

import settings


def get_new_posts(subreddit_url, posts_nb=5):
    """Returns a dict of the last <posts_nb> new posts in the <subreddit_url> subreddit."""
    url = "http://www.reddit.com/r/%s/new.json?sort=new&limit=%s"
    url = url % (subreddit_url, posts_nb)
    data = None
    try:
        data = requests.get(url).json()['data']['children']
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        print("Failed to sync with Reddit servers.")
    return data


class RedditCog:
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.check_subreddit())


    async def check_subreddit(delay=60):
        await self.bot.wait_until_ready()
        reddit_chan = self.bot.get_channel(settings.REDDIT_CHANNEL)

        last_post = None
        while not self.bot.is_closed:
            await asyncio.sleep(delay)

            if last_post is None:
                new_posts = get_new_posts(settings.SUBREDDIT_URL, 1)
                if new_posts is not None:
                    last_post = new_posts[0]

            else:
                new_posts = get_new_posts(settings.SUBREDDIT_URL, 5)
                if new_posts is None:
                    continue
                for post in reversed(new_posts):
                    if post['data']['created_utc'] > last_post['data']['created_utc']:
                        embed = Embed(
                            type = 'rich',
                            colour = Colour.green(),
                            title       = post['data']['title'],
                            url         = post['data']['url'],
                            timestamp   = datetime.fromtimestamp(int(post['data']['created_utc'])),
                            description = post['data']['selftext'],
                        )
                        embed.set_author(
                            name=post['data']['author'],
                            url="https://www.reddit.com/user/%s" % post['data']['author']
                        )
                        embed.set_footer(
                            text="New reddit post",
                            icon_url="https://upload.wikimedia.org/wikipedia/fr/f/fc/Reddit-alien.png"
                        )
                        await reddit_chan.send(embed=embed)
                        last_post = post


def setup(bot):
    bot.add_cog(RedditCog(bot))
