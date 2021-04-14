"""
This module contains platform data.
"""

# Platform names
from silvera.core import CustomType, TypedList, TypeDef

JAVA = "java"
PYTHON = "python"

# silvera types
VOID = "void"
STRING = "str"
PASSWORD = "pwd"
FLOAT = "float"
DOUBLE = "double"
BOOL = "bool"
i16 = "i16"
i32 = "i32"
i64 = "i64"
INT = "int"
DATE = "date"

# Collections types
LIST = "list"
SET = "set"
DICT = "dict"

# Constants
DYNAMICALLY_TYPED = "dynamically_typed"
TYPES = "types"
COLLECTIONS = "collections"
FILE_EXTENSION = "file_extension"
VERSION = "version"
DEF_RET_VAL = "default_return_value"
MODULE_CASE = "module_case"
NUMB_OF_MODULES = "numb_of_modules"
ONE_MODULE = 1
MULT_MODULES = 2
INIT_FILE = "init_file"

ROLE_SERVER = "server"
ROLE_CLIENT = "client"

platforms = {
    JAVA: {
        DYNAMICALLY_TYPED: False,
        FILE_EXTENSION: ".java",
        NUMB_OF_MODULES: MULT_MODULES,

        TYPES: {
            INT: "java.lang.Integer",
            i16: "java.lang.Integer",
            i32: "java.lang.Integer",
            i64: "java.lang.Integer",
            FLOAT: "java.lang.Double",
            DOUBLE: "java.lang.Double",
            STRING: "java.lang.String",
            BOOL: "java.lang.Boolean",
            VOID: "void",
            DATE: "java.util.Date",
            PASSWORD: "java.lang.String"
        },

        COLLECTIONS: {
            LIST: "java.util.List",
            SET: "java.util.Set",
            DICT: "java.util.Map"
        },

        DEF_RET_VAL: {
            INT: 0,
            i16: 0,
            i32: 0,
            i64: 0,
            FLOAT: 0.0,
            DOUBLE: 0.0,
            STRING: '""',
            PASSWORD: '""',
            BOOL: "false",
            VOID: "",
            DATE: "new java.util.Date()",
            LIST: "java.util.Collections.emptyList()",
            SET: "java.util.Collections.emptySet()",
            DICT: "java.util.Collections.emptyMap()"

        }

    },

    PYTHON: {
        DYNAMICALLY_TYPED: True,
        FILE_EXTENSION: ".py",
        # MODULE_CASE: camelcase_to_snakecase,
        NUMB_OF_MODULES: ONE_MODULE,
        INIT_FILE: "__init__",
        TYPES: {
            INT: "int",
            i16: "int",
            i32: "int",
            i64: "int",
            FLOAT: "float",
            DOUBLE: "double",
            STRING: "str",
            BOOL: "bool",
            VOID: "",
            PASSWORD: "str"
        },

        COLLECTIONS: {
            LIST: "list",
            SET: "set",
            DICT: "dict"
        },

        DEF_RET_VAL: {
            i16: 0,
            i32: 0,
            i64: 0,
            FLOAT: 0.0,
            DOUBLE: 0.0,
            STRING: "",
            PASSWORD: "",
            BOOL: True,
            VOID: "",
            LIST: "[]",
            SET: "{}",
            DICT: "{}"
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
    """Converts silvera type to a platform type."""
    mappings = get_type_mappings(platform)
    return mappings[_type]


def convert_complex_type(platform, _type):
    """Converts complex silvera object to a platform type"""

    if isinstance(_type, TypeDef):
        return _type.name

    try:
        return convert_type(platform, _type)
    except KeyError:
        collections = platforms[platform][COLLECTIONS]
        if isinstance(_type, TypedList):
            tl_type = convert_complex_type(platform, _type.type)
            return collections[LIST] + "<" + tl_type + ">"


def convert_list_to_array(platform, lst):
    if isinstance(lst, TypedList):
        return lst.type.name + "[]"
    return "Object[]"


def get_def_ret_val(platform, _type):
    """Returns the default return value for given platform and data type"""
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


def get_init_file(platform):
    """Returns the init file."""
    return platforms[platform][INIT_FILE]


def is_collection(_type):
    if isinstance(_type, TypedList):
        return True
    return False
