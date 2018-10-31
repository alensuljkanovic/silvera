import os
import yaml

from talkie.generator.generator import TalkieGenerator
from talkie.lang.meta import get_metamodel
from talkie.utils import get_root_path


def test_example():
    examples_path = os.path.join(get_root_path(), "tests", "examples",
                                 "web-shop")

    with open(os.path.join(examples_path, "rest.yaml")) as f:
        p = yaml.load(f)

    metamodel = get_metamodel()
    path = os.path.join(examples_path, "web-shop.tl")
    model = metamodel.model_from_file(path)
    model.add_rest_info(p)
    print(model)

    output_dir = os.path.join(get_root_path(), "talkie", "generator",
                              "src-gen")

    generator = TalkieGenerator(model)
    generator.generate(output_dir)

