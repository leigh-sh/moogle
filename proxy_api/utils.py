import datetime
from json import JSONEncoder

COUNTRY_CODES = ['us', 'uk']
INVALID_PROXIES = 'invalid_proxies'


class DateTimeEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
