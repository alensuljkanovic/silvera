import os
import pytest
from silvera.generator.generator import generate
from silvera.run import run
from silvera.utils import get_root_path
from click.testing import CliRunner
from silvera.cli import silvera

def test_schematic():
    example_path = os.path.join(get_root_path(), "tests", "examples",
                                "schematic")

    run(example_path)
