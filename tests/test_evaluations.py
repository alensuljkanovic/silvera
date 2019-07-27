import os
import pytest

from talkie.evaluation import Evaluator
from talkie.run import load
from talkie.utils import get_root_path


@pytest.fixture()
def examples_path():
    return os.path.join(get_root_path(), "tests", "examples")


def test_coupling(examples_path):
    model = load(os.path.join(examples_path, "metrics", "coupling"))

    evaluator = Evaluator()
    evaluator.evaluate(model)
