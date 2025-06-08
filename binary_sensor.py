from homeassistant.components.binary_sensor import BinarySensorEntity
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
        self._definition = definition
        self._attr_unique_id = f"{coordinator.device_id}_{definition['field']}"
        self._attr_name = f"{definition['name']}"
        self._attr_device_class = definition.get("device_class")

    @property
    def is_on(self):
        return self.coordinator.data.get(self._definition["field"])