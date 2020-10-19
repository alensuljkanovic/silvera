import os
import fnmatch
from silvera.generator.generator import generate
from silvera.lang.meta import get_metamodel
from silvera.lang.obj_processors import model_processor
from silvera.resolvers import RESTResolver, NO_STRATEGY
from silvera.core import Model, Module


def compile(src_path, output_dir=None, rest_res_strategy=NO_STRATEGY):
    """Runs Silvera compiler

    After this function is called, Silvera will process the given .si file,
    and compile it to a chosen target platform.

    Args:
        src_path (str): path to the Silvera project
        output_dir (str): path to the directory where compiled application will
            be stored
        rest_res_strategy (int): REST resolving strategy.

    Returns:
        None
    """
    model = load(src_path, rest_res_strategy)

    if output_dir is None:
        output_dir = src_path
    else:
        output_dir = os.path.abspath(output_dir)

    generate(model, output_dir)


_metamodel = None


def load(src_path, rest_res_strategy=NO_STRATEGY):
    """Loads project

    Args:
        src_path(str): path to the project root dir, or to a single .si file.
        rest_res_strategy (int): REST resolving strategy.

    Returns:
        Model
    """
    if not os.path.exists(src_path) or not os.path.isdir(src_path):
        raise ValueError("Loading failed. Directory '%s' doesn't exist." %
                         src_path)

    global _metamodel

    if not _metamodel:
        _metamodel = get_metamodel()

    model = Model(src_path)
    for root, _, filenames in os.walk(src_path):
        for filename in fnmatch.filter(filenames, "*.si"):
            module_path = os.path.join(root, filename)
            module = _metamodel.model_from_file(module_path)
            if not isinstance(module, Module):
                raise ValueError("Loading failed. Invalid module: %s" %
                                 module_path)
            module.model = model
            module.path = module_path.replace(src_path, "")[1:]
            model.modules.append(module)

    model_processor(model)

    resolver = RESTResolver(rest_res_strategy)
    resolver.resolve_model(model)

    return model
