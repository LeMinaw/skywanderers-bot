import asyncio
from time import time
from discord import Embed, Member, Colour
from discord.ext.commands import Cog, command

import settings
from utils import RedisDict

class MuteCog(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mutes = RedisDict(redis=self.bot.redis, redis_key='mutes')
        self.bot.loop.create_task(self.check_mutes())

    @Cog.listener()
    async def on_ready(self):
        if settings.RESET_MUTES_ON_LOAD:
            self.mutes.save()
            print("Data reinit done.")
        try:
            self.mutes.load()
            print("Data loading sucessful.")
        except NameError:
            print("Error occured while loading data. Attempting to reinit.")
            self.mutes.save()
            print("Data reinit done.")


    @command(name='mute')
    async def mute(self, ctx, user: Member, dur: int=None):
        if ctx.author.permissions_in(ctx.channel).kick_members:
            if user is not None:
                self.mutes.load()
                if user.id in self.mutes.data and dur is None:
                    del self.mutes.data[user.id]
                    muted = False
                else:
                    end_time = time() + 60*dur if dur is not None else -1
                    self.mutes.data[user.id] = end_time
                    muted = True
                self.mutes.save()

                action = "muted" if muted else "unmuted"
                duration = f"for {dur}m" if dur is not None else "forever"

                log_chan = ctx.guild.get_channel(settings.LOG_CHANNEL)
                await log_chan.send(embed=Embed(
                    title = "MUTING",
                    description = "**{usr} has been {act} by {ath} ({dur})**".format(
                        usr = user.mention,
                        act = action,
                        ath = ctx.author.mention,
                        dur = duration
                    ),
                    type = 'rich',
                    colour = Colour.orange()
                ))
                await user.send(embed=Embed(
                    title = "You have been {act} from Skywanderers' discord server {dur}.".format(
                        act=action,
                        dur=duration
                    ),
                    type = 'rich',
                    colour = Colour.orange()
                ))
            else:
                await ctx.author.send(f"Can't mute `{user}`: member not found.")
        else:
            await ctx.author.send("You are not allowed to mute people in this channel.")


    async def on_message(self, msg):
        self.mutes.load()
        if msg.author.id in self.mutes.data:
            await msg.delete()
            await msg.author.send(f"You're currently muted. Your message was deleted :(.\n```{msg.content}```")
        # await self.bot.process_commands(msg) # Prevents commands API freeze


    async def check_mutes(self, delay=20):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            await asyncio.sleep(delay)
            print("Loading mutes...")
            self.mutes.load()
            # Copy ids in a list because we'll change dict size during iteration
            user_ids = list(self.mutes.data.keys())
            for user_id in user_ids:
                end_time = self.mutes.data[user_id]
                print(f"uid:{user_id} end:{end_time}")
                if time() > end_time > 0:
                    del self.mutes.data[user_id]
                    self.mutes.save()

                    user = self.bot.get_user(user_id)
                    log_chan = self.bot.get_channel(settings.LOG_CHANNEL)
                    await log_chan.send(embed=Embed(
                        title = "MUTING",
                        description = f"**{user.mention} has been unmuted (time elapsed)**",
                        type = 'rich',
                        colour = Colour.orange()
                    ))
                    await user.send(embed=Embed(
                        title = "You have been unmuted from Skywanderers' discord server.",
                        description = "Welcome back!",
                        type = 'rich',
                        colour = Colour.orange()
                    ))

def setup(bot):
    bot.add_cog(MuteCog(bot))
