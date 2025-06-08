import json
from .const import DOMAIN, MQTT_TOPIC
from .coordinator import EureviaCoordinator
from homeassistant.helpers.dispatcher import async_dispatcher_send


async def setup_mqtt(hass, mqtt_client):
    async def message_received(topic, payload_raw):
        payload = json.loads(payload_raw)
        topic_id = topic.split('/')[-1]

        coordinator = hass.data[DOMAIN]["coordinators"].get(topic_id)
        if not coordinator:
            coordinator = EureviaCoordinator(hass, topic_id, mqtt_client)
            coordinator.update_data(payload)
            hass.data[DOMAIN]["coordinators"][topic_id] = coordinator
            async_dispatcher_send(hass, f"{DOMAIN}_new_device", coordinator)
        else:
            coordinator.update_data(payload)

    await mqtt_client.subscribe(f"{MQTT_TOPIC}/#", message_received)