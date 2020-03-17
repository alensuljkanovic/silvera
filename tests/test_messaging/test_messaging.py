"""This module contains tests for messaging communication style"""
import os
import pytest
from silvera.utils import get_root_path
from silvera.run import load
from silvera.exceptions import SilveraLoadError


@pytest.fixture()
def examples_path():
    return os.path.join(get_root_path(), "tests", "test_messaging")


def test_multiple_msg_pools(examples_path):
    mult_pools = os.path.join(examples_path, "multiple_pools")

    with pytest.raises(SilveraLoadError):
        load(mult_pools)


def test_msg_pool_all_groups(examples_path):
    example = os.path.join(examples_path, "messaging")
    model = load(example)

    msg_pool = model.msg_pool

    groups = msg_pool.get_all_groups()
    assert len(groups) == 3

    expected = {"TaskMsgGroup", "BoardMsgGroup", "EmployeeMsgGroup"}
    actual = {g.name for g in groups}
    assert expected == actual


def test_msg_pool_get_all(examples_path):
    example = os.path.join(examples_path, "messaging")
    model = load(example)

    msg_pool = model.msg_pool

    messages = msg_pool.messages
    assert len(messages) == 7
    expected = {"AssignTask", "CloseTask", "TASK_CREATED", "TASK_ASSIGNED",
                "TASK_CLOSED", "BOARD_CREATED", "EMPLOYEE_CREATED"}
    actual = {m.name for m in messages}
    assert expected == actual


def test_msg_fqn(examples_path):
    example = os.path.join(examples_path, "messaging")
    model = load(example)

    msg_pool = model.msg_pool
    msg = msg_pool.groups[0].messages[0]
    assert msg.fqn == "TaskMsgGroup.AssignTask"


def test_find_msg_by_fqn(examples_path):
    example = os.path.join(examples_path, "messaging")
    model = load(example)

    msg_pool = model.msg_pool

    assign_task = msg_pool.get("TaskMsgGroup.AssignTask")
    assert len(assign_task.fields) == 2
    assert assign_task.name == "AssignTask"


def test_same_empty_msg_group(examples_path):
    example = os.path.join(examples_path, "empty_group")

    with pytest.raises(SilveraLoadError) as exc_info:
        load(example)

    exc = exc_info.value
    print(exc)


def test_unique_msg_group_id(examples_path):
    example = os.path.join(examples_path, "group_redefinitions")

    with pytest.raises(SilveraLoadError) as exc_info:
        load(example)

    exc = exc_info.value
    print(exc)


def test_unique_msg_name(examples_path):
    example = os.path.join(examples_path, "message_redefinition")

    with pytest.raises(SilveraLoadError) as exc_info:
        load(example)

    exc = exc_info.value
    print(exc)


