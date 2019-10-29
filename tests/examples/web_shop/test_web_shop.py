import os
import shutil
import pytest
from silvera.run import run
from silvera.utils import get_root_path


@pytest.fixture
def example_path():
    example_path = os.path.join(get_root_path(), "tests", "examples",
                                "web_shop")
    yield example_path

    # Remove generated folders
    for s in ["ConfigServer", "PaymentService", "ProductService",
              "ServiceRegistry", "ShoppingCartService", "UserService"]:
        path = os.path.join(example_path, s)
        if os.path.exists(path):
            shutil.rmtree(path)


def test_web_shop(example_path):
    run(example_path)
