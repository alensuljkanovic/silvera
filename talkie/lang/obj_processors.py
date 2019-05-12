"""
This module contains object processors attached to Talkie objects. Object
processors are used during parsing.
"""
from collections import deque, OrderedDict
from talkie.talkie import ServiceDecl, ConfigServerDecl, ServiceRegistryDecl


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

        start.dependencies.append(end)


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


def process_module(module):
    """Performs special processing of a Module object, such as resolving
    imports and connections.

    Args:
        module (Module): module object that is being processed

    Returns:
        None
    """
    for decl in module.decls:
        if isinstance(decl, ServiceDecl):
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

