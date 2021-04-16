"""
This module contains object processors attached to Silvera objects. Object
processors are used during parsing.
"""
from collections import deque, OrderedDict, defaultdict

from silvera.const import BASIC_TYPES
from silvera.core import (ServiceDecl, ConfigServerDecl, ServiceRegistryDecl,
                          TypedList, TypeDef, Deployable, Deployment,
                          MessagePool, ProducerAnnotation, APIGateway, TypedSet)
from silvera.exceptions import SilveraTypeError, SilveraLoadError
from silvera.utils import available_port


def process_dependency(module):
    """Object processor for the Interface class."""
    deps = {c for c in module.decls if c.__class__.__name__ == "Dependency"}

    for dependency in deps:
        #
        # Mark start as 'circuit_breaked'
        #
        start = dependency.start
        end = dependency.end

        if hasattr(start, "circuit_breaked"):
            start.circuit_breaked = True

        use = {c.method_name: (c.failure_pattern, c.fallback_method)
               for c in dependency.circuit_break_defs}
        end_api_functions = {f.name: f for f in end.api.functions}

        # Check if all methods are defined in the end service
        non_existing = {f for f in use if f not in end_api_functions}
        if non_existing:
            raise SilveraLoadError(
                "Following functions are not defined in service '{}': {}".format(
                    end.name,
                    sorted(non_existing)
                ))

        for orig_name, orig_fn in end_api_functions.items():
            if orig_name in use:
                failure_pattern, fallback_method = use[orig_name]

                fn_clone = orig_fn.clone()
                fn_clone.dep = orig_fn
                fn_clone.cb_pattern = failure_pattern

                # Set default value for fallback function
                if fallback_method is None:
                    fallback_method = orig_name + "_fallback"

                fn_clone.cb_fallback = fallback_method
                start.dep_functions.append(fn_clone)

                ret_type = orig_fn.ret_type
                if isinstance(ret_type, TypeDef):
                    start.dep_typedefs.extend(recurse_typedef(ret_type))
                elif isinstance(ret_type, TypedList):
                    start.dep_typedefs.extend(recurse_typedef(ret_type.type))

        start.dependencies.append(end)


def recurse_typedef(typedef, visited=None):
    """Find all types that the current service will depend upon"""
    if visited is None:
        visited = set()

    if typedef in visited:
        return

    visited.add(typedef)

    for field in typedef.fields:
        if isinstance(field.type, TypeDef):
            recurse_typedef(field.type, visited)
        elif isinstance(field.type, TypedList):
            recurse_typedef(field.type.type, visited)

    return visited


def assign_ref(decl, attr_name, module=None, lookup_name=None):
    """Assign reference to object attribute.

    Args:
        decl (Decl): declaration object
        attr_name (str): attribute name
        module (Module): module object
        lookup_name (str): lookup name
    """
    if module is None:
        module = decl.parent

    if lookup_name is None:
        lookup_name = getattr(decl, attr_name)

    try:
        ref_obj = lookup(module, lookup_name)
    except KeyError as ex:
        linecol = module._tx_parser.pos_to_linecol(decl._tx_position)
        msg = "Error in module {} {}: {}".format(module.path,
                                                 linecol,
                                                 ex)
        raise KeyError(msg)

    setattr(decl, attr_name, ref_obj)


def lookup(module, name):
    """Tries to find object with given `name` for a given `module`.

    If name is FQN, lookup will be performed on a model level.

    Otherwise, lookup is first performed on a local level (inside `module`
    itself), and afterwards through imports (if local lookup fails).

    Args:
        module (Module): module object
        name (str): name of the object that we're looking for

    Returns:
        Decl
    """
    model = module.model
    if "." in name:
        return model.find_by_fqn(name)
    else:
        try:
            # Reference from current module
            return module.decl_by_name(name)
        except KeyError as ex:
            # Look for object in imports
            found = []
            for mm in module.depends_on():
                try:
                    found.append((mm, mm.decl_by_name(name)))
                except KeyError:
                    pass  # We will raise an error later if object is not found

            if not found:
                raise ex

            if len(found) > 1:
                imports = [f[0] for f in found]
                raise ValueError("Definition of object {} found in multiple "
                                 "modules: {}".format(name, imports))

            return found[0][1]


