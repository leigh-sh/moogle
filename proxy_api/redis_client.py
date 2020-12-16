import os
from json import dumps

import redis
from redis import RedisError

from utils import INVALID_PROXIES, COUNTRY_CODES

# Database Settings
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = 6379


class RedisClient(object):
    """Manage Redis Connection"""

    def __init__(self):
        self.r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

    def get_proxy_for_country_code(self, country_code):
        # rpoplpush: RPOP a value off of the src list and atomically LPUSH it on to the dst list. Returns the value.
        return self.r.rpoplpush(self.get_key_from_country_code(country_code), self.get_key_from_country_code(country_code))

    def get_key_from_country_code(self, country_code):
        return f'proxies_{country_code}'

    def remove_proxy_from_country_code_list(self, country_code, proxy_address):
        # lrem: Removes the first count occurrences of elements equal to element from the list stored at key.
        return self.r.lrem(name=self.get_key_from_country_code(country_code), count=1, value=proxy_address)

    def add_invalid_proxy(self, invalid_proxy):
        """ Add to invalid proxy, a InvalidProxy object which contains country_code, ip and timestamp"""
        self.r.rpush(INVALID_PROXIES, dumps(invalid_proxy))

    def add_to_list(self, key, obj):
        self.r.rpush(key, obj)

    def init_data(self):
        self.r.delete(self.get_key_from_country_code(COUNTRY_CODES[0]))
        self.r.delete(self.get_key_from_country_code(COUNTRY_CODES[1]))
        self.add_to_list(self.get_key_from_country_code(COUNTRY_CODES[0]), '1.1.1.1')
        self.add_to_list(self.get_key_from_country_code(COUNTRY_CODES[0]), '1.2.2.2')
        self.add_to_list(self.get_key_from_country_code(COUNTRY_CODES[0]), '1.3.3.3')
        self.add_to_list(self.get_key_from_country_code(COUNTRY_CODES[0]), '1.4.4.4')
        self.add_to_list(self.get_key_from_country_code(COUNTRY_CODES[1]), '2.1.1.1')
        self.add_to_list(self.get_key_from_country_code(COUNTRY_CODES[1]), '2.2.2.2')
        self.add_to_list(self.get_key_from_country_code(COUNTRY_CODES[1]), '2.3.3.3')
        self.add_to_list(self.get_key_from_country_code(COUNTRY_CODES[1]), '2.4.4.4')
