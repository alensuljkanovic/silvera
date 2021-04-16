import os
from textx.metamodel import metamodel_from_file
from silvera.core import Module, ServiceDecl, ServiceRegistryDecl, TypeDef, \
    DataType, Collection, Sequence, List, TypedList, Number, \
    Function, FunctionParameter, ConfigServerDecl, APIGateway, RESTAnnotation, \
    Deployment, MessagePool, MessageBroker, MessageGroup, Message, \
    ProducerAnnotation, ConsumerAnnotation, TypeField, Set, TypedSet, Dict, \
    TypedDict

from silvera.utils import get_root_path

_classes = (Module, ServiceDecl, ServiceRegistryDecl, TypeDef,
            DataType, Collection, Sequence, List, TypedList, Number, Function,
            FunctionParameter, ConfigServerDecl, APIGateway, RESTAnnotation,
            Deployment, MessagePool, MessageBroker, MessageGroup, Message,
            ProducerAnnotation, ConsumerAnnotation, TypeField,
            Set, TypedSet, Dict, TypedDict)


def get_metamodel():
    """
    Returns metamodel of FreeMindMap.
    """
    global _metamodel

    path = os.path.join(get_root_path(), "silvera", "lang", "silvera.tx")
    _metamodel = metamodel_from_file(path, classes=_classes,
                                     auto_init_attributes=False,
                                     autokwd=True)

    return _metamodel
