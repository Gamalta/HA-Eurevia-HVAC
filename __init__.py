from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .mqtt_client import EureviaMQTTClient

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})

    config = entry.data
    host = config["host"]
    port = config["port"]

    def on_message(topic, payload):
        hass.loop.call_soon_threadsafe(
            lambda: async_dispatcher_send(
                hass,
                f"{DOMAIN}_mqtt_message",
                topic,
                payload
            )
        )
    
    mqtt_client = EureviaMQTTClient(host, port, on_message)
    mqtt_client.start()
    mqtt_client.subscribe("local/hvac/devices/#")

    hass.data[DOMAIN][entry.entry_id] = {
        "mqtt_client": mqtt_client,
    }

    await hass.config_entries.async_forward_entry_setups(entry, ["climate"])

    return True
