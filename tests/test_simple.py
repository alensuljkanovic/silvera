"""
Tests simple example.
"""
import os
from silvera.lang.meta import get_metamodel
from silvera.utils import get_root_path


def test_example():
    examples_path = os.path.join(get_root_path(), "tests", "examples")

    metamodel = get_metamodel()
    path = os.path.join(examples_path, "example.si")
    metamodel.model_from_file(path)