def resolve_custom_types(service_decl):
    """Sets appropriate objects for function parameters whose type is domain
    object (typedef).
    """
    module = service_decl.parent

    api = service_decl.api
    if api is not None:

        # Resolve type definitions
        typedefs = api.typedefs
        for td in typedefs:
            for td_crud in [t for t in td.crud if t.operation != "@crud"]:
                _resolve_msg_inst(module, td_crud)
                _resolve_ch_inst(module, td_crud)

            for field in (f for f in td.fields
                          if not is_type_resolved(f.type)):
                if isinstance(field.type, TypedList):
                    _resolve_typed_list(service_decl, field.type)
                else:
                    try:
                        ft = service_decl.domain_objs[field.type]
                    except KeyError:
                        linecol = module._tx_parser.pos_to_linecol(
                            field._tx_position)
                        raise SilveraTypeError(module.path,
                                               field.type,
                                               linecol)

                    field.type = ft

        # Resolve public functions
        functions = api.functions

        for fnc in functions:
            _resolve_fnc(module, service_decl, fnc)

        # Resove internal functions
        functions = api.internal.functions if api.internal else []
        for fnc in functions:
            _resolve_fnc(module, service_decl, fnc)


def _resolve_fnc(module, service_decl, fnc):
    """Resolves all custom types in function object. That includes return type,
    parameters, and annotations.

    Args:
        module (Module): module object
        service_decl (ServiceDecl): service where function is declared.
        fnc (Function): function to resolve.
    """
    model = module.model
    msg_pool = model.msg_pool

    # Resolve function's return type
    ret_type = fnc.ret_type
    if not is_type_resolved(ret_type):
        if isinstance(ret_type, (TypedList, TypedSet)):
            _resolve_typed_list(service_decl, ret_type)
        else:
            try:
                rtd = service_decl.domain_objs[ret_type]
            except KeyError:
                linecol = module._tx_parser.pos_to_linecol(
                    fnc._tx_position)
                raise SilveraTypeError(module.path, ret_type, linecol)

            fnc.ret_type = rtd

    # Resolve function's parameters
    for param in [p for p in fnc.params
                  if not is_type_resolved(p.type)]:
        if isinstance(param.type, TypedList):
            _resolve_typed_list(service_decl, param.type)
        else:
            try:
                td = service_decl.domain_objs[param.type]
            except KeyError:
                linecol = module._tx_parser.pos_to_linecol(
                    param._tx_position)
                raise SilveraTypeError(module.path, param.type, linecol)

            param.type = td

    # Resolve messaging annotations
    for ann in fnc.msg_annotations:
        for subscr in ann.subscriptions:
            message_fqn = subscr.message

            # Find Message object represented by given FQN, and
            # set reference to it.
            try:
                subscr.message = msg_pool.get(message_fqn)
            except ValueError:
                linecol = module._tx_parser.pos_to_linecol(
                    subscr._tx_position)
                raise SilveraLoadError(
                    "Cannot resolve annotation ({} {}). Message '{}' "
                    "not defined in message pool.".format(
                        module.path,
                        linecol,
                        message_fqn)
                )

            # Find MessageChannel object represented by given FQN, and
            # set reference to it.
            channel_fqn = subscr.channel
            fqn = channel_fqn.split(".")
            broker_name = fqn[0]
            try:
                broker = model.msg_brokers[broker_name]
            except KeyError:
                linecol = module._tx_parser.pos_to_linecol(
                    subscr._tx_position)
                raise SilveraLoadError(
                    "Cannot resolve annotation ({} {}). Broker '{}' "
                    "not defined.".format(
                        module.path,
                        linecol,
                        broker_name)
                )

            channel_name = fqn[1]
            try:
                channel = broker.channels[channel_name]
                subscr.channel = channel
            except KeyError:
                linecol = module._tx_parser.pos_to_linecol(
                    subscr._tx_position)
                raise SilveraLoadError(
                    "Cannot resolve annotation ({} {}). Channel '{}' "
                    "not defined in broker '{}'".format(
                        module.path,
                        linecol,
                        channel_name,
                        broker_name)
                )

            # Perform registrations
            if isinstance(ann, ProducerAnnotation):
                broker.register_producer(channel_name, fnc)
            else:
                broker.register_consumer(channel_name, fnc)


