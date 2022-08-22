schema = {
    "name": "Smart Air Cooler",
    "module": "esp8266",
    "heartbeat_interval": 10,
    "communication": "mqtt",
    "ui_component": "SmartAirCooler",
    "routes": {
        "get": [
            "fan_speed",
            "water_intake",
            "cooling_pump",
            "water_level",
            "led_state",
            "water_drain",
            "temperature",
            "humidity"
        ],
        "post": {
            "fan_speed": {"dtype": "int", "range": [0, 100]},
            "water_intake": {"dtype": "bool"},
            "cooling_pump": {"dtype": "bool"},
            "water_level": {"dtype": "int", "range": [0, 100]},
            "led_state": {"dtype": "int", "values": [0, 1, 2]},
            "water_drain": {
                "dtype": "string",
                "values": ["release_slowly", "flush"],
            },
        }
    },
    "events": {
        "temperature_humidity": {
            "dtype": "dict",
            "schema": {
                "temperature": {"dtype": "float"},
                "humidity": {"dtype": "float"},
            },
        },
    },
}
