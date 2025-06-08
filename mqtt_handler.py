import logging
import json
from .const import DOMAIN, MQTT_TOPIC
from .coordinator import EureviaCoordinator
from homeassistant.helpers.dispatcher import async_dispatcher_send


_LOGGER = logging.getLogger(__name__)

async def setup_mqtt(hass, mqtt_client):
    async def message_received(topic, payload_raw):
        payload = json.loads(payload_raw)
        topic_id = topic.split('/')[-1]

        if payload.get("ID") is None:
            return
        device_id = str(payload.get("ID"))

        coordinator = hass.data[DOMAIN]["coordinators"].get(device_id)
        if not coordinator:
            coordinator = EureviaCoordinator(hass, topic_id, device_id, mqtt_client)
            hass.data[DOMAIN]["coordinators"][device_id] = coordinator

            async_dispatcher_send(hass, f"{DOMAIN}_new_device", coordinator)

        coordinator.update_data(payload)

    await mqtt_client.subscribe(f"{MQTT_TOPIC}/#", message_received)