def _resolve_msg_inst(module, msg_container):
    if msg_container.message is None:
        return
    # Find Message object represented by given FQN, and
    # set reference to it.
    msg_pool = module.model.msg_pool
    message_fqn = msg_container.message
    try:
        msg_container.message = msg_pool.get(message_fqn)
    except ValueError:
        linecol = module._tx_parser.pos_to_linecol(
            msg_container._tx_position)
        raise SilveraLoadError(
            "Cannot resolve annotation ({} {}). Message '{}' "
            "not defined in message pool.".format(
                module.path,
                linecol,
                message_fqn)
        )


def _resolve_ch_inst(module, channel_container):
    if channel_container.channel is None:
        return
    # Find MessageChannel object represented by given FQN, and
    # set reference to it.
    model = module.model
    channel_fqn = channel_container.channel
    fqn = channel_fqn.split(".")
    broker_name = fqn[0]
    try:
        broker = model.msg_brokers[broker_name]
    except KeyError:
        linecol = module._tx_parser.pos_to_linecol(
            channel_container._tx_position)
        raise SilveraLoadError(
            "Cannot resolve annotation ({} {}). Broker '{}' "
            "not defined.".format(
                module.path,
                linecol,
                broker_name)
        )

    channel_name = fqn[1]
    try:
        channel = broker.channels[channel_name]
        channel_container.channel = channel
    except KeyError:
        linecol = module._tx_parser.pos_to_linecol(
            channel_container._tx_position)
        raise SilveraLoadError(
            "Cannot resolve annotation ({} {}). Channel '{}' "
            "not defined in broker '{}'".format(
                module.path,
                linecol,
                channel_name,
                broker_name)
        )

    # Perform registrations
    # if isinstance(ann, ProducerAnnotation):
    #     broker.register_producer(channel_name, fnc)
    # else:
    #     broker.register_consumer(channel_name, fnc)


def _resolve_typed_list(service_decl, typed_list):
    """Resolves type of TypedList."""
    if isinstance(typed_list.type, TypedList):
        _resolve_typed_list(service_decl, typed_list.type)
    else:
        if not is_type_resolved(typed_list.type):
            try:
                ft = service_decl.domain_objs[typed_list.type]
            except KeyError:
                module = service_decl.parent
                linecol = module._tx_parser.pos_to_linecol(
                    typed_list._tx_position)
                raise SilveraTypeError(module.path,
                                       typed_list.type,
                                       linecol)

            typed_list.type = ft


def is_type_resolved(_type):
    """Helper function that checks if type is already resolved."""
    return _type in BASIC_TYPES or isinstance(_type, TypeDef)


def resolve_deployment_inheritance(base_service, service_decl):
    """Resolves deployment inheritance for between given services

    If `service_decl` is not redefining deployment, then deployment object
    from `base_service` will be provided to it.

    If `service_decl` redefines deployment, attributes that are not changed
    will be inherited from `base_service`.

    Args:
        base_service (ServiceDecl): base service
        service_decl (ServiceDecl): service that is being resolved

    Returns:
        None
    """
    deployment = service_decl.deployment
    if deployment is None:
        service_decl.deployment = base_service.deployment
    else:
        base_attr = base_service.deployment.__dict__
        curr_attr = service_decl.deployment.__dict__

        for attr_name, attr_val in curr_attr.items():
            if attr_val is None:
                new_val = base_attr[attr_name]
                setattr(deployment, attr_name, new_val)
            elif attr_name == "restart_policy":
                base_rp_attr = base_attr[attr_name].__dict__
                curr_rp__attr = curr_attr[attr_name].__dict__

                for rp_attr, rp_value in curr_rp__attr.items():
                    if rp_value is None:
                        new_val = base_rp_attr[rp_attr]
                        setattr(attr_val, rp_attr, new_val)


def resolve_api_inheritance(base_service, service_decl):
    """Resolves API inheritance between given services

    Note: API inheritance currently works only when adding new typedefs or
    functions. NotImplementedError will be raised in case of overriding any
    of the typedefs or methods from the parent.

    Args:
        base_service (ServiceDecl): base service
        service_decl (ServiceDecl): service that is being resolved

    Returns:
        None
    """
    api = service_decl.api
    if api is None:
        service_decl.api = base_service.api
    else:
        typedefs = {t.name: t for t in service_decl.api.typedefs}
        base_typedefs = {t.name: t for t in base_service.api.typedefs}

        for tdef_name, tdef in base_typedefs.items():
            if tdef_name not in typedefs:
                # If base_td is not in typedefs, it means it is not overriden
                # thus it must be inherited.
                service_decl.api.typedefs.append(tdef)
            else:
                _raise_not_implemented()

        functions = {m.name: m for m in service_decl.api.functions}
        base_functions = {m.name: m for m in base_service.api.functions}

        for fnc_name, fnc in base_functions.items():
            if fnc_name not in functions:
                service_decl.api.functions.append(fnc)
            else:
                _raise_not_implemented()


