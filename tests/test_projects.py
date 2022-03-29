import pytest
from debiai.debiai import Debiai
from debiai.debiai_project import Debiai_project
from debiai.config import get_config

config = get_config()
debiai_instance = Debiai(config.debiai_app_url)

print(
    "\n\nTesting the DebiAI Python module on the", config.debiai_app_url, "DebiAI app\n"
)

PROJECT_NAME = "test_project"


def test_project_list():
    projects = debiai_instance.get_projects()
    assert isinstance(projects, list)


def test_project_creation():
    nb_projects = len(debiai_instance.get_projects())

    # Create a project
    project = debiai_instance.create_project(PROJECT_NAME)

    assert isinstance(project, Debiai_project)
    assert len(debiai_instance.get_projects()) == nb_projects + 1

    # Test few edge cases
    with pytest.raises(ValueError) as excinfo:
        debiai_instance.create_project(None)
    assert "cannot be empty" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        debiai_instance.create_project("")
    assert "cannot be empty" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        debiai_instance.create_project(PROJECT_NAME)
    assert "already exist" in str(excinfo.value)

    # Get project by name
    project = debiai_instance.get_project(PROJECT_NAME)

    assert project is not None
    assert project.name == PROJECT_NAME

    # delete project
    assert debiai_instance.delete_project(project)
    assert len(debiai_instance.get_projects()) == nb_projects
    assert debiai_instance.get_project(PROJECT_NAME) is None


def test_project_deletion_by_id():
    project = debiai_instance.create_project(PROJECT_NAME)
    nb_projects = len(debiai_instance.get_projects())
    debiai_instance.delete_project_byId(project.id)

    assert len(debiai_instance.get_projects()) == nb_projects - 1
