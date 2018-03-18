import requests
import pickle


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
