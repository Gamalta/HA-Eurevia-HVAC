from homeassistant.components.climate.const import HVACMode
from homeassistant.components.climate import (
    PRESET_COMFORT,
    PRESET_SLEEP,
    PRESET_ECO,
)
from enum import IntEnum

DOMAIN = "eurevia-hvac"
PLATFORMS = ["climate", "sensor", "binary_sensor"]
MQTT_TOPIC = "local/hvac/devices"

class EureviaMode(IntEnum):
    """HVAC mode for eurevia climate devices."""
    OFF = 0

EUREVIA_HVAC_MODE_TO_HA_HVAC_MODE: dict[int, str] = {
    0: HVACMode.OFF     # off
}

EUREVIA_PRESET_MODE_TO_HA_PRESET_MODE: dict[int, str] = {
    3: PRESET_SLEEP,    # reduit
    1: PRESET_COMFORT,  # comfort
    2: PRESET_ECO       # eco
}
