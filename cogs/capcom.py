from discord     import Embed, Colour
from discord.ext import commands
from random      import randint
import re

import settings

class CapcomCog:
    def __init__(self, bot):
        self.bot = bot

        # Computing A11 quotes
        with open("a11.txt", 'rt') as script_file:
            script = script_file.read()
        pattern = re.compile(r'\n\n.+\n.+\n\n', re.MULTILINE)
        self.quotes = pattern.findall(script)


    @commands.command(name='capcom')
    async def capcom(self, ctx):
        quote = self.quotes[randint(1, len(self.quotes) - 1)]
        quote = [s for s in quote.split('\n') if s]

        embed = Embed(
            type = 'rich',
            colour = Colour.blue(),
            title = "Out-of-context Apollo 11 transcript",
            description = quote[1]
        )
        embed.set_footer(text=quote[0])
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(CapcomCog(bot))
