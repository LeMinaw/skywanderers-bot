import re
from random import randint, choice
from discord import Embed, Colour
from discord.ext.commands import command, Cog

class FunCog(Cog):
    sounds = ("beep", "bip", "bzz", "bop", "bup", "bzzz")
    answers = ("Yes", "Sure", "No way", "Never", "Yup", "Nope")

    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_message(self, msg):
        if self.bot.user.mentioned_in(msg) and not msg.mention_everyone:
            if "should" in msg.content.lower():
                response = choice(self.answers) + '.'

            else:
                sounds_nb = randint(1, 4)
                response = ''
                for i in range(sounds_nb):
                    if i + 1 == sounds_nb:
                        sep = "."
                    else:
                        sep = ", "
                    response += choice(self.sounds) + sep

            await msg.channel.send(response)

        if re.match(r"(?:\W|^)wew(?:\W|$)", msg.content, flags=re.I):
            embed = Embed(type='rich', colour=Colour.blue())
            embed.set_image(url="https://cdn.discordapp.com/attachments/241022918807519232/359170809001934848/seal_wew.png")
            await msg.channel.send(embed=embed)


def setup(bot):
    bot.add_cog(FunCog(bot))
