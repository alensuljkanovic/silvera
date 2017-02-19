"""
This module contains object processors attached to Talkie objects. Object
processors are used during parsing.
"""


def interface_processor(interface):
    """Object processor for the Interface class."""
    names = set()
    for endpoint in interface.endpoints:
        name = endpoint.name
        if name in names:
            raise Exception("Each endpoint must have a unique name!")
        names.add(name)
