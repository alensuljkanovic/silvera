"""
Tests simple example.
"""
import os
from talkie.lang.meta import get_metamodel
from talkie.utils import get_root_path


def test_example():
    examples_path = os.path.join(get_root_path(), "tests", "examples")

    metamodel = get_metamodel()
    path = os.path.join(examples_path, "example.tl")
    metamodel.model_from_file(path)
