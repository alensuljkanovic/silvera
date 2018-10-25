"""
This module contains the implementation of talkie IDL.
"""
from talkie.const import REST
import urllib.parse as url_parser


class Module:

    def __init__(self, decls):
        self.decls = decls

    @property
    def service_instances(self):
        for decl in self.decls:
            if isinstance(decl, ServiceDecl):
                for i in range(decl.num_of_instances):
                    yield Service(decl, i)

    @property
    def service_registries(self):
        for decl in self.decls:
            if isinstance(decl, ServiceRegistryDecl):
                yield decl

    @property
    def config_servers(self):
        for decl in self.decls:
            if isinstance(decl, ConfigServerDecl):
                yield decl

    def add_rest_info(self, rest_info):
        """Goes through all services who use REST as a communication style and
        adds mappings."""
        if rest_info is None:
            return

        for decl in self.decls:
            if isinstance(decl, ServiceDecl) and decl.uses_rest:
                try:
                    d = rest_info[decl.name]
                    decl.resolve_rest(d)
                except KeyError:
                    raise RuntimeError("REST mapping not defined for service"
                                       " %s" % decl.name)


class ServiceDecl:

    def __init__(self, parent=None, name=None, version=None, port=None,
                 config_server=None, service_registry=None, lang=None,
                 packaging=None, host=None, num_of_instances=None,
                 comm_style=None, api=None,):
        self.parent = parent
        self.name = name
        self.version = version
        self.port = port
        self.config_server = config_server
        self.service_registry = service_registry
        self.lang = lang
        self.packaging = packaging
        self.host = host
        self.num_of_instances = num_of_instances
        self.comm_style = comm_style
        self.api = api
        self.comm_style = comm_style

    @property
    def uses_rest(self):
        return self.comm_style == REST

    def resolve_rest(self, rest_info):
        pass
        path = rest_info["path"]
        methods = rest_info["methods"]
        for d in methods:
            name = d["name"]
            mapping = d["path"]
            for func in self.api.functions:
                if func.name == name:
                    func.add_rest_mappings(path + mapping)


class Service:

    def __init__(self, service_decl, idx=None):
        self.type = service_decl
        self.idx = idx
        if idx is not None:
            self.port = service_decl.port + idx
        else:
            self.port = None

    @property
    def name(self):
        return self.type.name

    @property
    def version(self):
        return self.type.version


class ServiceRegistryDecl:

    def __init__(self, parent, name=None, tool=None, port=None, uri=None,
                 client_mode=False, version=None):
        self.name = name
        self.version = version
        self.parent = parent
        self.tool = tool
        self.uri = uri
        self.port = port
        self.client_mode = client_mode

    @property
    def url(self):
        return "{}:{}/{}".format(self.uri, self.port, self.tool)


class ConfigServerDecl:

    def __init__(self, parent, name=None, version=None, port=None,
                 search_path=None):
        self.parent = parent
        self.name = name
        self.version = version
        self.search_path = search_path
        self.port = port


class Function:

    def __init__(self, parent, name=None, comm_type=None, ret_type=None,
                 params=None):
        self.parent = parent
        self.name = name
        self.comm_type = comm_type
        self.ret_type = ret_type
        self.params = params if params else []
        self.rest_path = None

    def add_rest_mappings(self, mapping):

        import re
        placeholders = re.findall(r'\{(.*?)\}', mapping)
        for param in self.params:
            param.url_placeholder = param.name in placeholders

        for placeholder in placeholders:
            if placeholder not in {p.name for p in self.params}:
                raise TypeError("Placeholder '%s' not found in function "
                                "parameters!" % placeholder)

        # Look for query parameters in the URL
        parsed = url_parser.urlparse(mapping)
        url_params = url_parser.parse_qs(parsed.query)
        for param in self.params:
            param.query_param = param.name in url_params
            print(param.name, param.query_param)

        for p in url_params:
            if p not in {p.name for p in self.params}:
                raise TypeError("Query parameter '%s' not found in "
                                "function parameters" % p)

        self.rest_path = mapping


class FunctionParameter:

    def __init__(self, parent, name=None, type=None, default=None):
        self.parent = parent
        self.type = type
        self.name = name
        self.default = default
        self.url_placeholder = False
        self.query_param = False


class TypeDef:

    def __init__(self, parent, name=None, inherits=None, fields=None):
        self.parent = parent
        self.name = name
        self.inherits = inherits if inherits else []
        self.fields = fields if fields else []

    def __str__(self):
        return self.name


class DataType:

    def __init__(self, parent):
        self.parent = parent


class CustomType(DataType):

    def __init__(self, parent, type):
        super().__init__(parent)
        self.type = type

    def __str__(self):
        return str(self.type)


class Number(DataType):

    def __init__(self, parent):
        super().__init__(parent)


class Collection(DataType):

    def __init__(self, parent):
        super().__init__(parent)


class Sequence(Collection):

    def __init__(self, parent):
        super().__init__(parent)


class List(Sequence):

    def __init__(self, parent):
        super().__init__(parent)


class TypedList(List):

    def __init__(self, parent, type, len):
        super().__init__(parent)
        self.type = type
        self.len = len

