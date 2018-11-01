"""
This module contains function that export Talkie module into dot format.
"""
from talkie.talkie import Deployable, ConfigServerDecl, ServiceRegistryDecl, \
    ServiceDecl

HEADER = """
digraph talkie {
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
        str = "{} {}({})".format(f.ret_type, f.name, unfold_params(f))
        l.append(str)
    return "\l".join(l) + "\l"


def export_to_dot(module, output_path, detailed=False):
    """Exports given module to a DOT file

    To create a PNG image from DOT use following command:
    dot -Tpng <dot-file> -o <image_name>.png

    Args:
        module (Module): Talkie module object
        output_path (str): path where dot file will be created
        detailed (bool): tells exporter whether image should contain full
            details or not. If set to True, API functions from services will
            be shown.
    """

    str = HEADER
    for decl in module.decls:

        if isinstance(decl, Deployable):
            color = ""
            functions = ""
            if isinstance(decl, ConfigServerDecl):
                color = ", fillcolor=antiquewhite"
            if isinstance(decl, ServiceRegistryDecl):
                color = ", fillcolor=darkseagreen1"
            if isinstance(decl, ServiceDecl) and detailed:
                functions = "|%s" % get_functions(decl)

            str += '  {0}[label="{{{0}|{1}{2}}}"{3}]\n'.format(
                decl.name, deploy_to_str(decl), functions, color)

            if hasattr(decl, "service_registry"):
                str += '  {} -> {}[label="register", color=green]\n'.format(
                    decl.name, decl.service_registry.name)

            if hasattr(decl, "config_server"):
                str += '  {} -> {}[label="config", color=orange]\n'.format(
                    decl.name, decl.config_server.name)

    for conn in module.connections:
        str += '  {} -> {}[label="dependency"]\n'.format(conn.start.name, conn.end.name)

    str += " }"

    with open(output_path, "w") as f:
        f.write(str)


