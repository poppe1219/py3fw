# @PydevCodeAnalysisIgnore, pylint: disable=missing-docstring

CONFIG_SCHEMA = {
    "type":"object",
    "$schema": "http://json-schema.org/draft-04/schema",
    "definitions": {
        "child_node": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "pattern": "^[0-9]{3}$"
                },
                "child_nodes": {
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/child_node"
                    }
                }
            },
            "additionalProperties": False,
            "required": [
                "id"
            ]
        }
    },
    "properties":{
        "@api": {
            "type":"object",
            "properties":{
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
        "root": {
            "type":"object",
            "properties": {
                "child_nodes": {
                    "type":"array",
                    "items": {
                        "$ref": "#/definitions/child_node"
                    }
                },
                "id": {
                    "type":"string"
                }
            },
            "additionalProperties": False,
        }

    },
    "required": [
        "@api",
        "@config_id",
        "root"
    ]
}
