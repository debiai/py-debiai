import pytest
from debiai.debiai import Debiai
from debiai.debiai_project import Debiai_project
from debiai.config import get_config

config = get_config()
debiai_instance = Debiai(config.debiai_app_url)

print("\n\nTesting the DebiAI Python module on the",
      config.debiai_app_url, "DebiAI app\n")


project_name = "test_project"
test_project = None


def test_project_list():
    projects = debiai_instance.get_projects()
    assert type(projects) is list


def test_project_creation():
    nb_projects = len(debiai_instance.get_projects())

    global test_project
    test_project = debiai_instance.create_project(project_name)

    assert type(test_project) is Debiai_project
    assert len(debiai_instance.get_projects()) == nb_projects + 1

    with pytest.raises(ValueError) as excinfo:
        debiai_instance.create_project(None)
    assert "cannot be empty" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        debiai_instance.create_project("")
    assert "cannot be empty" in str(excinfo.value)


def test_project_with_same_name():
    with pytest.raises(ValueError) as excinfo:
        debiai_instance.create_project(project_name)
    assert "already exist" in str(excinfo.value)


def test_get_project_by_name():
    project = debiai_instance.get_project(project_name)

    assert project is not None
    assert project.name == project_name


def test_project_deletion():
    nb_projects = len(debiai_instance.get_projects())

    assert debiai_instance.delete_project(test_project)
    assert len(debiai_instance.get_projects()) == nb_projects - 1
    assert debiai_instance.get_project(project_name) is None


def test_project_deletion_by_id():
    test_project = debiai_instance.create_project(project_name)
    nb_projects = len(debiai_instance.get_projects())
    debiai_instance.delete_project_byId(test_project.id)

    assert len(debiai_instance.get_projects()) == nb_projects - 1
