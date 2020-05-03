import os
import pytest
from silvera.utils import get_root_path
from silvera.run import load


@pytest.fixture()
def examples_path():
    return os.path.join(get_root_path(), "tests", "examples", "annotations")


def test_multiple_annotations(examples_path):
    model = load(os.path.join(examples_path, "multiple"))

    service = model.find_by_fqn("multiple_ann.TestService")
    fnc_add = service.get_function("add")
    assert len(fnc_add.annotations) == 3
    assert fnc_add.is_async()
