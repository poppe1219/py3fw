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
                    "pattern": "WsgiApps",
                    "default": "WsgiApps"
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
        "parent_path": {
            "type": "string"
        },
        "path": {
            "type": ["null", "string"]
        },
        "default_user": {
            "type": ["null", "string"]
        },
        "default_email": {
            "type": ["null", "string"]
        },
        "name": {
            "type": "string"
        },
        "nodes": {
            "type": "object",
            "additionalProperties": False,
            "patternProperties": {
                "^[.]+$": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": 255
                        },
                        "path": {
                            "type": "string",
                            "minLength": 1
                        },
                        "type": {
                            "type": "string",
                            "enum": [
                                "file",
                                "dir"
                            ]
                        },
                        "configType": {
                            "type": "string"
                        },
                        "ctime": {
                            "type": "number"
                        },
                        "mtime": {
                            "type": "number"
                        },
                        "size": {
                            "type": "number",
                            "minimum": 0,
                            "multipleOf": 1.0  # Force integer values only.
                        },
                        "content": {
                            "type": "array",
                            "items": {
                                "type":"string",
                                "pattern": "^[.]+$"
                            },
                            "uniqueItems": True
                        }
                    },
                    "required": [
                        "name",
                        "type"
                    ]
                }
            }
        }
    },
    "requried": [
        "@api",
        "@config_id",
        "root_path",
        "tree_id"
    ]
}
