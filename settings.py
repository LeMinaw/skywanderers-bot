hfrom os import getenv

# GLOBAL

EXTENSIONS = [
    'cogs.log',
    'cogs.fun',
    'cogs.mute',
    'cogs.kick',
    'cogs.twitch',
    'cogs.youtube',
    'cogs.capcom',
    'cogs.skyware',
    'cogs.workshop',
]

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

# SKYWARE

SHOWCASE_CHANNEL = 281178410917822474

# YOUTUBE

YOUTUBE_API_KEY = getenv('YOUTUBE_API_KEY')
YOUTUBE_CHANNEL_ID = "UCITNnomMkqQv1aNi_8dxVBQ"

# WORKSHOP

STEAM_API_KEY = getenv('STEAM_API_KEY')
STARSHIP_EVO_APPID = 711980


try:
    from localsettings import *
    print("localsettings module found, using it.")
except ImportError:
    print("Using production settings from env vars.")
