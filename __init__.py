from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send
from .mqtt_handler import setup_mqtt
from .const import DOMAIN, PLATFORMS
from mqtt_client import EureviaMQTTClient

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    config = entry.data
    mqtt_client = EureviaMQTTClient(config["host"], config["port"], config.get("user"), config.get("password"))
    await mqtt_client.connect()

    hass.data.setdefault(DOMAIN, {"mqtt_client": mqtt_client, "coordinators": {}})

    await setup_mqtt(hass, mqtt_client)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True