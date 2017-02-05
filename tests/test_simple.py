"""
Tests simple example.
"""
import os

from generator.generator import TalkieGenerator
from talkie.lang.meta import get_metamodel
from talkie.utils import get_root_path


def test_simple():
    metamodel = get_metamodel()
    path = os.path.join(get_root_path(), "tests", "examples", "simple_interface.tl")
    model = metamodel.model_from_file(path)

    generator = TalkieGenerator(model)
    generator.generate()