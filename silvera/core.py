"""
This module contains the implementation of Silvera DSL.
"""
import os
# from silvera.const import REST
import urllib.parse as url_parser
from collections import defaultdict


def fqn_to_path(fqn):
    fqns = fqn.split(".")
    path = os.sep.join(fqns[:-1]) + ".si"
    return path


class Model:
    """Model object"""

    def __init__(self, root_dir, modules=None):
        super().__init__()
        self.root_dir = root_dir
        self.modules = modules if modules else []
        self.msg_pool = None
        self.msg_brokers = {}

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
        path = os.sep.join(fqns[:-1]) + ".si"
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
        super().__init__()
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
    def services(self):
        for decl in self.decls:
            if isinstance(decl, ServiceDecl):
                yield decl

    @property
    def service_instances(self):
        for decl in self.decls:
            if isinstance(decl, ServiceDecl):
                for i in range(decl.replicas):
                    yield Service(decl, i)

    @property
    def service_decls(self):
        for decl in self.decls:
            if isinstance(decl, ServiceDecl):
                yield decl

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
    def api_gateways(self):
        for decl in self.decls:
            if isinstance(decl, APIGateway):
                yield decl

    @property
    def dependencies(self):
        for decl in self.decls:
            if decl.__class__.__name__ == "Dependency":
                yield decl

    @property
    def msg_brokers(self):
        for decl in self.decls:
            if isinstance(decl, MessageBroker):
                yield decl

    def decl_by_name(self, name):
        for decl in self.decls:
            if hasattr(decl, "name") and decl.name == name:
                return decl

        raise KeyError("Declaration with name '%s' not found!" % name)


class Deployable:
    """Base class for all deployable objects"""
    def __init__(self, deployment=None, **kwargs):
        super().__init__(**kwargs)
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


class Deployment:
    """Deployment info container."""

    def __init__(self, parent, version=None, url=None, port=None,
                 lang=None, packaging=None, host=None, replicas=None,
                 restart_policy=None):
        super().__init__()
        self.version = version if version else "0.0.1b"
        self.url = url if url else "http://localhost"
        self.port = port
        self.lang = lang if lang else "java"
        self.packaging = packaging if packaging else "jar"
        self.host = host if host else "PC"
        self.replicas = replicas if replicas is not None else 1
        self.restart_policy = restart_policy


class MessageBroker:
    """Message broker object.

    Its sole responsibility is to deliver messages to a destination. The
    number of channels is fixed.
    """
    def __init__(self, parent, name, channels):
        super().__init__()
        self.parent = parent
        self.name = name
        self._channels = channels
        self._consumers_per_ch = defaultdict(list)
        self._producers_per_ch = defaultdict(list)

    @property
    def channels(self):
        """Returns dict of all channels defined within broker

        Returns:
            dict
        """
        return {c.name: c for c in self._channels}

    def register_consumer(self, channel_name, consumer):
        """Register consumer to a channel with a given name.

        Args:
            channel_name (str): channel name
            consumer (Function): API function that consumes messages from the
                channel
        """
        self._consumers_per_ch[channel_name].append(consumer)

    def register_producer(self, channel_name, producer):
        """Register producer to a channel with a given name.

        Args:
            channel_name (str): channel name
            producer (Function): API function that produces messages for the
                channel
        """
        self._producers_per_ch[channel_name].append(producer)


class MessagePool:
    """Object that contains definitions of all messages used throught the
    system."""
    def __init__(self, parent, groups):
        super().__init__()
        self.parent = parent
        self.groups = groups

    @property
    def messages(self):
        """Returns list of all messages defined in message pool

        Returns:
            list
        """
        def _recurse(groups, messages=None):
            """Go recursively through groups and collect messages"""
            if messages is None:
                messages = []

            for item in groups:
                if isinstance(item, MessageGroup):
                    if item.messages:
                        messages.extend(item.messages)
                    _recurse(item.groups, messages)

            return messages

        return _recurse(self.groups)

    def get_all_groups(self):
        """Returns the list of all MessageGroup objects inside the message
        pool

        Returns:
            list
        """
        def _recurse(groups, result=None):
            """Go recursively through groups and collect messages"""
            if result is None:
                result = []

            for item in groups:
                if isinstance(item, MessageGroup):
                    result.append(item)
                    _recurse(item.groups, result)

            return result

        return _recurse(self.groups)

    def get(self, msg_fqn):

        for m in self.messages:
            if m.fqn == msg_fqn:
                return m

        raise ValueError("Message with given FQN not found in message pool: "
                         "%s" % msg_fqn)


