from discord     import Client, Game, Embed, Colour, Object, utils
from collections import OrderedDict
from datetime    import datetime
from random      import choice, randint
from hashlib     import sha256
from redis       import from_url, StrictRedis
from time        import time
import psycopg2
import asyncio
import json
import sys
import re

from utils import *

from settings import *
try:
    from localsettings import *
except ImportError:
    print("Using production settings from env vars.")


client = Client()
db = psycopg2.connect(**DATABASE)
redis = from_url(REDIS_URL)
mutes = RedisDict(redis=redis, redis_key='mutes')


@client.event
async def on_message(msg):
    mutes.load()
    if msg.author.id in mutes.data:
        await client.delete_message(msg)
        await client.send_message(msg.author, "You're currently muted. Your message was deleted :(.\n```%s```" % msg.content)

    else:
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
            if msg.author.server_permissions.kick_members:
                results = re.search(r'^!mute <@(\d+)>(?: (\d+))?$', msg.content)
                if results is not None:
                    user_id = results.group(1)
                    minutes = results.group(2) or -1

                    user = msg.server.get_member(user_id)

                    mutes.load()
                    if user.id in mutes.data and minutes == -1:
                        del mutes.data[user.id]
                        muted = False
                    else:
                        mutes.data[user.id] = int(minutes)
                        muted = True
                    mutes.save()

                    action = "muted" if muted else "unmuted"
                    duration = "for %sm" % minutes if minutes != -1 else "forever"
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

        elif msg.content.startswith('!info') or msg.content.startswith('!mgc'):
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
                    "\n[ON] Chat logging"
                    "\n[ON] Welcome and goodbye"
                    "\n[ON] Automated redeem"
                    "\n[ON] Showcase management"
                    "\n[ON] Moderation tools"
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

        if client.user.mentioned_in(msg) and not msg.mention_everyone:
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

        if re.match(r"(?:\W|^)wew(?:\W|$)", msg.content, flags=re.I):
            embed = Embed(type='rich', colour=Colour.blue())
            embed.set_image(url="https://cdn.discordapp.com/attachments/241022918807519232/359170809001934848/seal_wew.png")
            await client.send_message(msg.channel, embed=embed)


@client.event
async def on_message_delete(msg):
    if msg.channel.id not in DONT_LOG_CHANNELS_IDS:
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
    if msg_before.channel.id not in DONT_LOG_CHANNELS_IDS and msg_before.content != msg_after.content:
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
    showcase_channel = client.get_channel(SHOWCASE_CHANNEL_ID)
    # reddit_channel   = client.get_channel(REDDIT_CHANNEL_ID)

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
            end_time = mutes.data[user_id]
            if time() > end_time > 0:
                del mutes.data[user_id]
                mutes.save()

                server = list(client.servers)[0]
                user = server.get_member(user_id)

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

# async def check_subreddit(delay=60):
#     await client.wait_until_ready()
#     last_post = None
#
#     while not client.is_closed:
#         await asyncio.sleep(delay)
#
#         if last_post is None:
#             new_posts = get_new_posts(SUBREDDIT_URL, 1)
#             if new_posts is not None:
#                 last_post = new_posts[0]
#
#         else:
#             new_posts = get_new_posts(SUBREDDIT_URL, 5)
#             if new_posts is None:
#                 continue
#             for post in reversed(new_posts):
#                 if post['data']['created_utc'] > last_post['data']['created_utc']:
#                     embed = Embed(
#                         type = 'rich',
#                         colour = Colour.green(),
#                         title       = post['data']['title'],
#                         url         = post['data']['url'],
#                         timestamp   = datetime.fromtimestamp(int(post['data']['created_utc'])),
#                         description = post['data']['selftext'],
#                     )
#                     embed.set_author(
#                         name=post['data']['author'],
#                         url="https://www.reddit.com/user/%s" % post['data']['author']
#                     )
#                     embed.set_footer(
#                         text="New reddit post",
#                         icon_url="https://upload.wikimedia.org/wikipedia/fr/f/fc/Reddit-alien.png"
#                     )
#                     await client.send_message(reddit_channel, embed=embed)
#
#                     last_post = post


# client.loop.create_task(check_subreddit(SUBREDDIT_REFRESH))
client.loop.create_task(check_mutes())
client.run(DISCORD_TOKEN)
db.close()
