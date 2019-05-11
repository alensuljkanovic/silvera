"""
This module contains object processors attached to Talkie objects. Object
processors are used during parsing.
"""


def module_processor(module):
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
