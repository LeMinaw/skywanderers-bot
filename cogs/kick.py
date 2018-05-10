from discord     import Embed, Member, Colour
from discord.ext import commands

import settings

class KickCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='kick')
    async def kick(self, ctx, user: Member):
        if ctx.author.permissions_in(ctx.channel).kick_members:
            if user is not None:
                await user.kick()

                embed = Embed(
                    title = "KICKING",
                    type = 'rich',
                    description = f"**{user} has been kicked from the server.**",
                    colour = Colour.orange()
                )
                log_chan = ctx.guild.get_channel(settings.LOG_CHANNEL)
                await log_chan.send(embed=embed)

            else:
                await ctx.send(f"Can't kick `{user}`: member not found.")
        else:
            await ctx.send("You are not allowed to kick people in this channel.")

def setup(bot):
    bot.add_cog(KickCog(bot))
