"""
Tests simple example.
"""
import os
from talkie.lang.meta import get_metamodel
from talkie.utils import get_root_path
from talkie.generator.generator import TalkieGenerator


def test_example():
    metamodel = get_metamodel()
    path = os.path.join(get_root_path(), "tests", "examples",
                        "example.tl")
    model = metamodel.model_from_file(path)

    output_dir = os.path.join(get_root_path(), "talkie", "generator",
                              "src-gen")

    generator = TalkieGenerator(model)
    generator.generate(output_dir)
