SENSOR_DEFINITIONS = [
    {"field": "Tmp", "name": "Temperature", "unit": "°C", "device_class": "temperature"},
    {"field": "RH", "name": "Humidity", "unit": "%", "device_class": "humidity"},
    {"field": "Voltage", "name": "Voltage", "unit": "V", "device_class": "voltage"},
    {"field": "Voltage_percent", "name": "Voltage %", "unit": "%", "device_class": None},
    {"field": "LQI", "name": "LQI", "unit": None, "device_class": None},
    {"field": "LQI_percent", "name": "LQI %", "unit": "%", "device_class": None},
]

BINARY_SENSOR_DEFINITIONS = [
    {"field": "Battery_low", "name": "Battery Low", "device_class": "battery"},
]