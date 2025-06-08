from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature
from homeassistant.components.climate.const import HVACMode, PRESET_NONE
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN, EUREVIA_HVAC_MODE_TO_HA_HVAC_MODE, EUREVIA_PRESET_MODE_TO_HA_PRESET_MODE
from .coordinator import EureviaCoordinator

async def async_setup_entry(hass, entry, async_add_entities):
    async def add_coordinator(device_id):
        coordinator = hass.data[DOMAIN]["coordinators"][device_id]
        if all(k in coordinator.data for k in ("ID", "Mode_Active", "Stp_Comf", "Zone_Name")):
            async_add_entities([EureviaClimate(coordinator)])

    for device_id in hass.data[DOMAIN]["coordinators"]:
        await add_coordinator(device_id)

    async_dispatcher_connect(hass, f"{DOMAIN}_new_device", add_coordinator)


class EureviaClimate(CoordinatorEntity, ClimateEntity):

    def __init__(self, coordinator: EureviaCoordinator):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._device_id = coordinator.device_id

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": f"Eurevia HVAC {self.zone_name}",
            "manufacturer": "Eurevia",
            "model": "HVAC",
        }

    @property
    def unique_id(self):
        return self._device_id

    @property
    def zone_name(self):
        data = self._coordinator.data
        return data.get("Th_Name") or data.get("Custom_Zone_Name") or data.get("Zone_Name")

    @property
    def name(self):
        return self.zone_name

    @property
    def current_temperature(self):
        return self._coordinator.data.get("Tmp")

    @property
    def current_humidity(self):
        return self._coordinator.data.get("RH")

    @property
    def temperature_unit(self):
        return UnitOfTemperature.CELSIUS

    @property
    def target_temperature(self):
        return self._coordinator.data.get("Stp_Comf")

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
        operating_mode = self._coordinator.data.get("Mode_Active") or self._coordinator.data.get("Mode")
        return EUREVIA_HVAC_MODE_TO_HA_HVAC_MODE.get(operating_mode, HVACMode.HEAT_COOL)

    @property
    def preset_modes(self):
        return list(EUREVIA_PRESET_MODE_TO_HA_PRESET_MODE.values())

    @property
    def preset_mode(self):
        operating_mode = self._coordinator.data.get("Mode_Active") or self._coordinator.data.get("Mode")
        return EUREVIA_PRESET_MODE_TO_HA_PRESET_MODE.get(operating_mode, PRESET_NONE)

    async def async_set_temperature(self, **kwargs):
        new_temperature = kwargs.get("temperature")
        if new_temperature is not None:
            await self._coordinator.publish("set", {"Stp_Comf": new_temperature})

    async def async_set_hvac_mode(self, hvac_mode):
        await self._update_operating_mode(hvac_mode)

    async def async_set_preset_mode(self, preset_mode):
        await self._update_operating_mode(preset_mode)

    async def _update_operating_mode(self, operating_mode):
        reverse_map = {v: k for k, v in {**EUREVIA_HVAC_MODE_TO_HA_HVAC_MODE, **EUREVIA_PRESET_MODE_TO_HA_PRESET_MODE}.items()}
        new_operating_mode = reverse_map.get(operating_mode)

        if new_operating_mode is not None:
            await self._coordinator.publish("set", {"Mode": new_operating_mode, "Mode_Active": new_operating_mode})