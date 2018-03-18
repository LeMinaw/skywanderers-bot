from os import getenv

DISCORD_TOKEN = getenv('DISCORD_TOKEN')

LOG_CHANNEL_ID      = "361282322303156224"
MAIN_CHANNEL_ID     = "241014195884130315"
RULES_CHANNEL_ID    = "275053802615209986"
SHOWCASE_CHANNEL_ID = "281178410917822474"
# REDDIT_CHANNEL_ID   = "362107240963899395"

DONT_LOG_CHANNELS_IDS = [
    LOG_CHANNEL_ID,
    "271095863194025993", # bot-chat
    "397822559837618219", # warframe
    "403763237201379338"  # warframe-alerts
]

# SUBREDDIT_URL = "skywanderers"
# SUBREDDIT_REFRESH = 20 # Seconds
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
