import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN


class ZendureConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="Zendure Readonly",
                data={
                    "host": user_input["host"],
                },
            )

        schema = vol.Schema({
            vol.Required("host", default="192.168.x.y"): str,
        })

        return self.async_show_form(step_id="user", data_schema=schema)
