import logging
import json
from .const import MQTT_TOPIC
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

class EureviaCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, device_id, mqtt_client):
        super().__init__(hass, _LOGGER, name=f"Eurevia {device_id}")
        self._mqtt = mqtt_client
        self._device_id = device_id
        self.data = {}

    def update_data(self, payload):
        self.data = payload
        self.async_set_updated_data(self.data)

    async def publish(self, topic_suffix, message_dict):
        topic = f"{MQTT_TOPIC}/{self._device_id}/{topic_suffix}"
        payload = json.dumps(message_dict)
        await self._mqtt.publish(topic, payload)

    async def async_subscribe(self):
        async def message_received(msg_topic, payload_raw):
            payload = json.loads(payload_raw)
            if str(payload.get("ID")) != self.device_id:
                return
            self.update_data(payload)
        await self._mqtt.subscribe(f"{MQTT_TOPIC}/#", message_received)