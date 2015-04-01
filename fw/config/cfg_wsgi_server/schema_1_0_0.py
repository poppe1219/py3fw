# @PydevCodeAnalysisIgnore, pylint: disable=missing-docstring

CONFIG_SCHEMA = {
    "type": "object",
    "$schema": "http://json-schema.org/draft-04/schema",
    "properties": {
        "@api": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "pattern": "jconf",
                    "default": "jconf"
                },
                "name": {
                    "type": "string",
                    "pattern": "WsgiServer",
                    "default": "WsgiServer"
                },
                "version": {
                    "type": "string",
                    "pattern": "^1\\.0\\.0$",
                    "default": "1.0.0"
                },
                "prev_version": {
                    "type": "null",
                    "default": None
                }
            },
            "required": [
                "type",
                "name",
                "version",
                "prev_version"
            ]
        },
        "@config_id": {
            "type": "string"
        },
        "server": {
            "type": "object",
            "properties": {
                "address": {
                    "type": "string",
                    "default": "localhost",
                    "anyOf": [
                        {
                            "pattern": (
                                "^([01]?\\d\\d?|2[0-4]\\d|25[0-5])"
                                "\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])"
                                "\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])"
                                "\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])$"
                                )
                        },
                        {
                            "enum": [
                                "localhost"
                            ]
                        }
                    ]
                },
                "port": {
                    "type": "number",
                    "multipleOf": 1.0,
                    "minimum": 1,
                    "maximum": 65535,
                    "default": 9000
                }
            }
        }
    },
    "requried": [
        "@api",
        "@config_id",
        "content"
    ]
}
