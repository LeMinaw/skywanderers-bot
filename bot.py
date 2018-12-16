from discord     import Game, Embed, Colour
from discord.ext import commands
from random      import choice
import redis
import sys

import settings

bot = commands.Bot(command_prefix='!', description="Skywanderers' main guidance computer")
bot.redis = redis.from_url(settings.REDIS_URL)


@bot.command(name='info', aliases=['mgc'])
async def info(ctx):
    embed = Embed(
        type = 'rich',
        colour = Colour.orange(),
        title = "SKYWANDERERS' MAIN GUIDANCE COMPUTER",
    )
    embed.set_image(url="https://cdn.discordapp.com/attachments/279940382656167936/361678736422076418/comp.png")
    embed.add_field(name="Commands handbook", value=
            "!info or !mgc"
            "\n!capcom"
            "\n!redeem activationKey"
            "\n!kick @member"
            "\n!mute @member"
            "\n!mute @member minutes")
    embed.add_field(name="Subsystems status", value=
            "[OFF] Reddit tracking"
            "\n[ON] Twitch tracking"
            "\n[ON] Chat logging"
            "\n[ON] Welcome and goodbye"
            "\n[ON] Automated redeem"
            "\n[OFF] Showcase management"
            "\n[ON] Skywa.re integration"
            "\n[ON] Moderation tools"
            "\n[ON] Cool easter eggs")
    embed.set_footer(
        text="Main guidance computer crafted by LeMinaw corp. ltd",
        icon_url="https://cdn.discordapp.com/avatars/201484914686689280/b6a28b98e51f482052e42009fed8c6c4.png"
    )
    await ctx.send(embed=embed)


@bot.event
async def on_member_join(member):
    main_chan  = bot.get_channel(settings.MAIN_CHANNEL)
    rules_chan = bot.get_channel(settings.RULES_CHANNEL)
    faq_chan   = bot.get_channel(settings.FAQ_CHANNEL)
    txt = choice([
        "Welcome on board, {user}! ",
        "Say hello to {user}, our new sky wanderer! ",
        "Be nice with our new recuit, {user}. ",
        "Hey guys, looks like {user} is with us from now! ",
    ]) + choice([
        "Pray for Tsunamayo, our only god up there. ",
        "Be careful. Mind the frog. ",
        "Warning! This server is lava. ",
        "May the force be with you. ",
    ]) + "By the way, be sure to have a quick look at {rules} and {faq}."
    await main_chan.send(txt.format(
        user=member.mention, rules=rules_chan.mention, faq=faq_chan.mention))


@bot.event
async def on_member_remove(member):
    main_chan  = bot.get_channel(settings.MAIN_CHANNEL)
    txt = "Bye bye, {mention}. " + choice([
        "Just go.",
        "Have peace wandering among the stars <3",
        "It's been fun. Don't come back.",
    ])
    await main_chan.send(txt.format(mention=member.name))


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id}).")
    await bot.change_presence(activity=Game(name="Skywanderers"))


if __name__ == '__main__':
    for extension in settings.EXTENSIONS:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f"Failed to load extension {extension}.")
            print(sys.exc_info())

    bot.run(settings.DISCORD_TOKEN)
