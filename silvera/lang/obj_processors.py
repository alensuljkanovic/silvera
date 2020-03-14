"""
This module contains object processors attached to Silvera objects. Object
processors are used during parsing.
"""
from collections import deque, OrderedDict
from silvera.core import (ServiceDecl, ConfigServerDecl, ServiceRegistryDecl,
                          TypedList, TypeDef, Deployable, Deployment)
from silvera.exceptions import SilveraTypeError


BASIC_TYPES = {"date", "i16", "i32", "i64", "bool", "int", "void", "str",
               "double"}


def process_connections(module):
    """Object processor for the Interface class."""
    conns = {c for c in module.decls if c.__class__.__name__ == "Connection"}

    for connection in conns:
        #
        # Mark start as 'circuit_breaked'
        #
        start = connection.start
        end = connection.end
        if hasattr(start, "circuit_breaked"):
            start.circuit_breaked = True

        use = {c.method_name: (c.failure_pattern, c.fallback_method)
               for c in connection.circuit_break_defs}

        for orig_fn in end.api.functions:
            if orig_fn.name in use:
                fn_clone = orig_fn.clone()
                fn_clone.dep = orig_fn
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
    api = service_decl.api
    if api is not None:

        # Resolve type definitions
        typedefs = api.typedefs
        for field in (f for td in typedefs for f in td.fields
                      if not is_type_resolved(f.type)):
            if isinstance(field.type, TypedList):
                _resolve_typed_list(service_decl, field.type)
            else:
                try:
                    ft = service_decl.domain_objs[field.type]
                except KeyError:
                    raise SilveraTypeError(service_decl.name, field.type)

                field.type = ft

        # Resolve functions
        functions = api.functions

        for fnc in functions:

            # Resolve function's return type
            ret_type = fnc.ret_type
            if not is_type_resolved(ret_type):
                if isinstance(ret_type, TypedList):
                    _resolve_typed_list(service_decl, ret_type)
                else:
                    try:
                        rtd = service_decl.domain_objs[ret_type]
                    except KeyError:
                        raise SilveraTypeError(service_decl.name, ret_type)

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
                        raise SilveraTypeError(service_decl.name, param.type)

                    param.type = td


def _resolve_typed_list(service_decl, typed_list):
    """Resolves type of TypedList."""
    if isinstance(typed_list.type, TypedList):
        _resolve_typed_list(service_decl, typed_list.type)
    else:
        if not is_type_resolved(typed_list.type):
            try:
                ft = service_decl.domain_objs[typed_list.type]
            except KeyError:
                raise SilveraTypeError(service_decl.name, typed_list.type)

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

    base_service = lookup(module, base_service_name)
    service_decl.extends = base_service

    if service_decl.config_server is None:
        service_decl.config_server = base_service.config_server

    if service_decl.service_registry is None:
        service_decl.service_registry = base_service.service_registry

    resolve_deployment_inheritance(base_service, service_decl)
    resolve_api_inheritance(base_service, service_decl)


def process_module(module):
    """Performs special processing of a Module object, such as resolving
    imports and connections.

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
                decl.deployment = Deployment(decl)

        if isinstance(decl, ServiceDecl):
            resolve_inheritance(module, decl)
            resolve_custom_types(decl)

            cfg = decl.config_server
            if cfg and not isinstance(cfg, ConfigServerDecl):
                decl.config_server = lookup(module, cfg)

            reg = decl.service_registry
            if reg and not isinstance(reg, ServiceRegistryDecl):
                decl.service_registry = lookup(module, reg)

        if decl.__class__.__name__ == "Connection":
            start = decl.start
            if not isinstance(start, ServiceDecl):
                decl.start = lookup(module, start)

            end = decl.end
            if not isinstance(end, ServiceDecl):
                decl.end = lookup(module, end)

    process_connections(module)


def model_processor(model):
    """Object processor for the Model class"""

    deps = {}

    for module in model.modules:
        deps[module] = []

    for module in model.modules:
        for dep_path in module.depends_on():
            deps[module].append(dep_path)

    # topologically sort modules
    modules = sort(deps)
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

