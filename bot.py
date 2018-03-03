from discord     import Client, Game, Embed, Colour, Object, utils
from collections import OrderedDict
from datetime    import datetime
from random      import choice, randint
from hashlib     import sha256
from redis       import from_url, StrictRedis
from time        import time
from os          import getenv
import requests
import psycopg2
import asyncio
import pickle
import json
import sys
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
LOG_CHANNEL_ID      = "361282322303156224"
MAIN_CHANNEL_ID     = "241014195884130315"
RULES_CHANNEL_ID    = "275053802615209986"
REDDIT_CHANNEL_ID   = "362107240963899395"
SHOWCASE_CHANNEL_ID = "281178410917822474"
SUBREDDIT_URL = "skywanderers"
SUBREDDIT_REFRESH = 20 # Seconds
DATABASE = {
    "dbname": "d9um5ikkkmm463",
    "user": "fukkkitgsohzeo",
    "password": getenv('DB_PWD'),
    "host": "ec2-184-73-199-72.compute-1.amazonaws.com",
    "port": 5432
}
REDIS_URL = getenv('REDIS_URL')
ROLES = {
    11:"Supporter",
    12:"Pioneer",
    13:"Explorer",
    14:"Entrepreneur",
    15:"Pirate",
    16:"Corporate Mogul",
    17:"Adventurer",
    18:"Pirate Lord",
    19:"Legendary Pirate Lord",
    20:"Legendary Pirate King",
}
REACTIONS_THRESHOLD = 20
RESET_MUTES_ON_LOAD = False


try:
    from localsettings import *
except ImportError:
    print("Using production settings from env vars.")


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


class OpenCursor:
    """Cursor context manager"""
    def __init__(self, db):
        self.db = db
    def __enter__(self):
        self.cursor = self.db.cursor()
        return self.cursor
    def __exit__(self, type, value, traceback):
        self.cursor.close()


class RedisDict:
    def __init__(self, redis, redis_key, data={}):
        if type(data) is not dict:
            raise TypeError
        self.data = data
        self.redis = redis
        self.redis_key = redis_key

    def save(self):
        data = pickle.dumps(self.data)
        self.redis.set(self.redis_key, data)

    def load(self):
        data = self.redis.get(self.redis_key)
        if data is None:
            self.data = {}
        else:
            self.data = pickle.loads(data)


def make_dict(coll):
    """Makes a dict from a collection of sub-collection.
    Each first items of the collection is a key."""
    return {x[0]: tuple(x[1:]) for x in coll}


def get_new_posts(subreddit_url, posts_nb=5):
    """Returns a dict of the last <posts_nb> new posts in the <subreddit_url> subreddit."""
    url = "http://www.reddit.com/r/%s/new.json?sort=new&limit=%s"
    url = url % (subreddit_url, posts_nb)
    data = None
    try:
        data = requests.get(url).json()['data']['children']
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        print("Failed to sync with Reddit servers.")
    return data


async def check_subreddit(delay=60):
    await client.wait_until_ready()
    last_post = None

    while not client.is_closed:
        await asyncio.sleep(delay)

        if last_post is None:
            new_posts = get_new_posts(SUBREDDIT_URL, 1)
            if new_posts is not None:
                last_post = new_posts[0]

        else:
            new_posts = get_new_posts(SUBREDDIT_URL, 5)
            if new_posts is None:
                continue
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
                    embed.set_author(
                        name=post['data']['author'],
                        url="https://www.reddit.com/user/%s" % post['data']['author']
                    )
                    embed.set_footer(
                        text="New reddit post",
                        icon_url="https://upload.wikimedia.org/wikipedia/fr/f/fc/Reddit-alien.png"
                    )
                    await client.send_message(reddit_channel, embed=embed)

                    last_post = post