def _raise_not_implemented():
    raise NotImplementedError(
        "Currently, it is not possible to override typedefs or functions from"
        " parent ( sorry :( ). It is possible only to add new"
        " ones."
    )


def resolve_inheritance(module, service_decl):
    """Resolves inheritance for a given service."""
    base_service_name = service_decl.extends

    if base_service_name is None:
        return

    assign_ref(service_decl, "extends")
    base_service = service_decl.extends

    if service_decl.config_server is None:
        service_decl.config_server = base_service.config_server

    if service_decl.service_registry is None:
        service_decl.service_registry = base_service.service_registry

    resolve_deployment_inheritance(base_service, service_decl)
    resolve_api_inheritance(base_service, service_decl)


def resolve_api_gateway(module, api_gateway):

    reg = api_gateway.service_registry
    if reg and not isinstance(reg, ServiceRegistryDecl):
        assign_ref(api_gateway, "service_registry")

    for gt in list(api_gateway.gateway_for):
        if isinstance(gt.service, ServiceDecl):
            continue
        assign_ref(gt, "service", module=module)


def process_module(module):
    """Performs special processing of a Module object, such as resolving
    imports and dependencies.

    Args:
        module (Module): module object that is being processed

    Returns:
        None
    """
    for decl in module.decls:
        if isinstance(decl, Deployable):
            # If deployment is not defined, object with default values
            # will be assigned. But, in case deployment is not set and
            # decl extends another declaration, then deployment from the
            # parent declaration will be used.
            if decl.deployment is None and decl.extends is None:
                deployment = Deployment(decl)
                deployment.port = available_port(1)
                decl.deployment = deployment

        if isinstance(decl, ServiceDecl):
            resolve_inheritance(module, decl)
            resolve_custom_types(decl)

            cfg = decl.config_server
            if cfg and not isinstance(cfg, ConfigServerDecl):
                assign_ref(decl, "config_server")

            reg = decl.service_registry
            if reg and not isinstance(reg, ServiceRegistryDecl):
                assign_ref(decl, "service_registry")

            # assign port number if not assigned
            deployment = decl.deployment
            if deployment.port is None:
                deployment.port = available_port(deployment.replicas)

        if isinstance(decl, APIGateway):
            resolve_api_gateway(module, decl)

        if decl.__class__.__name__ == "Dependency":
            start = decl.start
            if not isinstance(start, ServiceDecl):
                assign_ref(decl, "start")

            end = decl.end
            if not isinstance(end, ServiceDecl):
                assign_ref(decl, "end")

    process_dependency(module)


def check_msg_pool(msg_pool):
    """Checks if all messages and groups are defined correctly.

    Exception will be raised in following cases:
    1. MessageGroup is empty (no messages defined inside group).
    2. MessageGroup's ID not unique.
    3. Message's name within the group is not unique.

    Args:
        msg_pool (MessagePool): message pool

    Returns:
        None

    Raises:
        SilveraLoadException
    """
    all_groups = msg_pool.get_all_groups()
    fqns = defaultdict(list)
    for group in all_groups:
        fqns[group.fqn].append(group)

    empty_groups = []
    for fqn, groups in fqns.items():
        # Raise exception in case of group redefinition
        if len(groups) > 1:
            err_msg = "Redefinition of message group found: "
            for g in groups:
                err_msg += to_err_line(g)

            raise SilveraLoadError(err_msg)

        # Check if there are messages in group
        group = groups[0]
        if not group.messages:
            empty_groups.append(group)

        # Check if message names are unique
        names = defaultdict(list)
        for m in group.messages:
            names[m.name].append(m)

        for name, messages in names.items():
            if len(messages) > 1:
                err_msg = "Redefinition of message found:"
                for msg in messages:
                    err_msg += to_err_line(msg)

                raise SilveraLoadError(err_msg)

    if empty_groups:
        err_msg = "Group(s) without messages found: "
        for g in empty_groups:
            err_msg += to_err_line(g)
        raise SilveraLoadError(err_msg)


