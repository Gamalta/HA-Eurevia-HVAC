from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .models import BINARY_SENSOR_DEFINITIONS
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    async def add_coordinator(coordinator):
        entities = []
        for definition in BINARY_SENSOR_DEFINITIONS:
            if(definition["field"] in coordinator.data):
                entities.append(EureviaBinarySensor(coordinator, definition))
        async_add_entities(entities)

    for coordinator in hass.data[DOMAIN]["coordinators"].values():
        await add_coordinator(coordinator)

    async_dispatcher_connect(hass, f"{DOMAIN}_new_device", add_coordinator)

class EureviaBinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, definition):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._definition = definition
        self._topic_id = coordinator.topic_id

        self._attr_device_class = definition.get("device_class")

    @property
    def unique_id(self):
        return f"{self.zone_name}_{self._definition["field"]}"


    @property
    def zone_name(self):
        data = self._coordinator.data
        return data.get("Th_Name") or data.get("Custom_Zone_Name") or data.get("Zone_Name")

    @property
    def device_info(self) -> DeviceInfo:
        return {
            "identifiers": {(DOMAIN, self._topic_id)},
            "name": f"Eurevia HVAC {self.zone_name}",
            "manufacturer": "Eurevia",
            "model": "HVAC",
        }

    @property
    def is_on(self):
        return self._coordinator.data.get(self._definition["field"])