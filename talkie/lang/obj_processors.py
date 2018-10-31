"""
This module contains object processors attached to Talkie objects. Object
processors are used during parsing.
"""
from talkie.utils import create_dependency_obj


def module_processor(module):
    """Object processor for the Interface class."""
    conns = {c for c in module.decls if c.__class__.__name__ == "Connection"}

    for connection in conns:
        #
        # Mark start as 'circuit_breaked'
        #
        start = connection.start
        if hasattr(start, "circuit_breaked"):
            start.circuit_breaked = True

        end = connection.end
        d = create_dependency_obj(end, connection)
        start.dependencies.append(d)
