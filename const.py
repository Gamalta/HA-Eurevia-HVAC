from homeassistant.components.climate.const import HVACMode
from homeassistant.components.climate import (
    PRESET_COMFORT,
    PRESET_SLEEP,
    PRESET_ECO,
    PRESET_NONE,
)
from enum import IntEnum

DOMAIN = "eurevia-hvac"

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
