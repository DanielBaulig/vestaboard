""" Vestaboard Integration """
import requests
import logging
import json

_LOGGER=logging.getLogger(__name__)

from .const import DOMAIN, CONF_LOCAL_API_HOST, CONF_LOCAL_API_KEY

ATTR_LINES="lines"

character_map = {
    ' ': 0,
    'A': 1,
    'B': 2,
    'C': 3,
    'D': 4,
    'E': 5,
    'F': 6,
    'G': 7,
    'H': 8,
    'I': 9,
    'J': 10,
    'K': 11,
    'L': 12,
    'M': 13,
    'N': 14,
    'O': 15,
    'P': 16,
    'Q': 17,
    'R': 18,
    'S': 19,
    'T': 20,
    'U': 21,
    'V': 22,
    'W': 23,
    'X': 24,
    'Y': 25,
    'Z': 26,
    '1': 27,
    '2': 28,
    '3': 29,
    '4': 30,
    '5': 31,
    '6': 32,
    '7': 33,
    '8': 34,
    '9': 35,
    '0': 36,
    '!': 37,
    '@': 38,
    '#': 39,
    '$': 40,
    '(': 41,
    ')': 42,
    '-': 44,
    '+': 46,
    '&': 47,
    '=': 48,
    ';': 49,
    ':': 50,
    "'": 52,
    '"': 53,
    '%': 54,
    ',': 55,
    '.': 56,
    '/': 59,
    '?': 60,
    '°': 62,
    '\xc1': 63,
    '\xc2': 64,
    '\xc3': 65,
    '\xc4': 66,
    '\xc5': 67,
    '\xc6': 68,
    '\xc7': 69,
    '~': 0
}

async def async_setup_entry(hass, config):
    host = config.data[CONF_LOCAL_API_HOST]
    local_api_key = config.data[CONF_LOCAL_API_KEY] 

    uri = f"http://{host}:7000/local-api/message"
    headers = {
        'X-Vestaboard-Local-Api-Key': local_api_key
    }

    async def post(call):
        nonlocal uri
        nonlocal headers
        nonlocal host

        lines = call.data.get(ATTR_LINES)

        lines_array = []

        for i in range(6):
            line = '' if i >= len(lines) else (lines[i] or '')
            normalized_line = '{:<22}'.format(line[:22].upper())

            lines_array.append([])

            for char in normalized_line:
                lines_array[i].append(
                    character_map.get(char if char in character_map else '?')
                )
        lines_json = json.dumps(lines_array)
        
        try:
            _LOGGER.debug('Request being sent to %s with payload %s', uri, lines_json)
            response = await hass.async_add_executor_job(lambda: requests.post(
                uri,
                data=lines_json,
                headers=headers,
            ))
        except ConnectionError:
            _LOGGER.error('Failed to connect to %s', host)
            return False
        except requests.Timeout:
            _LOGGER.error('Connection attempt timed out connecting to %s', host)
            return False
        except requests.exceptions.RequestException as err:
            _LOGGER.error('An unknown request exception occured connecting to %s', host)
            return False
        except:
            _LOGGER.error('An unknown exception occured connecting to %s', host)
            return False

        if response.status_code < 200 or response.status_code > 299:
            _LOGGER.error('Update failed with error code %d and message %s', response.status_code, response.text)
            return False

        return True

    hass.services.async_register(DOMAIN, "post", post)

    return True