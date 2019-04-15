from talkie.const import HTTP_GET, HTTP_POST
from talkie.lang.meta import get_metamodel
from talkie.resolvers import RESTResolver
from talkie.utils import get_root_path
import pytest
import os


@pytest.fixture()
def examples_path():
    return os.path.join(get_root_path(), "tests", "examples", "resolving")


@pytest.fixture()
def metamodel():
    return get_metamodel()


def test_no_params_no_strategy(metamodel, examples_path):
    path = os.path.join(examples_path, "resolving_no_params.tl")
    model = metamodel.model_from_file(path)

    resolver = RESTResolver()
    resolver.resolve_model(model)

    service = model.service_by_name("TestService")
    func = service.get_function("getAll")
    assert func.http_verb == HTTP_GET
    assert func.rest_path == "testservice/getall/"


def test_one_param_no_strategy(metamodel, examples_path):
    path = os.path.join(examples_path, "resolving_one_param_no_strategy.tl")
    model = metamodel.model_from_file(path)

    resolver = RESTResolver()

    with pytest.raises(TypeError):
        resolver.resolve_model(model)


def test_multiple_params_no_strategy(metamodel, examples_path):
    path = os.path.join(examples_path, "resolving_mult_params_no_strategy.tl")
    model = metamodel.model_from_file(path)

    resolver = RESTResolver()
    resolver.resolve_model(model)

    service = model.service_by_name("TestService")
    func = service.get_function("getObject")
    assert func.http_verb == HTTP_GET
    assert func.rest_path == "testservice/getobject/{name}/{description}"


def test_one_param_post_annotation(metamodel, examples_path):
    path = os.path.join(examples_path, "resolving_one_param_post.tl")
    model = metamodel.model_from_file(path)

    resolver = RESTResolver()
    resolver.resolve_model(model)

    service = model.service_by_name("TestService")
    func = service.get_function("addCustomObject")
    assert func.http_verb == HTTP_POST
    assert func.rest_path == "testservice/addcustomobject/"


def test_resolving_with_dependencies(metamodel, examples_path):
    path = os.path.join(examples_path, "resolving_with_dependencies.tl")
    model = metamodel.model_from_file(path)

    resolver = RESTResolver()
    resolver.resolve_model(model)

    print_service = model.service_by_name("PrintService")
    print_func = print_service.get_function("print")
    assert print_func.http_verb == HTTP_GET
    assert print_func.rest_path == "printservice/print/{id}"

    office_service = model.service_by_name("OfficeService")
    office_print_func = office_service.get_function("print")
    assert office_print_func.http_verb == HTTP_GET
    assert office_print_func.rest_path == "printservice/print/{id}"

    office_print_func = office_service.get_function("addWorker")
    assert office_print_func.http_verb == HTTP_POST
    assert office_print_func.rest_path == "officeservice/addworker/"
