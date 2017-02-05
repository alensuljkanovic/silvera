"""
This module contains platform data.
"""

# Platform names
JAVA = "java"
PYTHON = "python"

# talkie IDL types
VOID = "void"
INT = "int"
STRING = "string"
FLOAT = "float"
DOUBLE = "double"
BOOL = "bool"

# Constants
DYNAMICALLY_TYPED = "dynamically_typed"
TYPES = "types"
FILE_EXTENSION = "file_extension"
VERSION = "version"
DEF_RET_VAL = "default_return_value"

platforms = {
    JAVA: {
        DYNAMICALLY_TYPED: False,
        FILE_EXTENSION: ".java",
        TYPES: {
            INT: "int",
            FLOAT: "float",
            DOUBLE: "double",
            STRING: "String",
            BOOL: "boolean",
            VOID: "void"
        },

        DEF_RET_VAL: {
            INT: 0,
            FLOAT: 0.0,
            DOUBLE: 0.0,
            STRING: "",
            BOOL: "true",
            VOID: ""
        }
    },

    PYTHON: {
        DYNAMICALLY_TYPED: True,
        FILE_EXTENSION: ".py",
        TYPES: {
            INT: "int",
            FLOAT: "float",
            DOUBLE: "double",
            STRING: "str",
            BOOL: "bool",
            VOID: ""
        },

        DEF_RET_VAL: {
            INT: 0,
            FLOAT: 0.0,
            DOUBLE: 0.0,
            STRING: "",
            BOOL: True,
            VOID: ""
        }
    }

}


def get_type_mappings(platform):
    """Returns type mappings for a provided platform."""
    types = platforms[platform][TYPES]

    mappings = {}
    for _type in types:
        mappings[_type] = types[_type]
    return mappings


def convert_type(platform, _type):
    """Converts talkie type to a platform type."""
    mappings = get_type_mappings(platform)
    return mappings[_type]


def get_def_ret_val(platform, _type):
    """Returns the default return value for given platform and data type"""
    p = platforms[platform]
    d = p[DEF_RET_VAL]
    ret_val = d[_type]
    return platforms[platform][DEF_RET_VAL][_type]


def get_file_ext(platform):
    """Returns the file extension for a given platform."""
    return platforms[platform][FILE_EXTENSION]


def is_dynamic(platform):
    """Tells if a given platform is a dynamically typed, or not."""
    return platforms[platform][DYNAMICALLY_TYPED]