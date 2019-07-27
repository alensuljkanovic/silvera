"""
This module tests loading mechanism
"""
import os
import pytest
from silvera.run import load
from silvera.core import ConfigServerDecl, ServiceRegistryDecl
from silvera.utils import get_root_path


@pytest.fixture()
def examples_path():
    return os.path.join(get_root_path(), "tests", "examples")


def test_load_ok(examples_path):

    model = load(os.path.join(examples_path, "importing", "ok"))
    assert len(model.modules) == 5

    # Find objects from share/setup.tl
    config_server = model.find_by_fqn("share.setup.ConfigServer")
    assert isinstance(config_server, ConfigServerDecl)
    service_reg = model.find_by_fqn("share.setup.ServiceRegistry")
    assert isinstance(service_reg, ServiceRegistryDecl)

    # Load services
    user_service = model.find_by_fqn("user.UserService")
    payment_service = model.find_by_fqn("payment.PaymentService")

    # Check if references towards ConfigServer and ServiceRegistry are
    # resolved properly.
    assert user_service.config_server is config_server
    assert user_service.service_registry is service_reg
    assert payment_service.config_server is config_server
    assert payment_service.service_registry is service_reg

    # Check if references towards other services are resolved properly
    payment_module = model.find_by_path("payment.tl")
    connections = list(payment_module.connections)
    # Check connection PaymentService -> user.UserService
    pay_to_user = connections[0]
    assert pay_to_user.start is payment_service
    assert pay_to_user.end is user_service


def test_missing_import(examples_path):
    with pytest.raises(KeyError) as exc_info:
        load(os.path.join(examples_path, "importing", "errors",
                          "missing_import"))
    exc_obj = exc_info.value
    expected_msg = '"Declaration with name \'ServiceRegistry\' not found!"'
    assert str(exc_obj) == expected_msg


def test_multiple_defs(examples_path):
    with pytest.raises(ValueError) as exc_info:
        load(os.path.join(examples_path, "importing", "errors",
                          "multiple_defs"))

    msg = "Definition of object ServiceRegistry found in multiple modules: "\
          "[first_setup.tl, second_setup.tl]"
    exc_obj = exc_info.value
    assert str(exc_obj) == msg


def test_cyclic_imports(examples_path):
    with pytest.raises(ValueError) as exc_info:
        load(os.path.join(examples_path, "importing", "errors",
                          "cyclic_import"))

    msg = "Cyclic import found!"
    exc_obj = exc_info.value
    assert str(exc_obj) == msg


def test_non_existing_dir(examples_path):
    # Test that error will be raised for non-existing directories
    with pytest.raises(ValueError):
        load(os.path.join(examples_path, "non-existing-dir"))


def test_loading_with_custom_types(examples_path):
    model = load(os.path.join(examples_path, "loading"))

    print_service = model.find_by_fqn("print.PrintService")
    doc_type = print_service.domain_objs["Document"]
    print_doc = print_service.get_function("printDoc")
    print_param = print_doc.params[0]
    assert print_param.type is doc_type

    office_service = model.find_by_fqn("office.OfficeService")
    worker = office_service.domain_objs["Worker"]
    rm_worker = office_service.get_function("removeWorker")
    rm_param = rm_worker.params[0]
    assert rm_param.type is worker
    assert rm_worker.ret_type is worker

    new_office_service = model.find_by_fqn("office.NewOfficeService")
    update_worker = new_office_service.get_function("updateWorker")
    up_param = update_worker.params[0]
    assert up_param.type is worker
