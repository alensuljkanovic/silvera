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

    with pytest.raises(SilveraLoadError):
        load(example)


def test_unique_msg_group_id(examples_path):
    example = os.path.join(examples_path, "group_redefinitions")

    with pytest.raises(SilveraLoadError):
        load(example)


def test_unique_msg_name(examples_path):
    example = os.path.join(examples_path, "message_redefinition")

    with pytest.raises(SilveraLoadError):
        load(example)


def test_broker(examples_path):
    example = os.path.join(examples_path, "messaging")
    model = load(example)

    msg_pool = model.msg_pool
    broker = model.msg_brokers["Broker"]
    channels = broker.channels
    assert len(channels) == 7

    assign_task_channel = channels["CMD_ASSIGN_TASK_CHANNEL"]
    assign_task_msg = msg_pool.get("TaskMsgGroup.AssignTask")

    assert assign_task_channel.msg_type is assign_task_msg

    task_service = model.find_by_fqn("task.Task")

    # Test `consumes` method
    consumes = task_service.consumes
    assert len(consumes) == 2
    close_task_msg = msg_pool.get("TaskMsgGroup.CloseTask")
    close_task_channel = channels["CMD_CLOSE_TASK_CHANNEL"]
    assert consumes == {
        assign_task_msg: [assign_task_channel],
        close_task_msg: [close_task_channel]
    }

    # Test `produces` method
    produces = task_service.produces
    assert len(produces) == 3
    task_created_msg = msg_pool.get("TaskMsgGroup.TASK_CREATED")
    task_created_ch = channels["EV_TASK_CREATED_CHANNEL"]
    task_assigned_msg = msg_pool.get("TaskMsgGroup.TASK_ASSIGNED")
    task_assigned_ch = channels["EV_TASK_ASSIGNED_CHANNEL"]
    task_closed_msg = msg_pool.get("TaskMsgGroup.TASK_CLOSED")
    task_closed_ch = channels["EV_TASK_CLOSED_CHANNEL"]
    assert produces == {
        task_created_msg: [task_created_ch],
        task_assigned_msg: [task_assigned_ch],
        task_closed_msg: [task_closed_ch]
    }
