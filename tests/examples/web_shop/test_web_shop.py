import os
import pytest
from silvera.generator.generator import generate
from silvera.run import run
from silvera.utils import get_root_path


def test_web_shop():
    example_path = os.path.join(get_root_path(), "tests", "examples",
                                "web_shop")
    run(example_path)
