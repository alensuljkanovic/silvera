import os
import locale


def get_root_path():
    """Returns project's root path."""
    path = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
    return path


def get_templates_path():
    """Returns the path to the templates folder."""
    return os.path.join(get_root_path(), "talkie", "generator", "templates")


def get_src_gen_path():
    """Returns the path to the src-gen folder."""
    return os.path.join(get_root_path(), "talkie", "generator", "src-gen")


def decode_byte_str(byte_str):
    """
    Decodes byte string into unicode string.

    Args:
        byte_str(byte): Byte string.

    Returns:
        Unicode string.
    """

    # first try to decode with utf-8 and if that fails try with system default
    for encoding in ("utf-8", locale.getpreferredencoding()):
        try:
            res = byte_str.decode(encoding)
            return res
        except Exception:
            continue
    else:
        return str(byte_str)


def create_dependency_obj(serv_obj, connection):
    """Creates Dependecy object from given ServiceDecl object."""
    use = {c.method_name: (c.failure_pattern, c.fallback_method)
           for c in connection.circuit_break_defs}

    functions = [f.clone() for f in serv_obj.api.functions if f.name in use]

    for func in functions:
        func.cb_pattern = use[func.name][0]
        fallback = use[func.name][1]

        if fallback:
            func.cb_fallback = fallback
        else:
            func.cb_fallback = "%s_fallback" % func.name

    return Dependency(serv_obj.name, serv_obj.port, functions)


class Dependency:
    """This object describes service's dependency on another service"""

    def __init__(self, name, port, functions):
        self.name = name
        self.port = port
        self.functions = functions
        for f in self.functions:
            f.parent = self

    def resolve_rest(self, rest_info):
        myinfo = rest_info[self.name]
        path = myinfo["path"]
        methods = myinfo["methods"]

        for m in methods:
            name = m["name"]
            mapping = m["path"]

            for f in self.functions:
                if f.name == name:
                    f.dep_rest_path = path + mapping
