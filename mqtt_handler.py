import json
from .const import DOMAIN, MQTT_TOPIC
from .coordinator import EureviaCoordinator
from homeassistant.helpers.dispatcher import async_dispatcher_send

async def setup_mqtt(hass, mqtt_client):
    async def message_received(topic, payload_raw):
        payload = json.loads(payload_raw)
        device_id = str(payload["ID"])

        if device_id not in hass.data[DOMAIN]["coordinators"]:
            coordinator = EureviaCoordinator(hass, device_id, mqtt_client)
            await coordinator.async_subscribe()
            hass.data[DOMAIN]["coordinators"][device_id] = coordinator

            async_dispatcher_send(hass, f"{DOMAIN}_new_device", coordinator)

        hass.data[DOMAIN]["coordinators"][device_id].update_data(payload)

    await mqtt_client.subscribe(f"{MQTT_TOPIC}/#", message_received)