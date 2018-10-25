import os

from talkie.generator.generator import TalkieGenerator
from talkie.lang.meta import get_metamodel
from talkie.utils import get_root_path


def run(tl_path, output_dir=None):
    """Runs Talkie

    After this function is called, Talkie will process the given .tl file,
    run a compiler and start an application.
    """
    meta = get_metamodel()
    model = meta.model_from_file(tl_path)

    if output_dir is None:
        output_dir = os.path.join(get_root_path(), "talkie", "generator",
                                  "src-gen")

    generator = TalkieGenerator(model)
    generator.generate(output_dir)

