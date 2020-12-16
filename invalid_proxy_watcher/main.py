import logging
import os
import sys
from collections import namedtuple
from datetime import datetime
from json import loads
from time import sleep


import redis

InvalidProxy = namedtuple('InvalidProxy', 'country_code ip timestamp')
logging.getLogger('').setLevel(os.getenv("LOGGING_LEVEL", logging.DEBUG))


# Database Settings
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = 6379
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)


def get_hours_as_seconds(num_of_hours):
    return num_of_hours * 3600


def restore_proxy():
    pipeline = redis_client.pipeline()
    pipeline.lpop('invalid_proxies')
    pipeline.rpush(invalid_proxy.country_code, invalid_proxy.ip)
    pipeline.execute()


if __name__ == '__main__':
    HOURS_TO_BAN = os.getenv("HOURS_TO_BAN", "6")
    MAX_WAIT_TIME_IN_SECONDS = get_hours_as_seconds(int(HOURS_TO_BAN))

    while True:
        logging.debug("Checking list (%s)" % datetime.now())
        proxy = redis_client.lindex(name='invalid_proxies', index=0)
        if proxy:
            invalid_proxy = InvalidProxy(*loads(proxy))
            invalid_proxy_datetime = datetime.fromtimestamp(loads(invalid_proxy.timestamp))

            diff = datetime.now() - invalid_proxy_datetime

            diff_in_seconds = MAX_WAIT_TIME_IN_SECONDS - diff.seconds
            logging.info(f'Found IP {invalid_proxy.ip}')
            if diff_in_seconds > 0:
                logging.debug(f'IP has not reached max wait time. Sleeping for {diff_in_seconds} seconds')
                sleep(diff_in_seconds)
            else:
                logging.info(f'Wait time for IP exceeded. Restoring IP {invalid_proxy.ip}')
                restore_proxy()
        else:
            logging.debug(f'List is empty, sleeping for a max of {MAX_WAIT_TIME_IN_SECONDS} seconds')
            sleep(MAX_WAIT_TIME_IN_SECONDS)