class MsgFQN:

    def __init__(self, parent, name):
        super().__init__()
        self.parent = parent
        self.name = name

    @property
    def fqn(self):
        """Returns FQN of a message

        Returns:
            str
        """
        def _recurse_up(item, path=None):
            if path is None:
                path = []

            if isinstance(item, MessagePool):
                return path

            path.append(item.name)
            return _recurse_up(item.parent, path)

        fqn = _recurse_up(self.parent)
        if fqn:
            return ".".join(reversed(fqn)) + "." + self.name
        else:
            return self.name

    @property
    def msg_pool(self):
        """Returns reference to a MessagePool to which this object belongs."""
        def _recurse_up(item):
            if isinstance(item, MessagePool):
                return item

            return _recurse_up(item.parent)

        return _recurse_up(self)


class DocstringContainer:

    def __init__(self, docstring=None, **kwargs):
        super().__init__(**kwargs)
        self.docstring = docstring


class MessageGroup(MsgFQN):

    def __init__(self, parent, name, groups=None, messages=None):
        super().__init__(parent=parent, name=name)
        self.groups = groups
        self.messages = messages

    @property
    def messages_dict(self):
        return {m.name: m for m in self.messages}


class Message(MsgFQN):
    """Message object"""
    def __init__(self, parent, name, fields=None, annotations=None):
        super().__init__(parent=parent, name=name)
        self.fields = fields if fields else []
        self.annotations = annotations if annotations else []

    def __str__(self):
        return "Message: %s" % self.fqn

    def __repr__(self):
        return str(self)


class MessageChannel:
    """Message channel object."""
    def __init__(self, parent, name, msg_type, annotations=None):
        self.parent = parent
        self.name = name
        self.msg_type = msg_type
        self.annotations = annotations if annotations else []
        self.persistent = False

    def is_p2p(self):
        """Returns True if channel is Point-to-Point channel. False otherwise.

        Returns:
            bool
        """
        for ann in self.annotations:
            if ann == "@p2p":
                return True
        return False

    @property
    def persistent(self):
        for ann in self.annotations:
            if hasattr(ann, "timeout"):
                return True
        return False


class ServiceObject(Deployable, DocstringContainer):
    """Base class for all services

    Contains information about deployment, communication style, etc.
    """

    def __init__(self, parent=None, name=None, config_server=None,
                 service_registry=None, deployment=None, comm_style=None,
                 extends=None, docstring=None):
        super().__init__(deployment=deployment, docstring=docstring)
        self.parent = parent
        self.extends = extends
        self.name = name
        self.config_server = config_server
        self.service_registry = service_registry
        self.comm_style = comm_style

        # Services upon whom this service depends on.
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

        self.gateway_for = gateway_for


