"""
This module contains the implementation of talkie IDL.
"""

class TalkieObject(object):
    """Base class for all classes used in the implementation of talkie IDL."""
    def __init__(self, parent):
        super(TalkieObject, self).__init__()
        self.parent = parent


class Interface(TalkieObject):
    """Object representation of an interface defined by talkie DSL."""
    def __init__(self, name, parent=None, functions=None, langs=None):
        """Initializes Interface object."""
        super(Interface, self).__init__(parent)
        self.name = name
        self.functions = functions if functions else []
        self.langs = langs if langs else []


class Function(TalkieObject):
    """Object representation of a function defined by talkie DSL."""
    def __init__(self, parent, name, ret_type=None, params=None):
        """Initializes Interface object."""
        super(Function, self).__init__(parent)
        self.name = name
        self.ret_type = ret_type
        self.params = params if params else []

    @property
    def parameters(self):
        params = ["%s %s" % (p.p_type, p.p_name) for p in self.params]
        return ", ".join(params)


class FunctionParameter(TalkieObject):
    """Object representation of a function param defined by talkie DSL."""
    def __init__(self, parent, p_name, p_type):
        super(FunctionParameter, self).__init__(parent)
        self.p_name = p_name
        self.p_type = p_type


