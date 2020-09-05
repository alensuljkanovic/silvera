import os
from textx.metamodel import metamodel_from_file
from silvera.core import Module, ServiceDecl, ServiceRegistryDecl, TypeDef, \
    CustomType, DataType, Collection, Sequence, List, TypedList, Number, \
    Function, FunctionParameter, ConfigServerDecl, APIGateway, RESTAnnotation,\
    Deployment, MessagePool, MessageBroker, MessageGroup, Message, \
    ProducerAnnotation, ConsumerAnnotation, TypeField

from silvera.utils import get_root_path

_classes = (Module, ServiceDecl, ServiceRegistryDecl, TypeDef, CustomType,
            DataType, Collection, Sequence, List, TypedList, Number, Function,
            FunctionParameter, ConfigServerDecl, APIGateway, RESTAnnotation,
            Deployment, MessagePool, MessageBroker, MessageGroup, Message,
            ProducerAnnotation, ConsumerAnnotation, TypeField)


def get_metamodel():
    """
    Returns metamodel of FreeMindMap.
    """
    global _metamodel

    path = os.path.join(get_root_path(), "silvera", "lang", "silvera.tx")
    _metamodel = metamodel_from_file(path, classes=_classes,
                                     auto_init_attributes=False)

    return _metamodel
