import asyncio
import logging
import paho.mqtt.client as mqtt

_LOGGER = logging.getLogger(__name__)

class EureviaMQTTClient:
    def __init__(self, host, port, user=None, password=None):
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._client = mqtt.Client()
        self._loop = asyncio.get_event_loop()
        self._subscriptions = {}

    async def connect(self):
        if self._user:
            self._client.username_pw_set(self._user, self._password)

        self._client.on_message = self._on_message
        self._client.connect(self._host, self._port)
        self._client.loop_start()

    async def publish(self, topic, payload):
        self._client.publish(topic, payload)

    async def subscribe(self, topic, callback):
        self._subscriptions[topic] = callback
        self._client.subscribe(topic)

    def _on_message(self, client, userdata, msg):
        payload = msg.payload.decode()
        _LOGGER.debug(f"MQTT message received on {msg.topic}: {payload}")
        if msg.topic in self._subscriptions:
            self._loop.call_soon_threadsafe(
                asyncio.create_task, self._subscriptions[msg.topic](msg.topic, payload)
            )
        else:
            for sub_topic, callback in self._subscriptions.items():
                if mqtt.topic_matches_sub(sub_topic, msg.topic):
                    self._loop.call_soon_threadsafe(
                        asyncio.create_task, callback(msg.topic, payload)
                    )