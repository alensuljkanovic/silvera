import os

from silvera.openapi.serialization import OpenAPIDump
from silvera.run import load
from openapi_spec_validator import validate_spec
from openapi_spec_validator.readers import read_from_filename


def test_openapi():
    file_dir = os.path.dirname(os.path.realpath(__file__))
    model_path = os.path.join(file_dir, "example")

    model = load(model_path)

    user_service = model.find_by_fqn("user.User")
    OpenAPIDump.dump(user_service, model_path)

    # test if file is valid
    spec_dict, _ = read_from_filename(os.path.join(model_path, "openapi.json"))
    validate_spec(spec_dict)
