import paho.mqtt.client as mqtt
import threading
import logging
import json

_LOGGER = logging.getLogger(__name__)

class EureviaMQTTClient:
    def __init__(self, host, port, on_message):
        self._host = host
        self._port = port
        self._on_message = on_message
        self._client = mqtt.Client()
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message_internal
        self._connected = False
        self._subscriptions = []

    def _on_connect(self, client, userdata, flags, rc):
        _LOGGER.info(f"Connected to external MQTT broker at {self._host}:{self._port}")
        self._connected = True
        for topic in self._subscriptions:
            client.subscribe(topic)

    def _on_message_internal(self, client, userdata, msg):
        payload = msg.payload.decode()
        self._on_message(msg.topic, payload)

    def start(self):
        def run():
            self._client.connect(self._host, self._port, 60)
            self._client.loop_forever()
        threading.Thread(target=run, daemon=True).start()

    def subscribe(self, topic, qos=0):
        self._subscriptions.append(topic)
        if self._connected:
            self._client.subscribe(topic, qos)

    def publish(self, topic, payload):
        self._client.publish(topic, payload)
