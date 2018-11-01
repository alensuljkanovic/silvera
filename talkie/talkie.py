"""
This module contains the implementation of talkie IDL.
"""
from talkie.const import REST
import urllib.parse as url_parser


class Module:
    """Object representation of Talkie module

    Module contains declarations of Services, Gateways, Service Registries,
    etc.
    """

    def __init__(self, decls):
        """Initializes object

        Args:
            decls (list): list of declarations within module
        """
        self.decls = decls

    @property
    def service_instances(self):
        for decl in self.decls:
            if isinstance(decl, ServiceDecl):
                for i in range(decl.replicas):
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

        rest_serv = [d for d in self.decls
                     if isinstance(d, ServiceDecl) and d.uses_rest]
        for decl in rest_serv:
            try:
                d = rest_info[decl.name]
                decl.resolve_rest(d)
            except KeyError:
                raise RuntimeError("REST mapping not defined for service"
                                   " %s" % decl.name)

        for decl in rest_serv:
            for dep in decl.dependencies:
                dep.resolve_rest(rest_info)


class Deployable:
    """Base class for all deployable objects"""
    def __init__(self, deployment=None):
        self.deployment = deployment

    @property
    def version(self):
        return self.deployment.version

    @property
    def port(self):
        return self.deployment.port

    @property
    def url(self):
        return self.deployment.url

    @property
    def replicas(self):
        return self.deployment.replicas

    @property
    def lang(self):
        return self.deployment.lang

    @property
    def host(self):
        return self.deployment.host


class ServiceObject(Deployable):
    """Base class for all services

    Contains information about deployment, communication style, etc.
    """

    def __init__(self, parent=None, name=None, config_server=None,
                 service_registry=None, deployment=None, comm_style=None):
        super().__init__(deployment)
        self.parent = parent
        self.name = name
        self.config_server = config_server
        self.service_registry = service_registry
        self.comm_style = comm_style

        # Services upon whom this service depends on.
        # Depedencies are defined by creating connections towards other
        # services in .tl file.
        self.dependencies = []


class APIGateway(ServiceObject):
    """Special kind of service that provides single entry point to a cluster
    of other services.
    """
    def __init__(self, parent=None, name=None, config_server=None,
                 service_registry=None, deployment=None, comm_style=None,
                 gateway_for=None):
        super().__init__(parent, name, config_server, service_registry,
                         deployment, comm_style)

        self._gateway_for = gateway_for

    @property
    def gateway_for(self):
        return [(g.service, g.url) for g in self._gateway_for]


class ServiceDecl(ServiceObject):
    """Service declaration object"""

    def __init__(self, parent=None, name=None, config_server=None,
                 service_registry=None, deployment=None, comm_style=None,
                 api=None):
        super().__init__(parent, name, config_server, service_registry,
                         deployment, comm_style)
        self.api = api

    @property
    def uses_rest(self):
        return self.comm_style == REST

    def resolve_rest(self, rest_info):
        path = rest_info["path"]
        methods = rest_info["methods"]
        for d in methods:
            name = d["name"]
            mapping = d["path"]
            for func in self.api.functions:
                if func.name == name:
                    func.add_rest_mappings(path + mapping)

            dep_func = [f for d in self.dependencies for f in d.functions]
            for func in dep_func:
                if func.name == name:
                    func.add_rest_mappings(path + mapping)


class Service:
    """Object of this class represents an instance of a service that is of
    given ServiceDecl type.
    """
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
        return self.type.deployment.version


class ServiceRegistryDecl(Deployable):
    """Registry of services. Contains info about their status (health),
    location, number of instances, etc.
    """

    def __init__(self, parent, name=None, tool=None,
                 client_mode=False, deployment=None):
        super().__init__(deployment)
        self.name = name
        self.parent = parent
        self.tool = tool
        self.client_mode = client_mode

class ConfigServerDecl(Deployable):
    """A special service that keep configuration files that are being used by
    other services.
    """
    def __init__(self, parent, name=None, search_path=None, deployment=None):
        super().__init__(deployment)

        self.parent = parent
        self.name = name
        self.search_path = search_path


class Function:
    """Object representation of function declaration."""
    def __init__(self, parent, name=None, ret_type=None, params=None):
        self.parent = parent
        self.name = name
        self.ret_type = ret_type
        self.params = params if params else []
        self.rest_path = None
        self.cb_pattern = None
        self.cb_fallback = None
        self.dep_rest_path = None

    def add_rest_mappings(self, mapping):

        import re
        placeholders = re.findall(r'\{(.*?)\}', mapping)
        for param in self.params:
            param.url_placeholder = param.name in placeholders

        for placeholder in placeholders:
            if placeholder not in {p.name for p in self.params}:
                raise TypeError("Placeholder '%s' not found in function "
                                "parameters for mapping '%s'!" %
                                (placeholder, mapping))

        # Look for query parameters in the URL
        parsed = url_parser.urlparse(mapping)
        url_params = url_parser.parse_qs(parsed.query)
        for param in self.params:
            param.query_param = param.name in url_params

        for p in url_params:
            if p not in {p.name for p in self.params}:
                raise TypeError("Query parameter '%s' not found in "
                                "function parameters" % p)

        self.rest_path = mapping

    def clone(self):
        params = [p.clone() for p in self.params]
        return Function(None, self.name, self.ret_type, params)


class FunctionParameter:
    """Object representation of function parameter."""
    def __init__(self, parent, name=None, type=None, default=None):
        self.parent = parent
        self.type = type
        self.name = name
        self.default = default
        self.url_placeholder = False
        self.query_param = False

    def clone(self):
        return FunctionParameter(None, self.name, self.type, self.default)


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

