from discord.ext.commands import Cog

import settings


class SkywareCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_message(self, msg):
        if msg.channel.id == settings.SHOWCASE_CHANNEL:
            if not (msg.author.bot or msg.webhook_id or msg.content.startswith("[INFO]")):
                await msg.delete()
                
                if not (msg.author.bot or msg.webhook_id):
                    await msg.author.send(
                        "The showcase is now closed! Please make your submission on "
                        f"www.skywa.re. Your message was deleted.\n```{msg.content}```"
                    )


def setup(bot):
    bot.add_cog(SkywareCog(bot))