import os
import shutil
import pytest
from silvera.generator.generator import generate
from silvera.run import run
from silvera.utils import get_root_path
from click.testing import CliRunner
from silvera.cli import silvera

@pytest.fixture
def example_path():
    example_path = os.path.join(get_root_path(), "tests", "examples",
                                "schematic")
    yield example_path

    # Remove generated folders
    for s in ["SchemeService", "LibraryService", "CompileService"]:
        path = os.path.join(example_path, s)
        if os.path.exists(path):
            shutil.rmtree(path)

def test_schematic(example_path):
    run(example_path)
