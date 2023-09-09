from homeassistant import config_entries

from .const import DOMAIN, CONF_LOCAL_API_KEY, CONF_LOCAL_API_HOST

import voluptuous as vol
import aiohttp
from . import Vestaboard

class VestaboardConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input):
        return await self.async_step_host(user_input)

    async def async_step_host(self, user_input):
        errors={}

        if user_input is not None:
            local_api_host = user_input.get(CONF_LOCAL_API_HOST).strip()
            # Validate host
            uri = f"http://{local_api_host}:7000/local-api/message"
            headers = {
                "X-Vestaboard-Local-Api-Key": "invalid",
            }
            async with aiohttp.ClientSession(headers=headers) as session:
                try:
                    async with session.get(uri) as _:
                        # Vestaboard will return a 200 without content
                        # provided an invalid api key (see above).
                        # But since that behavior is not documented we
                        # will not verify this and assume any response
                        # is hinting at an active Vestaboard.
                        pass
                except aiohttp.ClientConnectorError:
                    errors["base"] = "connection_error"

            if len(errors) == 0:
                setattr(
                    self,
                    CONF_LOCAL_API_HOST,
                    local_api_host,
                )
                return await self.async_step_ask_need_local_api_key()

        return self.async_show_form(
            step_id="host", data_schema=vol.Schema({
                vol.Required(CONF_LOCAL_API_HOST): str,
            }),
            last_step=False,
            errors=errors,
        )

    async def async_step_ask_need_local_api_key(self):
        return self.async_show_menu(
            step_id="ask_need_local_api_key",
            menu_options=[
                'local_api_enablement_token',
                'local_api_key',
            ]
        )
    
    async def async_step_local_api_key(self, user_input):
        assert hasattr(self, CONF_LOCAL_API_HOST)
        local_api_host = getattr(self, CONF_LOCAL_API_HOST)

        errors = {}

        if user_input is not None:
            local_api_key = user_input.get(CONF_LOCAL_API_KEY).strip()

            uri = f"http://{local_api_host}:7000/local-api/message"
            headers = {
                "X-Vestaboard-Local-Api-Key": local_api_key,
            }
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(uri) as response:
                    if not response.status in range(200, 299) or int(response.headers.get('Content-Length')) <= 0:
                        # Vestaboard will return the current active message
                        # given a valid API key. Given an invalid key,
                        # Vestaboard will also return 200 but without content.
                        errors["base"] = "invalid_api_key"

            if len(errors) == 0:
                # Shouldn't use IP address for unique ID
                # But not sure if we have anything better.
                # The Vestaboard itself doesn't uniquely identify itself
                # via the API.
                await self.async_set_unique_id(local_api_host)
                return self.async_create_entry(
                    title=local_api_host,
                    data={
                        CONF_LOCAL_API_HOST: local_api_host,
                        CONF_LOCAL_API_KEY: local_api_key,
                    }
                )

        local_api_key = getattr(self, CONF_LOCAL_API_KEY) if hasattr(self, CONF_LOCAL_API_KEY) else None
        
        return self.async_show_form(
            step_id="local_api_key", data_schema=vol.Schema({
                vol.Required(
                    CONF_LOCAL_API_KEY,
                    # Using local_api_key as a suggested value instead of skipping
                    # through this step so tha the user has an opportunity to
                    # note down the local API key when it's generated through
                    # a local API enablement token.
                    description={
                        "suggested_value": local_api_key,
                    },
                ): str
            }),
            errors=errors,
        )

    async def async_step_local_api_enablement_token(self, user_input):
        assert hasattr(self, CONF_LOCAL_API_HOST)
        errors={}

        if user_input is not None:
            local_api_enablement_token = user_input.get("local_api_enablement_token").strip()
            local_api_host = getattr(self, CONF_LOCAL_API_HOST)
            local_api_key = await Vestaboard.enable(local_api_host, local_api_enablement_token)

            if local_api_key is None:
                errors["base"] = "invalid_enablement_token"

            if len(errors) == 0:
                setattr(self, CONF_LOCAL_API_KEY, local_api_key)
                return await self.async_step_local_api_key(None)

        return self.async_show_form(
            step_id="local_api_enablement_token", data_schema=vol.Schema({
                vol.Required("local_api_enablement_token"): str
            }),
            errors=errors,
        )
