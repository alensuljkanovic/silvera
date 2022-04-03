import os
import shutil
import pytest
from silvera.cli import init, check
from click.testing import CliRunner

from silvera.utils import get_root_path


@pytest.fixture()
def remove_test_project():
    path = os.path.join(get_root_path(), "tests", "test_project")
    if os.path.exists(path):
        shutil.rmtree(path)

    yield

    # Remove test_project after test ends
    if os.path.exists(path):
        shutil.rmtree(path)


def test_init(remove_test_project):
    runner = CliRunner()
    init_res = runner.invoke(init, ["test_project"])
    assert init_res.exit_code == 0

    check_res = runner.invoke(check, ["test_project"])
    assert check_res.exit_code == 0