client = Client()
db = psycopg2.connect(**DATABASE)
redis = from_url(REDIS_URL)
mutes = RedisDict(redis=redis, redis_key='mutes')


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

    if msg.content.startswith('!mute'):
        if msg.author.server_permissions.mute_members:
            results = re.search(r'^!mute <@(\d+)>(?: (\d+))?$', msg.content)
            if results is not None:
                user_id = results.group(1)
                minutes = results.group(2)

                muted_role = utils.get(msg.author.server.roles, name='Muted')
                user = msg.server.get_member(user_id)
                muted = muted_role not in user.roles
                if muted:
                    await client.add_roles(user, muted_role)
                else:
                    await client.remove_roles(user, muted_role)

                mutes.load()
                if muted and minutes is not None:
                    mutes.data[user.id] = time() + int(minutes) * 60
                elif not muted and user.id in mutes.data:
                    del mutes.data[user.id]
                mutes.save()

                action = "muted" if muted else "unmuted"
                duration = "for %sm" % minutes if minutes is not None else "forever"
                await client.send_message(log_channel, embed=Embed(
                    title = "MUTING",
                    description = "**{usr} has been {act} by {ath} ({dur})**".format(
                        usr = user.mention,
                        act = action,
                        ath = msg.author.mention,
                        dur = duration
                    ),
                    type = 'rich',
                    colour = Colour.orange()
                ))
                await client.send_message(user, embed=Embed(
                    title = "You have been {act} from Skywanderers' discord server {dur}.".format(act=action, dur=duration),
                    type = 'rich',
                    colour = Colour.orange()
                ))
            else:
                await client.send_message(msg.author, "Bad syntax: `!mute @member` or `!mute @member 15` should work.")
        else:
            await client.send_message(msg.author, "You are not allowed to mute people in this channel.")

    elif msg.content.startswith('!redeem'):
        if re.match(r'^!redeem (\S+)$', msg.content):
            key = re.search(r'^!redeem (\S+)$', msg.content).group(1)
            key = key.encode('utf-8')
            key = sha256(key).hexdigest()

            with OpenCursor(db) as cur:
                cur.execute("SELECT code, active_disc, rank FROM register_activationcode")
                db_keys = make_dict(cur.fetchall())
                try:
                    db_key = db_keys[key]
                    if db_key[0]:
                        usr_id = msg.author.id
                        usr_name = msg.author.name
                        cur.execute("SELECT * FROM register_discordmember WHERE user_id = %s", (usr_id,))
                        db_usr = cur.fetchone()
                        if db_usr is None:
                            rank_id = db_key[1]
                            try:
                                role = utils.get(msg.server.roles, name=ROLES[rank_id])
                                await client.add_roles(msg.author, role)
                                cur.execute("INSERT INTO register_discordmember (username, user_id, user_rank) VALUES (%s, %s, %s)", (usr_name, usr_id, rank_id))
                                cur.execute("UPDATE register_activationcode SET active_disc = FALSE WHERE code = %s", (key,))
                                db.commit()
                                await client.send_message(main_channel, "%s is now %s! Thanks for supporting us!" % (msg.author.mention, role.mention))
                            except:
                                print(sys.exc_info())
                                await client.send_message(msg.author, "Error: Something weird occured. Please contact a moderator.")
                        else:
                            await client.send_message(msg.author, "Error: This user already used an activation code.")
                    else:
                        await client.send_message(msg.author, "Error: This code has already been used on discord.")
                except KeyError:
                    await client.send_message(msg.author, "Error: This code seems invalid.")
        else:
            await client.send_message(msg.author, "Bad syntax: `!redeem my_activation_code` should work.")

    elif msg.content.startswith('!capcom'):
        quote = quotes[randint(1, len(quotes) - 1)]
        quote = [s for s in quote.split('\n') if s]

        embed = Embed(
            type = 'rich',
            colour = Colour.blue(),
            title = "Out-of-context Apollo 11 transcript",
            description = quote[1]
        )
        embed.set_footer(text=quote[0])
        await client.send_message(msg.channel, embed=embed)

    elif msg.content.startswith('!info'):
        embed = Embed(
            type = 'rich',
            colour = Colour.orange(),
            title = "SKYWANDERERS' MAIN GUIDANCE COMPUTER",
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/279940382656167936/361678736422076418/comp.png")
        embed.add_field(name="Commands handbook", value=
                "!info"
                "\n!capcom"
                "\n!kick @member"
                "\n!redeem activationKey")
        embed.add_field(name="Subsystems status", value=
                "[ON] Reddit tracking"
                "\n[ON] Chat logging"
                "\n[ON] Welcome and goodbye"
                "\n[ON] Automated redeem"
                "\n[ON] Showcase management"
                "\n[ON] Cool easter eggs")
        embed.set_footer(
            text="Main guidance computer crafted by LeMinaw corp. ltd",
            icon_url="https://cdn.discordapp.com/avatars/201484914686689280/b6a28b98e51f482052e42009fed8c6c4.png?size=256"
        )
        await client.send_message(msg.channel, embed=embed)

    # elif not msg.author.bot and any(w in msg.content.lower() for w in ("skywanderers", "sky1", "sky wanderers")):
    #     response = await client.send_message(msg.channel, "Err: Skywanderers pre-aplha: not found :'(")
    #     await asyncio.sleep(2)
    #     await client.delete_message(response)

    if msg.channel.id == SHOWCASE_CHANNEL_ID:
        if "[complete]" in msg.content.lower():
            if not msg.author.bot:
                await client.send_message(msg.author, "`[Complete]` tags are not supposed to work. Please use a `[Completed]` tag instead.")
        if not any(prefix in msg.content.lower() for prefix in ("[completed]", "[wip]", "[info]")) and len(msg.attachments) == 0:
            await client.delete_message(msg)
            if not msg.author.bot:
                await client.send_message(msg.author, "You can only submit files or prefixed messages on #showcase. Your message was deleted :(.\n```%s```" % msg.content)
        elif "[completed]" in msg.content.lower():
            await client.add_reaction(msg, "\u2795")

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
async def on_socket_raw_receive(payload):
    try:
        event = json.loads(payload)
    except UnicodeDecodeError:
        return

    if (event['t'] == "MESSAGE_REACTION_ADD"
            and event['d']['channel_id'] == SHOWCASE_CHANNEL_ID
            and event['d']['emoji']['name'] == "\u2795"):

        chan = client.get_channel(event['d']['channel_id'])
        msg  = await client.get_message(chan, event['d']['message_id'])

        for reac in msg.reactions:
            if reac.emoji == "\u2795":
                reac_nb = reac.count
                break

        if not msg.pinned and reac_nb >= REACTIONS_THRESHOLD:
            await client.pin_message(msg)
            print("lo")
            await client.send_message(main_channel, "A publication just reached %s reactions in %s! Congratulations, %s." % (REACTIONS_THRESHOLD, chan.mention, msg.author.mention))


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
        "Just go.",
        "Have peace wandering among the stars <3",
        "It's been fun. Don't come back.",
    ])
    await client.send_message(main_channel, msg.format(mention=member.mention))


