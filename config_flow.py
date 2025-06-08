from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
from .const import DOMAIN

class EureviaHVACMQTTConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="Eurevia HVAC", data=user_input)

        schema = vol.Schema({
            vol.Required("host"): str,
            vol.Required("port", default=1883): int
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
