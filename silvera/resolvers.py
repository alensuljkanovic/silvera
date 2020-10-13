"""
This module contains classes for REST annotations resolvers.
"""
from silvera.const import HTTP_GET
from silvera.core import ServiceDecl

NO_STRATEGY = 0
PREFER_POST_OVER_PUT = 1
PREFER_PUT_OVER_POST = 2
PREFER_GET_OVER_DELETE = 3
PREFER_DELETE_OVER_GET = 4


class RESTResolver:
    """Resolves paths for services and their functions if they
    use REST communication style.

    If function is annotated with @rest, the annotation will be used by
    resolver. If there is no annotation, resolver will rely on chosen
    resolution strategy.

    Resolution strategies:
    -------------------------------------------------------------------
    - NO_STRATEGY:
        - This strategy uses following rule:
            - Every function is HTTP_GET function.

    - PREFER_POST_OVER_PUT:
        - This strategy uses following rules:
            1. Same as NO_STRATEGY
            2. Same as NO_STRATEGY
            3. If function has one parameter:
                3a: Parameter's type is typedef object -> HTTP_POST function
                3b: Parameter's type is not typedef object -> raise an
                    exception

    - PREFER_PUT_OVER_POST:
        - This strategy uses following rules:
            1. Same as NO_STRATEGY
            2. Same as NO_STRATEGY
            3. If function has one parameter:
                3a: Parameter's type is typedef object -> HTTP_PUT function
                3b: Parameter's type is not typedef object -> raise an
                    exception

    - PREFER_GET_OVER_DELETE:
        - This strategy uses following rules:
            1. Same as NO_STRATEGY
            2. Same as NO_STRATEGY
            3. If function has one parameter:
                3a: Parameter's type is typedef object -> raise an exception
                3b: Parameter's type is  not typedef object -> HTTP_GET
                    function

    - PREFER_DELETE_OVER_GET:
        - This strategy uses following rules:
            1. Same as NO_STRATEGY
            2. Same as NO_STRATEGY
            3. If function has one parameter:
                3a: Parameter's type is typedef object -> raise an exception
                3b: Parameter's type is not typedef object -> HTTP_DELETE
                    function
    """
    def __init__(self, strategy=NO_STRATEGY):
        super().__init__()

        strategy_map = {
            NO_STRATEGY: DefaultStrategy,
            PREFER_POST_OVER_PUT: PreferPostOverPut,
            PREFER_PUT_OVER_POST: PreferPutOverPost,
            PREFER_GET_OVER_DELETE: PreferGetOverDelete,
            PREFER_DELETE_OVER_GET: PreferDeleteOverGet
        }

        try:
            strategy_obj = strategy_map[strategy]
        except KeyError:
            raise KeyError("Unknown resolving strategy!")

        self.strategy = strategy_obj()

    def resolve_model(self, model):
        """Resolve model."""
        for decl in (d for module in model.modules for d in module.decls):
            if isinstance(decl, ServiceDecl):
                self.resolve_service(decl)

    def resolve_service(self, service):
        """Resolve service."""
        def http_get_params(func_params):
            return "/".join(["{%s}" % p.name for p in func_params])

        def func_name_mapping(func):
            ann = rest_annotation(func)
            if ann and ann.mapping:
                fn_mapping = ann.mapping
            else:
                fn_mapping = "%s" % func.name.lower()

                if func.http_verb == HTTP_GET and func.params:
                    fn_mapping += "/" + http_get_params(func.params)

            return fn_mapping

        model = service.parent.model
        # name = service.name
        api = service.api

        # path = "%s/" % name.lower()
        for func in api.functions:
            ann = rest_annotation(func)
            if ann is not None:
                self._apply_annotation(func)
            else:
                self._apply_strategy(func)

            func.add_rest_mappings(func_name_mapping(func))

        for func in service.dep_functions:
            org_serv = model.find_by_fqn(func.service_fqn)
            org_fn = org_serv.get_function(func.name)
            func.http_verb = org_fn.http_verb
            func.rest_path = func_name_mapping(func)

    def _apply_annotation(self, func):
        """Applies the REST annotation given in .si file.

        Args:
            func (Function): function object
        """
        ann = rest_annotation(func)
        func.http_verb = ann.method

    def _apply_strategy(self, func):
        """Tries to calculate REST path for the function based on chosen
        resolution strategy.

        Args:
            func (Function): function object
        """
        self.strategy.apply(func)


class ResolvingStrategy:

    def __init__(self):
        super().__init__()

    def apply(self, func):
        raise NotImplementedError()


class DefaultStrategy(ResolvingStrategy):

    def __init__(self):
        super().__init__()

    def apply(self, func):
        func.http_verb = HTTP_GET


class PreferPostOverPut(ResolvingStrategy):

    def __init__(self):
        super().__init__()

    def apply(self, func):
        raise NotImplementedError()


class PreferPutOverPost(ResolvingStrategy):

    def __init__(self):
        super().__init__()

    def apply(self, func):
        raise NotImplementedError()


class PreferGetOverDelete(ResolvingStrategy):

    def __init__(self):
        super().__init__()

    def apply(self, func):
        raise NotImplementedError()


class PreferDeleteOverGet(ResolvingStrategy):

    def __init__(self):
        super().__init__()

    def apply(self, func):
        raise NotImplementedError()


def rest_annotation(func):
    for ann in func.annotations:
        if ann.__class__.__name__ == "RESTAnnotation":
            return ann

    return None