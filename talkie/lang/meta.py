import os
from textx.metamodel import metamodel_from_file
from talkie.talkie import Module, ServiceDecl, ServiceRegistryDecl, TypeDef, \
    CustomType, DataType, Collection, Sequence, List, TypedList, Number, \
    Function, FunctionParameter, ConfigServerDecl
from talkie.utils import get_root_path

_classes = (Module, ServiceDecl, ServiceRegistryDecl, TypeDef, CustomType,
            DataType, Collection, Sequence, List, TypedList, Number, Function,
            FunctionParameter, ConfigServerDecl)


def get_metamodel():
    """
    Returns metamodel of FreeMindMap.
    """
    global _metamodel

    path = os.path.join(get_root_path(), "talkie", "lang", "talkie.tx")
    _metamodel = metamodel_from_file(path, classes=_classes)
    # _metamodel.register_obj_processors(_obj_processors)

    return _metamodel