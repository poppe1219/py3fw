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
                    "pattern": "FileTree",
                    "default": "FileTree"
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
        "root_path": {
            "type": "string"
        },
        "tree_id": {
            "type": "string",
            "minLength": 1
        },
        "path": {
            "type": "string",
            "minLength": 1
        },
        "visible_name": {
            "type": "string"
        },
        "content": {
            "type": "array",
            "items": {
                "$ref": "#/@definitions/file_tree_node"
            },
            "uniqueItems": True
        }
    },
    "requried": [
        "@api",
        "@config_id",
        "root_path",
        "tree_id"
    ],
    "@definitions": {
        "file_tree_node": {
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
                        "$ref": "#/@definitions/file_tree_node"
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
