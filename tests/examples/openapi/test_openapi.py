import os

from silvera.openapi.serialization import OpenAPIDump
from silvera.run import load


def test_openapi():
    file_dir = os.path.dirname(os.path.realpath(__file__))
    model_path = os.path.join(file_dir, "example")

    model = load(model_path)

    user_service = model.find_by_fqn("user.User")
    OpenAPIDump.dump(user_service, model_path)
