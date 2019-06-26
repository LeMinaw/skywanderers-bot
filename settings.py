from os import getenv

# GLOBAL

EXTENSIONS = ['cogs.log',
              'cogs.fun',
              'cogs.mute',
              'cogs.kick',
              'cogs.twitch',
              'cogs.redeem',
              'cogs.capcom',
              'cogs.skyware']

DISCORD_TOKEN = getenv('DISCORD_TOKEN')
REDIS_URL     = getenv('REDIS_URL')
FAQ_CHANNEL   = 511966157641875475
MAIN_CHANNEL  = 478014467746168832
RULES_CHANNEL = 275053802615209986

# LOGS

LOG_CHANNEL   = 361282322303156224
DONT_LOG = [
    271095863194025993, # bot-chat
    397822559837618219, # warframe
    403763237201379338  # warframe-alerts
]

# TWITCH

STREAMS_CHANNEL = 317360477292331011
TWITCH_CLIENT_ID = "qriowv30qp0heuosqlc3hekd9p6h29"

# REDDIT

REDDIT_CHANNEL = 362107240963899395
SUBREDDIT_URL = "skywanderers"

# MUTE

RESET_MUTES_ON_LOAD = False

# REDEEM

DATABASE = {
    "dbname": "d9um5ikkkmm463",
    "user": "fukkkitgsohzeo",
    "password": getenv('DB_PWD'),
    "host": "ec2-184-73-199-72.compute-1.amazonaws.com",
    "port": 5432
}
ROLES = {
    11: "Supporter",
    12: "Pioneer",
    13: "Explorer",
    14: "Entrepreneur",
    15: "Pirate",
    16: "Corporate Mogul",
    17: "Adventurer",
    18: "Pirate Lord",
    19: "Legendary Pirate Lord",
    20: "Legendary Pirate King",
}

try:
    from localsettings import *
    print("localsettings module found, using it.")
except ImportError:
    print("Using production settings from env vars.")
