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

    generator = TalkieGenerator(model)
    generator.generate()