def get_msg_pool(model):
    """Initializes msg_pool attr of model object"""
    results = []
    for module in model.modules:
        parser = module._tx_parser

        for decl in module.decls:
            if isinstance(decl, MessagePool):
                results.append((decl,
                                module.path,
                                parser.pos_to_linecol(decl._tx_position)))

    if results:
        if len(results) > 1:

            err_msg = "Multiple declarations of msg-pool found: "
            for _, file_path, linecol in results:
                err_msg += "\n\t * {} {}".format(file_path, linecol)

            raise SilveraLoadError(err_msg)

        msg_pool, _, _ = results[0]
        return msg_pool


def resolve_channel(msg_channel):
    """Resolves MessageChannel object.

    Args:
        msg_channel (MessageChannel): message channel object

    Raises:
        SilveraLoadError
    """
    module = msg_channel.parent.parent
    model = module.model

    msg_pool = model.msg_pool

    msg_type = msg_channel.msg_type
    try:
        # get Message object from pool
        msg = msg_pool.get(msg_type)
        # set the actual message object as a type
        msg_channel.msg_type = msg
    except ValueError:
        linecol = module._tx_parser.pos_to_linecol(msg_channel._tx_position)
        raise SilveraLoadError(
            "Cannot instantiate message channel '{}'({} {}). Message '{}' not "
            "defined in message pool.".format(
                msg_channel.name,
                module.path,
                linecol,
                msg_type
            ))


def resolve_brokers(brokers):
    """Resolves MessageBroker objects.

    If broker's name if not unique, SilveraLoadError is raised.
    If channel's name within broker if not unique, SilveraLoadError is raised.

    Args:
        brokers (list): list of message broker objects

    Raises:
        SilveraLoadError
    """
    visited = defaultdict(list)
    for b in brokers:
        ch_dict = defaultdict(list)
        for channel in b.channels.values():
            ch_dict[channel.name].append(channel)
            resolve_channel(channel)

        # Check for channel redefinitions
        for name, chs in ch_dict.items():
            if len(chs) > 1:
                err_msg = "Redefinition of message channel found:"
                for c in chs:
                    err_msg += to_err_line(c)
                raise SilveraLoadError(err_msg)

        visited[b.name].append(b)

    # Check for broker redefinitions
    for name, brokers in visited.items():
        if len(brokers) > 1:
            err_msg = "Redefinition of msg-broker found:"
            for b in brokers:
                err_msg += to_err_line(b)

            raise SilveraLoadError(err_msg)

    return {n: b[0] for n, b in visited.items()}


def model_processor(model):
    """Object processor for the Model class"""

    deps = {}

    for module in model.modules:
        deps[module] = []

    for module in model.modules:
        for dep_path in module.depends_on():
            deps[module].append(dep_path)

    msg_pool = get_msg_pool(model)

    if msg_pool:
        check_msg_pool(msg_pool)
        model.msg_pool = msg_pool

    # topologically sort modules
    modules = sort(deps)

    # collect message brokers if they exist
    msg_brokers = []
    for module in reversed(modules.keys()):
        msg_brokers.extend(list(module.msg_brokers))

    if msg_brokers:
        if not msg_pool:
            raise SilveraLoadError("Message pool must be defined in order to "
                                   "instantiate message brokers.")

        # check if message brokers are valid
        brokers = resolve_brokers(msg_brokers)
        model.msg_brokers = brokers

    # process all modules
    for module in reversed(modules.keys()):
        process_module(module)


def sort(modules):
    """Topologically sorts the modules by using Khan's algorithm"""

    sorted_nodes = []
    in_degree = {}

    for n in modules:
        in_degree[n] = 0

    # For each edge, increase in degree
    for n in modules:
        for e in modules[n]:
            in_degree[e] += 1

    queue = deque()
    for n in in_degree:
        if in_degree[n] == 0:
            queue.appendleft(n)

    while queue:
        n = queue.pop()
        sorted_nodes.append(n)
        for e in modules[n]:
            in_degree[e] -= 1
            if in_degree[e] == 0:
                queue.appendleft(e)

    if len(sorted_nodes) != len(modules):
        raise ValueError("Cyclic import found!")

    sorted_graph = OrderedDict()
    for n in sorted_nodes:
        sorted_graph[n] = modules[n]

    return sorted_graph


def to_err_line(item):
    module = item.msg_pool.parent
    path = module.path
    parser = module._tx_parser
    linecol = parser.pos_to_linecol(item._tx_position)
    return "\n\t- {}: {} {}".format(path, item.fqn, linecol)