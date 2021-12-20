"""
This module test inheritance mechanism
"""
import os
import pytest

from silvera.run import load
from silvera.utils import get_root_path


@pytest.fixture()
def examples_path():
    return os.path.join(get_root_path(), "tests", "examples")


def test_cfg_and_reg_inheritance(examples_path):

    model = load(os.path.join(examples_path, "inheritance", "cfg_reg"))
    user_service = model.find_by_fqn("user.UserService")
    new_user_service = model.find_by_fqn("user.NewUserService")

    assert new_user_service.extends is user_service
    assert new_user_service.config_server is user_service.config_server
    assert new_user_service.service_registry is user_service.service_registry


def test_deployment_inheritance(examples_path):

    model = load(os.path.join(examples_path, "inheritance", "deployment"))

    user_service = model.find_by_fqn("user.UserService")
    changed_service = model.find_by_fqn("user.ChangedUserService")

    ch_deployment = changed_service.deployment
    ch_restart = ch_deployment.restart_policy
    base_deployment = user_service.deployment
    base_restart = base_deployment.restart_policy

    assert ch_deployment.version == "0.2.1"
    assert ch_deployment.port == 8081
    assert ch_deployment.lang == "python"
    assert ch_deployment.packaging == "wheel"
    assert ch_deployment.host == base_deployment.host
    assert ch_restart.condition == "on-failure"
    assert ch_restart.max_attempts == 3
    assert ch_restart.delay == base_restart.delay
    assert ch_restart.window == base_restart.window
    assert ch_deployment.replicas == base_deployment.replicas


def test_api_inheritance(examples_path):

    model = load(os.path.join(examples_path, "inheritance", "api"))

    user_service = model.find_by_fqn("user.UserService")
    changed_service = model.find_by_fqn("user.ChangedUserService")

    base_login = user_service.get_function("login")

    assert changed_service.get_function("login") is base_login
    assert changed_service.get_function("logout")

    user_obj = user_service.domain_objs["User"]

    ch_user_obj = changed_service.domain_objs["User"]
    assert ch_user_obj.name == user_obj.name
    assert ch_user_obj.fields[0].type == user_obj.fields[0].type
    assert ch_user_obj.fields[0].name == user_obj.fields[0].name
    assert ch_user_obj.fields[1].type == user_obj.fields[1].type
    assert ch_user_obj.fields[1].name == user_obj.fields[1].name
    assert ch_user_obj.fields[2].type == user_obj.fields[2].type
    assert ch_user_obj.fields[2].name == user_obj.fields[2].name
