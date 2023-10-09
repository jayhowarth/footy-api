import redis

# host = 'localhost'  # local
host = '192.168.0.246' # Hogstation
port = 49159 # Hogstation
#port = 6379  # local


class RedisManager:

    def __init__(self):
        self.r = r = redis.Redis(host=host, port=port, charset="utf-8", decode_responses=True)

    @staticmethod
    def set_remaining_counter(x):
        r = redis.Redis(host=host, port=port, charset="utf-8", decode_responses=True)
        r.set("remaining", x.strip())

    @staticmethod
    def get_remaining_counter():
        r = redis.StrictRedis(host=host, port=port)
        return int(r.get("remaining"))
