import pytest
from debiai.debiai import Debiai
from debiai.debiai_project import Debiai_project
from tests.config import get_config


@pytest.fixture(scope="module", autouse=True)
def setup_module():
    # Code executed at the beginning of running the test module
    PROJECT_NAME = "test_selections_project"
    config = get_config()
    debiai_instance = Debiai(config.debiai_app_url)

    # Create a DebiAI object
    project = debiai_instance.create_project(PROJECT_NAME)

    yield project

    # Code executed at the end of running the test module
    # Delete the project
    debiai_instance.delete_project(project)


def test_delete_selection(setup_module):
    project: Debiai_project = setup_module

    # Check if the selection is deleted
    assert project.get_selection("selection 1") is None
    assert project.get_selection("selection 2") is None

    # Try to delete in a wrong way
    with pytest.raises(ValueError) as execution_info:
        project.delete_selection("selection 2")
    assert "does not exist" in str(execution_info.value)
    with pytest.raises(ValueError) as execution_info:
        project.delete_selection("")
    assert "name is required" in str(execution_info.value)
    with pytest.raises(ValueError) as execution_info:
        project.delete_selection({})
    assert "name must be a string" in str(execution_info.value)
