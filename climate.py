from homeassistant.components.climate import ClimateEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.const import UnitOfTemperature
from homeassistant.components.climate.const import HVACMode, HVACAction, PRESET_NONE, ClimateEntityFeature
from homeassistant.core import HomeAssistant
from .const import DOMAIN, EUREVIA_PRESET_MODE_TO_HA_PRESET_MODE, EUREVIA_HVAC_MODE_TO_HA_HVAC_MODE
import json

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    mqtt_client = hass.data[DOMAIN][entry.entry_id]["mqtt_client"]
    entities = {}

    def mqtt_dispatch_handler(topic, raw_payload):
        try:
            payload = json.loads(raw_payload)
        except json.JSONDecodeError:
            return

        if not all(key in payload for key in ("ID", "Mode_Active", "Stp_Comf", "Zone_Name")):
            return

        device_id = str(payload["ID"])
        def schedule_entity_addition(entity):
            async def _add():
                async_add_entities([entity])
            hass.loop.call_soon_threadsafe(lambda: hass.async_create_task(_add()))

        if device_id not in entities:
            entity = EureviaHVACMQTTClimate(
                mqtt_client,
                topic,
                device_id,
                payload
            )
            entities[device_id] = entity
            schedule_entity_addition(entity)
        else:
            entities[device_id].update_from_mqtt(payload)

    entry.async_on_unload(
        async_dispatcher_connect(hass, f"{DOMAIN}_mqtt_message", mqtt_dispatch_handler)
    )



class EureviaHVACMQTTClimate(ClimateEntity):



    def __init__(self, mqtt_client, topic, device_id, payload):
        self._mqtt = mqtt_client
        self._topic = topic
        self._device_id = device_id
        #self._payload = payload.copy()

        self._state = {
            "temperature": payload.get("Tmp"),
            "humidity": payload.get("RH"),
            "target_temperature": payload.get("Stp_Comf"),
            "operating_mode": payload.get("Mode_Active", None) or payload.get("Mode"),
            "zone_name": payload.get("Th_Name", None) or payload.get("Custom_Zone_Name", None) or payload.get("Zone_Name", None)
        }



    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": f"Eurevia HVAC {self._state['zone_name']}",
            "manufacturer": "Eurevia",
            "model": "HVAC",
        }



    @property
    def unique_id(self):
        return self._device_id



    @property
    def name(self):
        return self._state["zone_name"]



    @property
    def extra_state_attributes(self):
        return {
            "zone_name": self._state["zone_name"],
        }



    @property
    def current_temperature(self):
        return self._state["temperature"]



    @property
    def current_humidity(self):
        return self._state["humidity"]



    @property
    def temperature_unit(self):
        return UnitOfTemperature.CELSIUS



    @property
    def target_temperature(self):
        return self._state["target_temperature"]



    @property
    def supported_features(self):
        return (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.PRESET_MODE
            | ClimateEntityFeature.TURN_OFF
            | ClimateEntityFeature.TURN_ON
        )



    @property
    def hvac_modes(self):
        return [HVACMode.OFF, HVACMode.HEAT_COOL]



    @property
    def hvac_mode(self):
        operating_mode = self._state["operating_mode"]
        if operating_mode in EUREVIA_HVAC_MODE_TO_HA_HVAC_MODE:
            return EUREVIA_HVAC_MODE_TO_HA_HVAC_MODE[operating_mode]
        else:
            return HVACMode.HEAT_COOL



    async def async_set_hvac_mode(self, hvac_mode):
        await self.update_operating_mode(hvac_mode)



    @property
    def preset_modes(self):
        return list(EUREVIA_PRESET_MODE_TO_HA_PRESET_MODE.values())



    @property
    def preset_mode(self):
        operating_mode = self._state["operating_mode"]
        if operating_mode in EUREVIA_PRESET_MODE_TO_HA_PRESET_MODE:
            return EUREVIA_PRESET_MODE_TO_HA_PRESET_MODE[operating_mode]
        else:
            return PRESET_NONE



    async def async_set_preset_mode(self, preset_mode):
        await self.update_operating_mode(preset_mode)



    async def update_operating_mode(self, operating_mode):
        combined_modes = list(EUREVIA_HVAC_MODE_TO_HA_HVAC_MODE.items()) + list(EUREVIA_PRESET_MODE_TO_HA_PRESET_MODE.items())

        new_operating_mode = next(
            (k for k, v in combined_modes if v == operating_mode),
            None
        )

        if new_operating_mode is not None:
            self._state["operating_mode"] = new_operating_mode
            self._mqtt.publish(self._topic + "/set", json.dumps({"Mode_Active": new_operating_mode, "Mode": new_operating_mode}))
            self.schedule_ha_update()



    async def async_set_temperature(self, **kwargs):
        new_temperature = kwargs.get("temperature")
        if new_temperature is not None:
            self._state["target_temperature"] = new_temperature
            self._mqtt.publish(f"{self._topic}/set", json.dumps({"Stp_Comf": new_temperature}))
            self.schedule_ha_update()



    def update_from_mqtt(self, payload):
        self._state["temperature"] = payload.get("Tmp")
        self._state["humidity"] = payload.get("RH")
        self._state["target_temperature"] = payload.get("Stp_Comf")
        self._state["operating_mode"] = payload.get("Mode_Active", None) or payload.get("Mode")
        self._state["zone_name"] = payload.get("Th_Name", None) or payload.get("Custom_Zone_Name", None) or payload.get("Zone_Name", None)
        self.schedule_ha_update()



    def schedule_ha_update(self):
        if self.hass and self.hass.loop.is_running():
            self.hass.loop.call_soon_threadsafe(self.async_write_ha_state)