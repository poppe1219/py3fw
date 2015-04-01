# @PydevCodeAnalysisIgnore, pylint: disable=missing-docstring

CONFIG_SCHEMA = {
    "type":"object",
    "$schema": "http://json-schema.org/draft-04/schema",
    "properties": {
        "@api": {
            "type":"object",
            "properties": {
                "type": {
                    "type": "string",
                    "pattern": "jconf",
                    "default": "jconf"
                },
                "name": {
                    "type":"string",
                    "pattern": "TestConfig",
                    "default": "TestConfig"
                },
                "version": {
                    "type":"string",
                    "pattern": "^1\\.1\\.0$",
                    "default": "1.1.0"
                },
                "prev_version": {
                    "type": "string",
                    "pattern": "^1\\.0\\.1$",
                    "default": "1.0.1"
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
        "root": {
            "type": "string",
            "pattern": "^[0-9]{3}$",
            "default": "001"
        },
        "nodes": {
            "type":"object",
            "additionalProperties": False,
            "patternProperties": {
                "^[0-9]{3}$": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "pattern": "^[0-9]{3}$"
                        },
                        "content": {
                            "type": "array",
                            "items": {
                                "type":"string",
                                "pattern": "^[0-9]{3}$"
                            }
                        }
                    },
                    "additionalProperties": False,
                    "required": [
                        "id"
                    ]
                }
            },
            "default": {
                "001": {
                    "id": "001"
                }
            }
        }
    },
    "required": [
        "@api",
        "@config_id",
        "root",
        "nodes"
    ]
}
