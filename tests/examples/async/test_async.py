import os
import pytest
from silvera.run import compile
from silvera.utils import get_root_path


@pytest.fixture
def example_path():
    example_path = os.path.join(get_root_path(), "tests", "examples", "async")
    return example_path


def test_async(example_path):
    compile(example_path, output_dir=os.path.join(example_path, "src-gen"))
