schema = {
    "name": "Light controller",
    "module": "esp8266",
    "heartbeat_interval": 10,
    "communication": "mqtt",
    "routes": {
        "cooler_water_intake": {
            "dtype": "bool"
        },
        "exhaust_fan": {
            "dtype": "int",
            "range": [
                0,
                100
            ]
        },
        "led_state": {
            "dtype": "int",
            "values": [
                0,
                1,
                2
            ]
        },
        "cooler_tank_switch": {
            "dtype": "string",
            "values": [
                "release_slowly",
                "flush"
            ]
        }
    },
    "events": {
        "cooler_water_intake": {
            "dtype": "bool"
        },
        "temperature_humidity": {
            "dtype": "dict",
            "schema": {
                "temperature": {
                    "dtype": "float"
                },
                "humidity": {
                    "dtype": "float"
                }
            }
        }
    }
}
