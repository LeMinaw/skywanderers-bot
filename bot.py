from discord        import Client, Game, Embed, Colour, Object
from collections    import OrderedDict
from datetime       import datetime
from random         import choice, randint
from os             import getenv
import requests
import asyncio
import json
import re


DISCORD_TOKEN = getenv('DISCORD_TOKEN')
WATCH_CHANNELS_IDS = [
    "241014195884130315",
    "342383722185883648",
    "271723356795961345",
    "281178410917822474",
    "352907720975843329",
    "271382095383887872",
    "358061597580722199",
    "283816917368832000",
    "317360477292331011",
    "291336725589000204"
]
LOG_CHANNEL_ID    = "361282322303156224"
MAIN_CHANNEL_ID   = "241014195884130315"
RULES_CHANNEL_ID  = "275053802615209986"
REDDIT_CHANNEL_ID = "362107240963899395"
SUBREDDIT_URL = "skywanderers"
SUBREDDIT_REFRESH = 30 # Seconds


# class RedditEmbed(Embed):
#     def __init__(self, post_data):
#         super()
#         type = 'rich',
#         colour = Colour.green(),
#         title       = post['data']['title'],
#         url         = post['data']['url'],
#         timestamp   = datetime.fromtimestamp(int(post['data']['created_utc'])),
#         description = post['data']['selftext'],
#     )


def get_new_posts(subreddit_url, posts_nb=5):
    """Returns a dict of the last <posts_nb> new posts in the <subreddit_url> subreddit."""
    url = "http://www.reddit.com/r/%s/new.json?sort=new&limit=%s" % (subreddit_url, posts_nb)
    data = None
    try:
        data = requests.get(url).json()['data']['children']
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as e:
        print("Failed to get new posts.")
    return data


async def check_subreddit(delay=60):
    await client.wait_until_ready()
    for i in range(5): # 5 Tries
        new_posts = get_new_posts(SUBREDDIT_URL, 1)
        if new_posts is not None:
            last_post = new_posts[0]
            break
        await asyncio.sleep(10)

    while not client.is_closed:
        new_posts = get_new_posts(SUBREDDIT_URL, 5)

        if new_posts is not None:
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
                    embed.set_author(name=post['data']['author'], url="https://www.reddit.com/user/%s" % post['data']['author'])
                    embed.set_footer(text="New reddit post", icon_url="https://upload.wikimedia.org/wikipedia/fr/f/fc/Reddit-alien.png")
                    await client.send_message(reddit_channel, embed=embed)

                    last_post = post

        await asyncio.sleep(delay)


client = Client()
log_channel     = Object(id=LOG_CHANNEL_ID)
main_channel    = Object(id=MAIN_CHANNEL_ID)
reddit_channel  = Object(id=REDDIT_CHANNEL_ID)


