from discord import utils
from discord.ext import commands
from hashlib     import sha256
import psycopg2
import sys

from utils import make_dict, OpenCursor
import settings

class RedeemCog:
    def __init__(self, bot):
        self.bot = bot
        self.db = psycopg2.connect(**settings.DATABASE)

    @commands.command(name='redeem')
    async def redeem(self, ctx, key: str):
        key = key.encode('utf-8')
        key = sha256(key).hexdigest()

        with OpenCursor(self.db) as cur:
            cur.execute("SELECT code, active_disc, rank FROM register_activationcode")
            db_keys = make_dict(cur.fetchall())
            try:
                db_key = db_keys[key]
                if db_key[0]:
                    usr_id = ctx.author.id
                    usr_name = ctx.author.name
                    cur.execute("SELECT * FROM register_discordmember WHERE user_id = %s", (usr_id,))
                    db_usr = cur.fetchone()
                    if db_usr is None:
                        rank_id = db_key[1]
                        try:
                            role = utils.get(ctx.guild.roles, name=settings.ROLES[rank_id])
                            await ctx.author.add_roles(role)
                            cur.execute("INSERT INTO register_discordmember (username, user_id, user_rank) VALUES (%s, %s, %s)", (usr_name, usr_id, rank_id))
                            cur.execute("UPDATE register_activationcode SET active_disc = FALSE WHERE code = %s", (key,))
                            self.db.commit()

                            main_chan = ctx.guild.get_channel(settings.MAIN_CHANNEL)
                            await main_chan.send(f"{ctx.author.mention} is now {role.mention}! Thanks for supporting us!")
                        except:
                            print(sys.exc_info())
                            await ctx.author.send("Error: Something weird occured. Please contact a moderator.")
                    else:
                        await ctx.author.send("Error: This user already used an activation code.")
                else:
                    await ctx.author.send("Error: This code has already been used on discord.")
            except KeyError:
                await ctx.author.send("Error: This code seems invalid.")


def setup(bot):
    bot.add_cog(RedeemCog(bot))
