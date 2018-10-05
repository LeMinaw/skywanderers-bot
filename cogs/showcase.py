import json
import re

import settings

class ShowcaseCog:
    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, msg):
        if msg.channel.id == settings.SHOWCASE_CHANNEL:
            if "[complete]" in msg.content.lower():
                await msg.author.send("`[Complete]` tags are not supposed to work. Please use a `[Completed]` tag instead.")

            if not any(pre in msg.content.lower() for pre in ("[completed]", "[wip]", "[info]")) and len(msg.attachments) == 0:
                await msg.delete()
                if not msg.author.bot:
                    await msg.author.send(f"You can only submit files or prefixed messages on #showcase. Your message was deleted :(.\n```{msg.content}```")
            elif any(pre in msg.content.lower() for pre in ("[completed]", "[wip]")):
                await msg.add_reaction("\u2795")


    async def on_socket_raw_receive(self, payload):
        try:
            event = json.loads(payload)
        except UnicodeDecodeError:
            return

        if (event['t'] == "MESSAGE_REACTION_ADD"
                and event['d']['channel_id'] == settings.SHOWCASE_CHANNEL
                and event['d']['emoji']['name'] == "\u2795"):

            chan = self.bot.get_channel(settings.SHOWCASE_CHANNEL)
            msg  = await chan.get_message(event['d']['message_id'])

            for reac in msg.reactions:
                if reac.emoji == "\u2795":
                    reac_nb = reac.count
                    break

            if not msg.pinned and reac_nb >= settings.REACTIONS_THRESHOLD:
                await msg.pin()
                guild = self.bot.get_guild(event['d']['guild_id'])
                main_chan = guild.get_channel(settings.MAIN_CHANNEL)
                await main_chan.send("A publication just reached %s reactions in %s! Congratulations, %s." % (
                    settings.REACTIONS_THRESHOLD,
                    chan.mention,
                    msg.author.mention
                ))


def setup(bot):
    bot.add_cog(ShowcaseCog(bot))