class ServiceDecl(ServiceObject):
    """Service declaration object"""

    def __init__(self, parent=None, name=None, config_server=None,
                 service_registry=None, deployment=None, comm_style=None,
                 api=None, extends=None, handlers=None, docstring=None):
        super().__init__(parent, name, config_server, service_registry,
                         deployment, comm_style, extends, docstring=docstring)
        self.api = api
        self.handlers = handlers
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
        raise KeyError("Function not found!")

    def has_async(self):
        for f in self.api.functions:
            if f.is_async():
                return True
        return False

    @property
    def domain_objs(self):
        return {obj.name: obj for obj in self.api.typedefs}

    def __str__(self):
        return "ServiceDecl: %s" % self.name

    def __repr__(self):
        return str(self)

    @property
    def consumes(self):
        """Returns dict where for each message is shown from which channel
        the message is consumed.

        Returns:
            dict
        """
        cons = defaultdict(list)
        internal = self.api.internal
        if not internal:
            return cons

        for f in internal.functions:
            for ann in f.msg_annotations:
                if isinstance(ann, ConsumerAnnotation):
                    for subscr in ann.subscriptions:
                        cons[subscr.message].append(subscr.channel)
        return cons

    @property
    def f_consumers(self):
        """Returns list of all functions that consume messages from channels.

        Returns:
            list
        """
        cons = set()
        internal = self.api.internal
        if not internal:
            return cons

        for f in internal.functions:
            for ann in f.msg_annotations:
                if isinstance(ann, ConsumerAnnotation):
                    for subscr in ann.subscriptions:
                        cons.add(f)

        return sorted(cons, key=lambda f: f.name)

    @property
    def produces(self):
        """Returns dict where for each message is shown to which channel
        the message is published.

        Returns:
            dict
        """
        prods = defaultdict(list)
        for f in self.api.functions:
            for ann in f.msg_annotations:
                if isinstance(ann, ProducerAnnotation):
                    for subscr in ann.subscriptions:
                        prods[subscr.message].append(subscr.channel)

        for t in self.api.typedefs:
            for msg, values in t.produces.items():
                prods[msg].append(values)
        return prods

    @property
    def consumers_per_message(self):
        cons = defaultdict(set)
        internal = self.api.internal
        if not internal:
            return cons

        for f in internal.functions:
            for ann in f.msg_annotations:
                if isinstance(ann, ConsumerAnnotation):
                    for subscr in ann.subscriptions:
                        cons[subscr.message].add(f)

        return cons

    def gateway_urls(self):
        """Returns all URLs where this service is available through API
        Gateways.

        Returns:
            set
        """
        model = self.parent.model
        result = set()
        for module in model.modules:
            for ag in module.api_gateways:
                for gf in ag.gateway_for:
                    if gf.service is self:
                        depl = ag.deployment
                        url = "%s:%s%s" % (depl.url, depl.port, gf.path)
                        result.add(url)
        return result

    @property
    def uses_messaging(self):
        """Returns True if a service uses messaging for communication. False
        otherwise.

        Returns:
            bool
        """
        for t in self.api.typedefs:
            if len(t.produces) > 0:
                return True

        for f in self.api.functions:
            for _ in f.msg_annotations:
                # Return True if generator is not empty.
                return True

        if not self.api.internal:
            return False

        for f in self.api.internal.functions:
            for _ in f.msg_annotations:
                # Return True if generator is not empty.
                return True

        return False


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

    def __init__(self, parent, name=None, client_mode=False, deployment=None):
        super().__init__(deployment)
        self.name = name
        self.parent = parent
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


class Function(DocstringContainer):
    """Object representation of function declaration."""
    def __init__(self, parent, name=None, ret_type=None, params=None,
                 annotations=None, docstring=None):
        super().__init__(docstring)
        self.parent = parent
        self.name = name
        self.ret_type = ret_type
        self.params = params if params else []
        self.rest_path = None
        self.dep = None
        self.http_verb = None
        self.cb_pattern = None
        self.cb_fallback = None
        self.annotations = annotations if annotations else []

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
        return "{}.{}".format(module.path.replace(".si", ""), service.name)

    @property
    def msg_annotations(self):
        """Returns generator of MessagingAnnotations"""
        for ann in self.annotations:
            if isinstance(ann, MessagingAnnotation):
                yield ann

    @property
    def produces(self):
        """Returns list of tuples that show which messages will be published
        to which channel.

        Returns:
            list
        """
        result = []
        for ann in self.msg_annotations:
            if isinstance(ann, ProducerAnnotation):
                for subscr in ann.subscriptions:
                    result.append((subscr.message, subscr.channel))
        return result

    @property
    def consumes(self):
        """Returns list of message-channel pairs for each function that is
        message consumer

        Returns:
            list
        """
        result = []
        for ann in self.msg_annotations:
            if isinstance(ann, ConsumerAnnotation):
                for subscr in ann.subscriptions:
                    result.append((subscr.message, subscr.channel))
        return result

    @property
    def channels(self):
        """Returns list of all channels from which the function consumes
        messages

        Returns:
            list
        """
        result = []
        for sub in self.consumes:
            result.append(sub[1].name)
        return result

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

    def is_async(self):
        return "@async" in self.annotations

    def clone(self):
        params = [p.clone() for p in self.params]

        annotations = []
        for ann in self.annotations:
            ann_clone = ann if isinstance(ann, str) else ann.clone()
            annotations.append(ann_clone)

        f = Function(None, self.name, self.ret_type, params, annotations)
        f.http_verb = self.http_verb
        f.cb_pattern = self.cb_pattern
        f.cb_fallback = self.cb_fallback
        return f

    @property
    def is_ret_type_a_list(self):
        return isinstance(self.ret_type, List)

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

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def clone(self):
        raise NotImplementedError()


