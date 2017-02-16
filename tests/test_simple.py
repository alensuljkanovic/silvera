"""
Tests simple example.
"""
import os
from generator.generator import TalkieGenerator
from talkie.lang.meta import get_metamodel
from talkie.utils import get_root_path


def test_simple1():
    metamodel = get_metamodel()
    path = os.path.join(get_root_path(), "tests", "examples",
                        "simple_interface.tl")
    model = metamodel.model_from_file(path)

    generator = TalkieGenerator(model)
    generator.generate()


def test_simple2():
    metamodel = get_metamodel()
    path = os.path.join(get_root_path(), "tests", "examples",
                        "simple_interface2.tl")
    model = metamodel.model_from_file(path)

    generator = TalkieGenerator(model)
    generator.generate()