@client.event
async def on_message(msg):
    if msg.content.startswith('!kick'):
        if msg.author.permissions_in(msg.channel).kick_members:
            if re.match(r'^!kick <@(\d+)>$', msg.content):
                user_id = re.search(r'^!kick <@(\d+)>$', msg.content).group(1)
                user = msg.server.get_member(user_id)

                await client.kick(user)

                embed = Embed(
                    title = "KICKING",
                    type = 'rich',
                    description = "**{user} has been kicked from the server.**".format(user=user),
                    colour = Colour.orange()
                )
                await client.send_message(log_channel, embed=embed)

                embed = Embed(
                    title = "{user} has been kicked from the server.".format(user=user.name),
                    type = 'rich',
                    colour = Colour.orange()
                )
                await client.send_message(main_channel, embed=embed)
            else:
                await client.send_message(msg.author, "Bad syntax: `!kick @member` should work.")
        else:
            await client.send_message(msg.author, "You are not allowed to kick people in this channel.")

    elif msg.content.startswith('!redeem'):
        if re.match(r'^!redeem (\S+)$', msg.content):
            pass # TODO: VALIDATES ACCOUNT
        else:
            await client.send_message(msg.author, "Bad syntax: `!redeem my_activation_code` should work.")

    elif msg.content.startswith('!info'):
        embed = Embed(
            type = 'rich',
            colour = Colour.orange(),
            title = "SKYWANDERER'S MAIN GUIDANCE COMPUTER",
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/279940382656167936/361678736422076418/comp.png")
        embed.add_field(name="Commands handbook", value="!info\n!kick @member\n!redeem activationKey")
        embed.add_field(name="Subsystems status", value="[UP] Reddit tracking\n[UP] Chat logging\n[UP] Welcome and goodbye\n[UP] Cool easter eggs")
        embed.set_footer(text="Main guidance computer crafted by LeMinaw corp. ltd", icon_url="https://cdn.discordapp.com/avatars/201484914686689280/b6a28b98e51f482052e42009fed8c6c4.png?size=256")
        await client.send_message(msg.channel, embed=embed)

    elif not msg.author.bot and any(w in msg.content.lower() for w in ("skywanderers", "sky1", "sky wanderers")):
        response = await client.send_message(msg.channel, "Err: Skywanderers pre-aplha: not found :'(")
        await asyncio.sleep(2)
        await client.delete_message(response)

    if "<@!%s>" % client.user.id in msg.content:
        sounds = ("beep", "bip", "bzz", "bop", "bup", "bzzz")
        sounds_nb = randint(1, 4)
        response = ''
        for i in range(sounds_nb):
            if i == sounds_nb - 1:
                sep = "."
            else:
                sep = ", "
            response += "%s%s" % (choice(sounds), sep)
        await client.send_message(msg.channel, response)


@client.event
async def on_message_delete(msg):
    if msg.channel.id in WATCH_CHANNELS_IDS:
        embed = Embed(
            title = "DELETION",
            type = 'rich',
            description = "**In #{msg.channel.name}, message by {msg.author.name}.**".format(msg=msg),
            colour = Colour.red()
        )
        embed.add_field(name="Old content", value=msg.content)
        await client.send_message(log_channel, embed=embed)


@client.event
async def on_message_edit(msg_before, msg_after):
    if msg_before.channel.id in WATCH_CHANNELS_IDS and msg_before.content != msg_after.content:
        embed = Embed(
            title = "EDITION",
            type = 'rich',
            description = "**In #{msg.channel.name}, message by {msg.author.name}.**".format(msg=msg_before),
            colour = Colour.blue()
        )
        embed.add_field(name="Old content", value=msg_before.content)
        embed.add_field(name="New content", value=msg_after.content)
        await client.send_message(log_channel, embed=embed)


@client.event
async def on_member_ban(member):
    embed = Embed(
        title = "BANNING",
        type = 'rich',
        description = "**{user} was banned from the server.**".format(user=member),
        colour = Colour.red()
    )
    await client.send_message(log_channel, embed=embed)

    embed = Embed(
        title = "{user} was banned from the server.".format(user=member.name),
        type = 'rich',
        colour = Colour.red()
    )
    await client.send_message(main_channel, embed=embed)


@client.event
async def on_member_unban(member):
    embed = Embed(
        title = "UNBANNING",
        type = 'rich',
        description = "**{user} was unbanned from the server.**".format(user=member),
        colour = Colour.green()
    )
    await client.send_message(log_channel, embed=embed)

    embed = Embed(
        title = "{user} was unbanned from the server".format(user=member.name),
        type = 'rich',
        colour = Colour.green()
    )
    await client.send_message(main_channel, embed=embed)


@client.event
async def on_member_join(member):
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
    ]) + "By the way, be sure to have a quick look at {rules}."
    rules_channel = client.get_channel(RULES_CHANNEL_ID)
    await client.send_message(main_channel, txt.format(user=member.mention, rules=rules_channel.mention))


@client.event
async def on_member_remove(member):
    msg = "Bye bye, {mention}. " + choice([
        "We will *not* remember you.",
        "Have peace wandering among the stars <3",
        "It's been fun. Don't come back.",
    ])
    await client.send_message(main_channel, msg.format(mention=member.mention))


@client.event
async def on_ready():
    print("Logged in as {user.name} ({user.id}).".format(user=client.user))
    await client.change_presence(game=Game(name="Skywanderers"))


client.loop.create_task(check_subreddit(SUBREDDIT_REFRESH))
client.run(DISCORD_TOKEN)
