from silvera.const import HTTP_GET, HTTP_POST
from silvera.lang.meta import get_metamodel
from silvera.resolvers import RESTResolver
from silvera.run import load
from silvera.utils import get_root_path
from silvera.exceptions import SilveraTypeError, SilveraLoadError
import pytest
import os


@pytest.fixture()
def examples_path():
    return os.path.join(get_root_path(), "tests", "examples", "resolving")


@pytest.fixture()
def metamodel():
    return get_metamodel()


def test_no_params_no_strategy(metamodel, examples_path):
    path = os.path.join(examples_path, "no_par_no_str")
    model = load(path)

    resolver = RESTResolver()
    resolver.resolve_model(model)

    service = model.find_by_fqn("test.TestService")
    func = service.get_function("getAll")
    assert func.http_verb == HTTP_GET
    assert func.rest_path == "testservice/getall/"


def test_one_param_no_strategy(metamodel, examples_path):
    path = os.path.join(examples_path, "one_par_no_str")
    model = load(path)

    resolver = RESTResolver()
    resolver.resolve_model(model)

    service = model.find_by_fqn("test.TestService")
    func = service.get_function("addCustomObject")
    assert func.http_verb == HTTP_GET
    assert func.rest_path == "testservice/addcustomobject/{o}"


def test_multiple_params_no_strategy(metamodel, examples_path):
    path = os.path.join(examples_path, "mult_par_no_str")
    model = load(path)

    resolver = RESTResolver()
    resolver.resolve_model(model)

    service = model.find_by_fqn("test.TestService")
    func = service.get_function("getObject")
    assert func.http_verb == HTTP_GET
    assert func.rest_path == "testservice/getobject/{name}/{description}"


def test_one_param_post_annotation(metamodel, examples_path):
    path = os.path.join(examples_path, "one_par_post")
    model = load(path)

    resolver = RESTResolver()
    resolver.resolve_model(model)

    service = model.find_by_fqn("test.TestService")
    func = service.get_function("addCustomObject")
    assert func.http_verb == HTTP_POST
    assert func.rest_path == "testservice/addcustomobject/"


def test_resolving_with_dependencies(metamodel, examples_path):
    path = os.path.join(examples_path, "dep")
    model = load(path)

    resolver = RESTResolver()
    resolver.resolve_model(model)

    print_service = model.find_by_fqn("print.PrintService")
    print_func = print_service.get_function("print")
    assert print_func.http_verb == HTTP_GET
    assert print_func.rest_path == "printservice/print/{id}"

    office_service = model.find_by_fqn("print.OfficeService")
    office_print_func = office_service.get_function("print")
    assert office_print_func.dep.rest_path == "printservice/print/{id}"
    assert office_print_func.dep.http_verb == HTTP_GET
    assert office_print_func.rest_path == "officeservice/print/{id}"

    office_print_func = office_service.get_function("addWorker")
    assert office_print_func.http_verb == HTTP_POST
    assert office_print_func.rest_path == "officeservice/addworker/"


def test_with_connections_and_inherit(examples_path):
    model = load(os.path.join(examples_path, "connections", "ok"))

    resolver = RESTResolver()
    resolver.resolve_model(model)

    new_office_service = model.find_by_fqn("print.NewOfficeService")

    new_print = new_office_service.get_function("print")
    assert new_print.http_verb == HTTP_GET
    assert new_print.rest_path == "newofficeservice/print/{id}"
    assert new_print.dep.http_verb == HTTP_GET
    assert new_print.dep.rest_path == "fastprintservice/print/{id}"

    new_fast_print = new_office_service.get_function("fastPrint")
    assert new_fast_print.http_verb == HTTP_POST
    assert new_fast_print.rest_path == "newofficeservice/fastprint/"
    assert new_fast_print.dep.http_verb == HTTP_POST
    assert new_fast_print.dep.rest_path == "fastprintservice/fastprint/"


def test_connections_with_different_style(examples_path):

    with pytest.raises(SilveraLoadError):
        load(os.path.join(examples_path, "connections", "error"))


def test_function_return_type_resolving_error(examples_path):

    with pytest.raises(Exception):
        load(os.path.join(examples_path, "types", "functions", "return_type",
                          "typedef"))

    with pytest.raises(Exception):
        load(os.path.join(examples_path, "types", "functions", "return_type"
                          "typed_list"))


def test_function_param_type_resolving_error(examples_path):

    with pytest.raises(SilveraTypeError):
        load(os.path.join(examples_path, "types", "functions", "param",
                          "typedef"))

    with pytest.raises(SilveraTypeError):
        load(os.path.join(examples_path, "types", "functions", "param",
                          "typed_list"))


def test_typedef_resolving_error(examples_path):

    with pytest.raises(SilveraTypeError):
        load(os.path.join(examples_path, "types", "typedefs", "td"))

    with pytest.raises(SilveraTypeError):
        load(os.path.join(examples_path, "types", "typedefs", "typed_list"))