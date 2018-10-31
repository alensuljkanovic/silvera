"""
Tests simple example.
"""
import os
from talkie.lang.meta import get_metamodel
from talkie.utils import get_root_path
from talkie.generator.generator import TalkieGenerator

import yaml


def test_example():
    examples_path = os.path.join(get_root_path(), "tests", "examples")

    with open(os.path.join(examples_path, "rest.yaml")) as f:
        p = yaml.load(f)

    metamodel = get_metamodel()
    path = os.path.join(examples_path, "example.tl")
    model = metamodel.model_from_file(path)
    print(model)
    # model.add_rest_info(p)
    #
    # output_dir = os.path.join(get_root_path(), "talkie", "generator",
    #                           "src-gen")
    #
    # generator = TalkieGenerator(model)
    # generator.generate(output_dir)
