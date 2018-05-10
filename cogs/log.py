from discord import Embed, Colour

import settings

class LogCog:
    def __init__(self, bot):
        self.bot = bot
        self.nologs_chans = settings.DONT_LOG + [settings.LOG_CHANNEL]

    async def on_ready(self):
        self.chan = self.bot.get_channel(settings.LOG_CHANNEL)

    async def on_message_delete(self, msg):
        if msg.channel.id not in self.nologs_chans:
            embed = Embed(
                title = "DELETION",
                type = 'rich',
                description = f"**In #{msg.channel.name}, message by {msg.author.name}.**",
                colour = Colour.red()
            )
            embed.add_field(name="Old content", value=msg.content)
            await self.chan.send(embed=embed)

    async def on_message_edit(self, msg_before, msg_after):
        if msg_before.channel.id not in self.nologs_chans and msg_before.content != msg_after.content:
            embed = Embed(
                title = "EDITION",
                type = 'rich',
                description = "**In #{msg.channel.name}, message by {msg.author.name}.**".format(msg=msg_before),
                colour = Colour.blue()
            )
            embed.add_field(name="Old content", value=msg_before.content)
            embed.add_field(name="New content", value=msg_after.content)
            await self.chan.send(embed=embed)

    async def on_member_ban(self, member):
        await self.chan.send(embed=Embed(
            title = "BANNING",
            type = 'rich',
            description = f"**{member} was banned from the server.**",
            colour = Colour.red()
        ))

    async def on_member_unban(self, ember):
        await self.chan.send(embed=Embed(
            title = "UNBANNING",
            type = 'rich',
            description = f"**{member} was unbanned from the server.**",
            colour = Colour.green()
        ))

def setup(bot):
    bot.add_cog(LogCog(bot))