class RESTAnnotation(Annotation):

    def __init__(self, parent, method=None, mapping=None):
        self.parent = parent
        self.method = method
        self.mapping = mapping

    def clone(self):
        return RESTAnnotation(None, self.method, self.mapping)


class MessagingAnnotation(Annotation):

    def __init__(self, parent, subscriptions=None):
        super().__init__(parent)
        self.subscriptions = subscriptions


class ProducerAnnotation(MessagingAnnotation):
    def __init__(self, parent, subscriptions):
        super().__init__(parent, subscriptions)


class ConsumerAnnotation(MessagingAnnotation):
    def __init__(self, parent, subscriptions):
        super().__init__(parent, subscriptions)


class TypeDef(DocstringContainer):

    def __init__(self, parent, name=None, inherits=None, fields=None,
                 crud=None, docstring=None):
        super().__init__(docstring)
        self.parent = parent
        self.name = name
        self.inherits = inherits if inherits else []
        self.fields = fields if fields else []
        self.crud = crud

        self.crud_dict = {}

        if "@crud" in [t.operation for t in crud]:
            self.crud_dict["@create"] = None
            self.crud_dict["@read"] = None
            self.crud_dict["@update"] = None
            self.crud_dict["@delete"] = None

        for td_crud in [t for t in crud if t.operation != "@crud"]:
            if td_crud.message:

                pkg = td_crud.message.split(".")
                class_path = ""
                if len(pkg) > 1:
                    for part in pkg[:-1]:
                        class_path += part.lower() + "."
                class_path += pkg[-1]
                self.crud_dict[td_crud.operation] = (td_crud.message,
                                                     td_crud.channel.split(".")[1],
                                                     class_path)
            else:
                self.crud_dict[td_crud.operation] = None

    @property
    def produces(self):
        prods = defaultdict(set)
        for t in self.crud:
            if t.message:
                prods[t.message].add(t.channel)
        return prods

    def __str__(self):
        return self.name

    @property
    def event_for(self):
        return {k: v for k, v in self.crud_dict.items() if v is not None}


class TypeField:

    def __init__(self, parent, id=None, classifiers=None, type=None,
                 name=None, constraints=None):
        self.parent = parent
        self.id = id
        self.classifiers = classifiers if classifiers else []
        self.type = type
        self.name = name
        self.constraints = constraints if constraints else []

    @property
    def isid(self):
        return any({c.id for c in self.classifiers})

    @property
    def unique(self):
        if self.isid:
            return True
        return any({c.unique for c in self.classifiers})

    @property
    def required(self):
        if self.isid:
            return True
        return any({c.required for c in self.classifiers})

    @property
    def ordered(self):
        return any({c.ordered for c in self.classifiers})


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


class Set(Sequence):
    def __init__(self, parent):
        super().__init__(parent)


class TypedSet(Set):
    def __init__(self, parent, type):
        super().__init__(parent)
        self.type = type


class Dict(Sequence):
    def __init__(self, parent):
        super().__init__(parent)


class TypedDict(Dict):
    def __init__(self, parent, key_type, value_type):
        super().__init__(parent)
        self.key_type = key_type
        self.value_type = value_type