@client.event
async def on_ready():
    print("Logged in as {user.name} ({user.id}).".format(user=client.user))

    global mutes
    global quotes
    global log_channel, main_channel, reddit_channel, showcase_channel

    # Getting channels
    log_channel      = client.get_channel(LOG_CHANNEL_ID)
    main_channel     = client.get_channel(MAIN_CHANNEL_ID)
    reddit_channel   = client.get_channel(REDDIT_CHANNEL_ID)
    showcase_channel = client.get_channel(SHOWCASE_CHANNEL_ID)

    # Changing presence
    await client.change_presence(game=Game(name="Skywanderers"))

    # Computing A11 quotes
    with open("a11.txt", 'rt') as script_file:
        script = script_file.read()
    pattern = re.compile(r'\n\n.+\n.+\n\n', re.MULTILINE)
    quotes = pattern.findall(script)

    # Loading redis mutes
    if RESET_MUTES_ON_LOAD:
        mutes.save()
        print("Data reinit done.")
    try:
        mutes.load()
        print("Data loading sucessful.")
    except NameError:
        print("Error occured while loading data. Attempting to reinit.")
        mutes.save()
        print("Data reinit done.")


async def check_mutes(delay=60):
    await client.wait_until_ready()

    while not client.is_closed:
        await asyncio.sleep(delay)
        mutes.load()
        user_ids = list(mutes.data.keys())
        for user_id in user_ids:
            if time() > mutes.data[user_id]:
                server = list(client.servers)[0]
                muted_role = utils.get(server.roles, name='Muted')
                user = server.get_member(user_id)
                await client.remove_roles(user, muted_role)

                del mutes.data[user_id]
                mutes.save()

                await client.send_message(log_channel, embed=Embed(
                    title = "MUTING",
                    description = "**{usr} has been unmuted (time elapsed)**".format(usr = user.mention),
                    type = 'rich',
                    colour = Colour.orange()
                ))
                await client.send_message(user, embed=Embed(
                    title = "You have been unmuted from Skywanderers' discord server.",
                    description = "Welcome back!",
                    type = 'rich',
                    colour = Colour.orange()
                ))


client.loop.create_task(check_subreddit(SUBREDDIT_REFRESH))
client.loop.create_task(check_mutes())
client.run(DISCORD_TOKEN)
db.close()
