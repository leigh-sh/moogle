from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES

from utils import COUNTRY_CODES


def error_response(status_code, message=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response


def bad_request(message):
    return error_response(400, message)


def invalid_country_code_response():
    return bad_request(message='Invalid country code. Please supply a country code from the following %s.'
                               % ','.join(COUNTRY_CODES))
