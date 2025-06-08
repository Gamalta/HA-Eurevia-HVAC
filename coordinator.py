import logging
import json
from .const import MQTT_TOPIC
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

class EureviaCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, topic_id, mqtt_client):
        super().__init__(hass, _LOGGER, name=f"Eurevia {topic_id}")
        self._mqtt = mqtt_client
        self._topic_id = topic_id

    @property
    def device_id(self):
        return self._topic_id

    def update_data(self, payload):
        self.async_set_updated_data(payload)

    async def publish(self, topic_suffix, message_dict):
        topic = f"{MQTT_TOPIC}/{self._topic_id}/{topic_suffix}"
        payload = json.dumps(message_dict)
        await self._mqtt.publish(topic, payload)
