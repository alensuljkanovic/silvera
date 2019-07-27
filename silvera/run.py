import os
import fnmatch
from silvera.generator.generator import generate
from silvera.lang.meta import get_metamodel
from silvera.lang.obj_processors import model_processor
from silvera.core import Model
from silvera.utils import get_root_path


def run(tl_path, output_dir=None):
    """Runs Silvera

    After this function is called, Silvera will process the given .tl file,
    run a compiler and start an application.
    """
    meta = get_metamodel()
    model = meta.model_from_file(tl_path)

    if output_dir is None:
        output_dir = os.path.join(get_root_path(), "silvera", "generator",
                                  "src-gen")

    generate(model, output_dir)


_metamodel = None


def load(src_path):
    """Loads project

    Args:
        src_path(str): path to the project root dir, or to a single .tl file.

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
    for root, dirs, filenames in os.walk(src_path):
        for filename in fnmatch.filter(filenames, "*.tl"):
            module_path = os.path.join(root, filename)
            module = _metamodel.model_from_file(module_path)
            module.model = model
            module.path = module_path.replace(src_path, "")[1:]
            model.modules.append(module)

    model_processor(model)
    return model
