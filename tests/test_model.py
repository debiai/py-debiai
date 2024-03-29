import pytest
from debiai.debiai import Debiai
from debiai.debiai_project import Debiai_project
from tests.config import get_config


@pytest.fixture(scope="module", autouse=True)
def setup_module():
    # Code executed at the beginning of running the test module
    PROJECT_NAME = "test_model_project"
    config = get_config()
    debiai_instance = Debiai(config.debiai_app_url)

    # Create a DebiAI object
    project = debiai_instance.create_project(PROJECT_NAME)

    yield project

    # Code executed at the end of running the test module
    # Delete the project
    debiai_instance.delete_project(project)


def test_bad_model_creation(setup_module):
    project: Debiai_project = setup_module

    # Create a model with missing name
    with pytest.raises(TypeError) as execution_info:
        project.create_model()
    assert "missing 1 required" in str(execution_info.value)

    with pytest.raises(ValueError) as execution_info:
        project.create_model("")
    assert "name is required" in str(execution_info.value)


def test_delete_model(setup_module):
    project: Debiai_project = setup_module

    # Create a model
    model1 = project.create_model("Model 1")
    project.create_model("Model 2")

    # Delete the model
    project.delete_model(model1)
    project.delete_model("Model 2")

    # Check if the model is deleted
    assert project.get_model("Model 1") is None
    assert project.get_model("Model 2") is None

    # Try to delete in a wrong way
    with pytest.raises(ValueError) as execution_info:
        project.delete_model(model1)
    assert "does not exist" in str(execution_info.value)
    with pytest.raises(ValueError) as execution_info:
        project.delete_model("Model 2")
    assert "does not exist" in str(execution_info.value)
    with pytest.raises(ValueError) as execution_info:
        project.delete_model("")
    assert "name is required" in str(execution_info.value)
    with pytest.raises(ValueError) as execution_info:
        project.delete_model({})
    assert "name must be a string" in str(execution_info.value)


def test_bad_expected_results(setup_module):
    project: Debiai_project = setup_module

    # Set expected results with missing results
    with pytest.raises(TypeError) as execution_info:
        project.set_expected_results()
    assert "missing 1 required" in str(execution_info.value)

    with pytest.raises(ValueError) as execution_info:
        project.set_expected_results([])
    assert "At least one" in str(execution_info.value)

    # Wrong type
    with pytest.raises(ValueError) as execution_info:
        project.set_expected_results({})
    assert "must be a list" in str(execution_info.value)

    with pytest.raises(ValueError) as execution_info:
        project.set_expected_results([""])
    assert "must be a dict" in str(execution_info.value)

    # Missing name field
    with pytest.raises(ValueError) as execution_info:
        project.set_expected_results(
            [
                {"type": "number"},
                {"name": "Model confidence", "type": "number"},
                {"name": "Model error", "type": "text"},
            ]
        )
    assert "'name' is required" in str(execution_info.value)

    # Missing type field
    with pytest.raises(ValueError) as execution_info:
        project.set_expected_results(
            [
                {"name": "Model result"},
                {"name": "Model confidence", "type": "number"},
                {"name": "Model error", "type": "text"},
            ]
        )
    assert "'type' is required" in str(execution_info.value)

    # Duplicate name
    with pytest.raises(ValueError) as execution_info:
        project.set_expected_results(
            [
                {"name": "Model result", "type": "number"},
                {"name": "Model result", "type": "number"},
                {"name": "Model error", "type": "text"},
            ]
        )
    assert "need to be unique" in str(execution_info.value)

    # Bad group
    with pytest.raises(ValueError) as execution_info:
        project.set_expected_results(
            [
                {"name": "Model result", "type": "number"},
                {"name": "Model confidence", "type": "number"},
                {"name": "Model error", "type": "text", "group": 1},
            ]
        )
    assert "must be a string" in str(execution_info.value)


def test_expected_results(setup_module):
    project: Debiai_project = setup_module

    # Set expected results
    project.set_expected_results(
        [
            {"name": "Model result", "type": "number"},
            {"name": "Model confidence", "type": "number"},
            {"name": "Model error", "type": "text", "group": "My group 1"},
        ]
    )

    # Get expected results
    expected_results = project.get_expected_results()

    assert expected_results == [
        {"name": "Model result", "type": "number"},
        {"name": "Model confidence", "type": "number"},
        {"name": "Model error", "type": "text", "group": "My group 1"},
    ]

    # Add again
    with pytest.raises(ValueError) as execution_info:
        project.set_expected_results(
            [
                {"name": "Model result", "type": "number"},
                {"name": "Model confidence", "type": "number"},
                {"name": "Model error", "type": "text", "group": "My group 1"},
            ]
        )
    assert "already set" in str(execution_info.value)
