import os
import pytest
from silvera.utils import get_root_path
from silvera.run import compile


@pytest.fixture()
def examples_path():
    return os.path.join(get_root_path(), "tests", "examples")


def test_messaging_example(examples_path):
    path = os.path.join(examples_path, "messaging")
    compile(path, output_dir=os.path.join(path, "src-gen"))
