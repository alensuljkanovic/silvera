"""
This module contains platform data.
"""
from talkie.generator.utils import camelcase_to_snakecase

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
MODULE_CASE = "module_case"
NUMB_OF_MODULES = "numb_of_modules"
ONE_MODULE = 1
MULT_MODULES = 2

ROLE_SERVER = "server"
ROLE_CLIENT = "client"

platforms = {
    JAVA: {
        DYNAMICALLY_TYPED: False,
        FILE_EXTENSION: ".java",
        NUMB_OF_MODULES: MULT_MODULES,
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
        MODULE_CASE: camelcase_to_snakecase,
        NUMB_OF_MODULES: ONE_MODULE,
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


def get_module_name(platform, module_name):
    """Returns the module name in case expected by the platform."""
    platform_desc = platforms[platform]
    if MODULE_CASE in platform_desc:
        func = platform_desc[MODULE_CASE]
        return func(module_name)
    return module_name


def get_numb_of_modules(platform):
    """Returns the number of modules used by the platform."""
    return platforms[platform][NUMB_OF_MODULES]
