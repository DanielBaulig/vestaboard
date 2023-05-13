""" Vestaboard Integration """
from datetime import timedelta
import requests
import logging
import json
import async_timeout
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

_LOGGER=logging.getLogger(__name__)

from .const import DOMAIN, CONF_LOCAL_API_HOST, CONF_LOCAL_API_KEY

ATTR_LINES="lines"

character_map = {
    '~': 0,
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
}

inverted_character_map = {v:k for k,v in character_map.items()}

class Vestaboard:
    def __init__(self, host, local_api_key):
        self.host = host
        self.local_api_key = local_api_key

    @property
    def auth_headers(self):
        return {
            'X-Vestaboard-Local-Api-Key': self.local_api_key
        }

    @property
    def local_api_uri(self):
        return f"http://{self.host}:7000/local-api/message"

    def read(self):
        uri = self.local_api_uri

        try:
            _LOGGER.debug('Read being sent to %s', uri)
            response = requests.get(uri, headers=self.auth_headers)
        except ConnectionError:
            _LOGGER.error('Failed to connect to %s', self.host)
            return None
        except requests.Timeout:
            _LOGGER.error('Connection attempt timed out connecting to %s', self.host)
            return None
        except requests.exceptions.RequestException as err:
            _LOGGER.error('An unknown request exception occured connecting to %s', self.host)
            return None
        except:
            _LOGGER.error('An unknown exception occured connecting to %s', self.host)
            return None

        if response.status_code < 200 or response.status_code > 299:
            _LOGGER.error('Read failed with error code %d and message %s', response.status_code, response.text)
            return None

        return [ ''.join([inverted_character_map[code] for code in line]) for line in response.json()['message'] ]

    def post(self, lines):
        uri = self.local_api_uri

        lines += [''] * (6 - len(lines))
        normalized_lines = ['{:<22}'.format(line[:22].upper()) for line in lines]
        encoded_lines = [[character_map.get(char, 60) for char in line] for line in normalized_lines]

        lines_json = json.dumps(encoded_lines)

        try:
            _LOGGER.debug('Request being sent to %s with payload %s', uri, lines_json)
            response = requests.post(
                uri,
                data=lines_json,
                headers=self.auth_headers,
            )
        except ConnectionError:
            _LOGGER.error('Failed to connect to %s', self.host)
            return False
        except requests.Timeout:
            _LOGGER.error('Connection attempt timed out connecting to %s', self.host)
            return False
        except requests.exceptions.RequestException as err:
            _LOGGER.error('An unknown request exception occured connecting to %s', self.host)
            return False
        except:
            _LOGGER.error('An unknown exception occured connecting to %s', self.host)
            return False

        if response.status_code < 200 or response.status_code > 299:
            _LOGGER.error('Update failed with error code %d and message %s', response.status_code, response.text)
            return False

        return True


class VestaboardCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, vestaboard):
        super().__init__(
            hass, _LOGGER, name="Vestaboard",
            update_interval=timedelta(seconds=30)
        )
        self.vestaboard = vestaboard

    async def _async_update_data(self):
        async with async_timeout.timeout(10):
            data = await self.hass.async_add_executor_job(lambda: self.vestaboard.read())
            if data is None:
                raise UpdateFailed("Couldn't update vestaboard lines sensor.")

            return data


async def async_setup_entry(hass, config):
    host = config.data[CONF_LOCAL_API_HOST]
    local_api_key = config.data[CONF_LOCAL_API_KEY]

    vestaboard = Vestaboard(host, local_api_key)
    coordinator = VestaboardCoordinator(hass, vestaboard)

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    hass.data[DOMAIN][config.entry_id] = {
        'coordinator': coordinator,
    }

    await coordinator.async_config_entry_first_refresh()

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(
            config,
            "sensor"
        )
    )

    async def post(call):
        lines = call.data.get(ATTR_LINES)
        result = await hass.async_add_executor_job(lambda: vestaboard.post(lines))
        # Update line sensors after an update
        config.async_create_task(hass, coordinator.async_request_refresh())
        return result

    hass.services.async_register(DOMAIN, "post", post)

    return True