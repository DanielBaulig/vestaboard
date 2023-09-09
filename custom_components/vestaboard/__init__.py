""" Vestaboard Integration """
from datetime import timedelta
import aiohttp
import logging
import json
import async_timeout
from contextlib import asynccontextmanager
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
    @staticmethod
    async def enable(host, enablement_token):
        uri = f"http://{host}:7000/local-api/enablement"
        headers = {
            "X-Vestaboard-Local-Api-Enablement-Token": enablement_token,
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(uri) as response:
                # Vestaboard response with text/plain content type
                json = await response.json(content_type="text/plain")

                if not response.status in range(200, 299) or "apiKey" not in json:
                    return None

        return json.get("apiKey")


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

    @asynccontextmanager
    async def session(self):
        async with aiohttp.ClientSession(headers=self.auth_headers) as session:
            yield session

    @asynccontextmanager
    async def post(self, lines):
        uri = self.local_api_uri
        _LOGGER.debug('POST being sent to %s', uri)
        async with self.session() as session:
            yield await session.post(uri, data=lines)

    @asynccontextmanager
    async def get(self):
        uri = self.local_api_uri
        _LOGGER.debug('GET being sent to %s', uri)
        async with self.session() as session:
            yield await session.get(uri)

    async def read(self):
        async with self.get() as response:
            if response.status not in range(200, 299):
                _LOGGER.error('Read failed with error code %d and message %s', response.status, await response.text())
                return None
                
            json = await response.json(content_type="text/plain")
        
        return self.decode_lines(json['message'])
    
    @staticmethod
    def encode_lines(lines):
        lines += [''] * (6 - len(lines))
        normalized_lines = ['{:<22}'.format(line[:22].upper()) for line in lines]
        encoded_lines = [[character_map.get(char, 60) for char in line] for line in normalized_lines]

        return json.dumps(encoded_lines)

    @staticmethod
    def decode_lines(lines):
        return [ ''.join([inverted_character_map[code] for code in line]) for line in lines ]

    async def write(self, lines):
        async with self.post(self.encode_lines(lines)) as response:
            if response.status not in range(200, 299):
                _LOGGER.error('Write failed with error code %d and message %s', response.status, await response.text())
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
            data = await self.vestaboard.read()
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
        result = await vestaboard.write(lines)
        # Update line sensors after an update
        config.async_create_task(hass, coordinator.async_request_refresh())
        return result

    hass.services.async_register(DOMAIN, "post", post)

    return True
