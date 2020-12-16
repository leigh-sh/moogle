import logging
import os
from collections import namedtuple
from datetime import datetime
from json import dumps

from apispec import APISpec
from apispec_webframeworks.flask import FlaskPlugin
from flask import Flask, request, Response

from errors import *
from redis_client import RedisClient

app = Flask(__name__)

logging.getLogger('').setLevel(os.getenv("LOGGING_LEVEL", logging.DEBUG))

redis_client = RedisClient()
InvalidProxy = namedtuple('InvalidProxy', 'country_code ip timestamp')
redis_client.init_data()

spec = APISpec(
    title="Proxy Management API",
    version="1.0.0",
    openapi_version="3.0.2",
    plugins=[FlaskPlugin()],
)


@app.route('/GetProxy', methods=['GET'])
def get_proxy():
    """
    gets a country code ('us' or 'uk') and returns a proxy from the list.
    ---
    get:
        description: country_code
        parameters:
         - in: query
           name: country_code
           schema:
            type: string
           description: should be 'us' or 'uk'
           required: true
        responses:
            200:
                description: proxy from the list of the country_code supplied
            404:
                description: proxy address was not found
            400:
                description: country_code was invalid
    """

    country_code = request.args.get('country_code')
    try:
        validate_country_code(country_code)
    except AssertionError:
        logging.debug(f'Country code empty or not found "{country_code}"')
        return invalid_country_code_response()
    proxy_address = redis_client.get_proxy_for_country_code(country_code)

    if not proxy_address:
        logging.warning(f'Proxy list for "{country_code}" is empty')
        return error_response(status_code=404, message='No proxy was found.')

    return Response(dumps(proxy_address.decode('utf-8')), status=200, mimetype='application/json')


@app.route('/ReportError', methods=['POST'])
def report_error():
    """
    Gets an IP address and a country code and marks it as invalid for the next 6 hours.
    ---
    post:
      requestBody:
        required: true
        description: Proxy to be marked as invalid
        content:
          application/json:
            schema:
              type: object
              properties:
                country_code:
                  type: string
                ip:
                  type: string
              required:
                - country_code
                - ip
      responses:
        '200':
          description: Proxy set to invalid
        '400':
          description: Proxy to remove does not exist or was not provided
      summary: Mark a proxy as invalid
    """

    data = request.get_json() or {}
    country_code = data.get('country_code')
    ip = data.get('ip')

    try:
        validate_country_code(country_code)
    except AssertionError:
        logging.debug(f'Country code empty or not found "{country_code}"')
        return invalid_country_code_response()

    removed_count = redis_client.remove_proxy_from_country_code_list(country_code=country_code, proxy_address=ip)

    if removed_count > 0:
        invalid_proxy = InvalidProxy(country_code=redis_client.get_key_from_country_code(country_code),
                                     ip=ip,
                                     timestamp=dumps(int(datetime.now().timestamp())))
        redis_client.add_invalid_proxy(invalid_proxy)
        logging.debug(f'IP "{ip}" was removed from country "{country_code}"')
    else:
        logging.info(f'IP to remove "{ip}" does not exist in "{country_code}"')
        return error_response(status_code=400, message='Reported proxy does not exist.')

    return Response(status=200)


@app.route("/spec")
def get_apispec():
    return jsonify(spec.to_dict())


def validate_country_code(country_code):
    assert country_code and country_code in COUNTRY_CODES


with app.test_request_context():
    spec.path(view=get_proxy)
    spec.path(view=report_error)

if __name__ == '__main__':
    app.run()
