"""
This module contains the implementation of Silvera DSL.
"""
import os
from silvera.const import REST
import urllib.parse as url_parser


def fqn_to_path(fqn):
    fqns = fqn.split(".")
    path = os.sep.join(fqns[:-1]) + ".tl"
    return path


class Model:
    """Model object"""

    def __init__(self, root_dir, modules=None):
        self.root_dir = root_dir
        self.modules = modules if modules else []

    def modules_dict(self):
        return {m.path: m for m in self.modules}

    def find_by_path(self, path):
        """Returns module from given path.

        Args:
            path (str): path to the Module

        Returns:
            Module
        """
        try:
            modules = self.modules_dict()
            return modules[path]
        except KeyError:
            raise ValueError("Module '%s' not found." % path)

    def find_by_fqn(self, fqn):
        fqns = fqn.split(".")
        path = os.sep.join(fqns[:-1]) + ".tl"
        name = fqns[-1]

        module = self.find_by_path(path)
        return module.decl_by_name(name)


class Module:
    """Object representation of Silvera module

    Module contains declarations of Services, Gateways, Service Registries,
    etc.
    """

    def __init__(self, decls, imports=None, model=None):
        """Initializes object

        Args:
            decls (list): list of declarations within module
            imports (list): list of imports
        """
        self.model = model
        self.imports = imports if imports else []
        self.decls = decls
        self._path = None
        self.name = None

    def __str__(self):
        return self._path

    def __repr__(self):
        return self._path

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, module_path):
        self._path = module_path
        self.name = os.path.basename(module_path)

    def depends_on(self):
        return [self.model.find_by_path(fqn_to_path(i.import_url))
                for i in self.imports]

    @property
    def service_instances(self):
        for decl in self.decls:
            if isinstance(decl, ServiceDecl):
                for i in range(decl.replicas):
                    yield Service(decl, i)

    def service_by_name(self, service_name):
        for decl in self.decls:
            if isinstance(decl, ServiceDecl):
                if decl.name == service_name:
                    return decl
        raise KeyError("Service with name '%s' not found!" % service_name)

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

    @property
    def connections(self):
        for decl in self.decls:
            if decl.__class__.__name__ == "Connection":
                yield decl

    def decl_by_name(self, name):
        for decl in self.decls:
            if hasattr(decl, "name") and decl.name == name:
                return decl

        raise KeyError("Declaration with name '%s' not found!" % name)


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
                 service_registry=None, deployment=None, comm_style=None,
                 extends=None):
        super().__init__(deployment)
        self.parent = parent
        self.extends = extends
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
                 api=None, extends=None):
        super().__init__(parent, name, config_server, service_registry,
                         deployment, comm_style, extends)
        self.api = api
        self.dep_functions = []
        self.dep_typedefs = []

    @property
    def functions(self):
        funcs = [f for f in self.api.functions]
        funcs.extend(self.dep_functions)

        return funcs

    def add_function(self, fnc):
        fnc.parent = self.api
        self.api.functions.append(fnc)

    def get_function(self, func_name):
        for f in self.functions:
            if f.name == func_name:
                return f

        # # Check if function is contained in a service that self depends upon
        # f = None
        # for dep_serv in self.dependencies:
        #     try:
        #         f = dep_serv.get_function(func_name)
        #     except KeyError:
        #         pass
        #
        # if not f:
        raise KeyError("Function not found!")

        # return f

    @property
    def uses_rest(self):
        return self.comm_style == REST

    @property
    def domain_objs(self):
        return {obj.name: obj for obj in self.api.typedefs}

    def __str__(self):
        return "ServiceDecl: %s" % self.name


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
    def __init__(self, parent, name=None, ret_type=None, params=None,
                 annotation=None):
        self.parent = parent
        self.name = name
        self.ret_type = ret_type
        self.params = params if params else []
        self.rest_path = None
        self.dep = None
        self.http_verb = None
        self.cb_pattern = None
        self.cb_fallback = None
        self.annotation = annotation

    @property
    def service_name(self):
        if self.dep:
            return self.dep.parent.parent.name
        return self.parent.parent.name

    @property
    def service_fqn(self):
        if self.dep:
            service = self.dep.parent.parent
            module = service.parent
        else:
            service = self.parent.parent
            module = service.parent
        return "{}.{}".format(module.path.replace(".tl", ""), service.name)

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
        ann = self.annotation
        if self.annotation:
            ann = Annotation(None, ann.method, ann.mapping)

        f = Function(None, self.name, self.ret_type, params, ann)
        f.http_verb = self.http_verb
        return f

    def __str__(self):
        return "Function %s" % self.name


class FunctionParameter:
    """Object representation of function parameter."""
    def __init__(self, parent, name=None, type=None, default=None,
                 name_mapping=None):
        self.parent = parent
        self.type = type
        self.name = name
        self.default = default
        self.name_mapping = name_mapping
        self.url_placeholder = False
        self.query_param = False

    def clone(self):
        return FunctionParameter(None, self.name, self.type, self.default,
                                 self.name_mapping)


class Annotation:

    def __init__(self, parent, method=None, mapping=None):
        self.parent = parent
        self.method = method
        self.mapping = mapping

    def clone(self):
        return Annotation(None, self.method, self.mapping)


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
