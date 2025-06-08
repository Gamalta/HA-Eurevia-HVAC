SENSOR_DEFINITIONS = [
    {"field": "Voltage", "name": "Voltage", "unit": "V", "device_class": "voltage"},
    {"field": "Voltage_percent", "name": "Voltage %", "unit": "%", "device_class": None},
    {"field": "LQI", "name": "LQI", "unit": None, "device_class": None},
    {"field": "LQI_percent", "name": "LQI %", "unit": "%", "device_class": None},

    {"field": "Water_Temp", "name": "Water Temperature", "unit": "°C", "device_class": "temperature"},
    {"field": "Air_Temp", "name": "Air Temperature", "unit": "°C", "device_class": "temperature"},
]

BINARY_SENSOR_DEFINITIONS = [
    {"field": "Battery_low", "name": "Battery Low", "device_class": "battery"},
]