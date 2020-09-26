"""
This module contains function that export Silvera module into dot format.
"""
import os
from silvera.core import Deployable, ConfigServerDecl, ServiceRegistryDecl, \
    ServiceDecl

HEADER = """
digraph silvera {
  fontname = "Bitstream Vera Sans"
  fontsize = 8
  node[
      shape=record,
      style=filled,
      fillcolor=azure
  ]
  nodesep = 0.3
  edge[dir=black,arrowtail=empty]

"""

DETAIL_SIMPLE = 0
DETAIL_WITH_FUNCTIONS = 1
DETAIL_ALL = 2


def deploy_to_str(deployable):
    depl = deployable.deployment
    l = ["%s: %s" % (a, getattr(depl, a)) for a in depl._tx_attrs if getattr(depl, a)]

    return "\l".join(l) + "\l"


def unfold_params(f):
    l = ["{} {}".format(p.type, p.name) for p in f.params]
    return ", ".join(l)


def get_functions(serv):
    l = []
    for f in serv.api.functions:
        str = "+ {}()".format(f.name)
        l.append(str)
    return "\l".join(l) + "\l"


def export_to_dot(model, output_path, detail_level=DETAIL_SIMPLE):
    """Exports given module to a DOT file

    To create a PNG image from DOT use following command:
    dot -Tpng <dot-file> -o <image_name>.png

    Args:
        model (Model): Silvera model object
        output_path (str): path where dot file will be created
        detailed (bool): tells exporter whether image should contain full
            details or not. If set to True, API functions from services will
            be shown.
    """

    str = HEADER

    for decl in (decl for m in model.modules for decl in m.decls):

        if isinstance(decl, Deployable):
            color = ""
            functions = ""
            deploy = ""
            if isinstance(decl, ConfigServerDecl):
                color = ", fillcolor=antiquewhite"
            if isinstance(decl, ServiceRegistryDecl):
                color = ", fillcolor=darkseagreen1"
            if isinstance(decl, ServiceDecl) and \
                    detail_level == DETAIL_WITH_FUNCTIONS:
                functions = "|%s" % get_functions(decl)

            if detail_level == DETAIL_ALL:
                deploy = "|%s" % deploy_to_str(decl)

            str += '  {0}[label="{{{0}{1}{2}}}"{3}]\n'.format(
                decl.name, deploy, functions, color)

            if hasattr(decl, "service_registry") and decl.service_registry:
                str += '  {} -> {}[label="register", color=green]\n'.format(
                    decl.name, decl.service_registry.name)

            if hasattr(decl, "config_server") and decl.config_server:
                str += '  {} -> {}[label="config", color=orange]\n'.format(
                    decl.name, decl.config_server.name)

    for conn in (conn for m in model.modules for conn in m.dependencies):
        cb_methods = [cb.method_name for cb in conn.circuit_break_defs]
        for method in cb_methods:
            str += '  {} -> {}[label="{}()"]\n'.format(
                conn.start.name,
                conn.end.name,
                method)

    str += " }"

    output_file = os.path.join(output_path, "model.dot")
    with open(output_file, "w") as f:
        f.write(str)


