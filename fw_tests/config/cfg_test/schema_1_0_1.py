# @PydevCodeAnalysisIgnore, pylint: disable=missing-docstring

CONFIG_SCHEMA = {
    "type":"object",
    "$schema": "http://json-schema.org/draft-04/schema",
    "definitions": {
        "content": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "pattern": "^[0-9]{3}$"
                },
                "content": {
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/content"
                    }
                }
            },
            "additionalProperties": False,
            "required": [
                "id"
            ]
        }
    },
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
                    "pattern": "^1\\.0\\.1$",
                    "default": "1.0.1"
                },
                "prev_version": {
                    "type": "string",
                    "pattern": "^1\\.0\\.0$",
                    "default": "1.0.0"
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
            "type":"object",
            "properties": {
                "content": {
                    "type":"array",
                    "items": {
                        "$ref": "#/definitions/content"
                    }
                },
                "id": {
                    "type":"string"
                }
            },
            "additionalProperties": False
        }
    },
    "required": [
        "@api",
        "@config_id",
        "root"
    ]
}
