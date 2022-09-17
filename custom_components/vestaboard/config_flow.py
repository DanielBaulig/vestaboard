from homeassistant import config_entries

from .const import DOMAIN, CONF_LOCAL_API_KEY, CONF_LOCAL_API_HOST

import voluptuous as vol

class VestaboardConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input):
        if user_input is not None:
            valid = True # figure out how to validate
            if valid:
                await self.async_set_unique_id(user_input.get(CONF_LOCAL_API_HOST))
                return self.async_create_entry(
                    title=user_input.get(CONF_LOCAL_API_HOST),
                    data={
                        CONF_LOCAL_API_HOST: user_input.get(CONF_LOCAL_API_HOST),
                        CONF_LOCAL_API_KEY: user_input.get(CONF_LOCAL_API_KEY)
                    }
                )
        

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema({
                vol.Required(CONF_LOCAL_API_HOST): str,
                vol.Required(CONF_LOCAL_API_KEY): str
            })
        )