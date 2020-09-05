import os
import pytest
from silvera.run import load
from silvera.utils import get_root_path


@pytest.fixture
def example_path():
    example_path = os.path.join(get_root_path(), "tests", "examples",
                                "classifiers")
    return example_path


def test_classifiers(example_path):
    model = load(example_path)

    student_serv = model.find_by_fqn("student.StudentService")
    student_type = student_serv.api.typedefs[0]

    email_field = student_type.fields[0]
    assert email_field.isid
    assert email_field.required  # ID is required by default
    assert email_field.unique  # ID is unique by default
    assert not email_field.ordered

    first_name_field = student_type.fields[1]
    assert not first_name_field.isid
    assert first_name_field.required
    assert not first_name_field.unique
    assert not first_name_field.ordered

    last_name_field = student_type.fields[2]

    assert not last_name_field.isid
    assert last_name_field.required
    assert not last_name_field.unique
    assert last_name_field.ordered
