from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .const import DOMAIN
from .models import SENSOR_DEFINITIONS

async def async_setup_entry(hass, config_entry, async_add_entities):
    async def add_coordinator(coordinator):
        entities = []
        for definition in SENSOR_DEFINITIONS:
            entities.append(EureviaSensor(coordinator, definition))
        async_add_entities(entities)

    for coordinator in hass.data[DOMAIN]["coordinators"].values():
        await add_coordinator(coordinator)

    async_dispatcher_connect(hass, f"{DOMAIN}_new_device", add_coordinator)

class EureviaSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, definition):
        super().__init__(coordinator)
        self._definition = definition
        self._attr_unique_id = f"{coordinator.device_id}_{definition['field']}"
        self._attr_name = f"{definition['name']}"
        self._attr_unit_of_measurement = definition.get("unit")
        self._attr_device_class = definition.get("device_class")

    @property
    def native_value(self):
        return self.coordinator.data.get(self._definition["field"])

    @property
    def device_info(self) -> DeviceInfo:
        return {
            "identifiers": {(DOMAIN, self.coordinator.device_id)},
            "manufacturer": "Eurevia",
            "model": "HVAC",
            "name": f"Eurevia {self.coordinator.device_id}",
        }