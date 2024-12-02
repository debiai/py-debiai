import pandas as pd
import pytest
from debiai.debiai import Debiai
from debiai.debiai_project import Debiai_project
from debiai.config import get_config

config = get_config()
debiai_instance = Debiai(config.debiai_app_url)

PROJECT_NAME = "test_edge_cases"
EMPTY_PROJECT_NAME = "test_empty_project"
SELECTION_NAME = "test_edge_case_selection"


def test_edge_cases():
    # Setup: Clean up any existing projects
    if debiai_instance.get_project(PROJECT_NAME) is not None:
        assert debiai_instance.delete_project_byId(PROJECT_NAME)
    if debiai_instance.get_project(EMPTY_PROJECT_NAME) is not None:
        assert debiai_instance.delete_project_byId(EMPTY_PROJECT_NAME)
    project = debiai_instance.create_project(EMPTY_PROJECT_NAME)
    project = debiai_instance.create_project(PROJECT_NAME)
    assert isinstance(project, Debiai_project)

    block_structure = [
        {
            "name": "Image ID",
            "contexts": [
                {"name": "My context 1", "type": "text"},
                {"name": "My context 2", "type": "number", "group": "My group 1"},
            ],
            "groundTruth": [{"name": "My groundtruth 1", "type": "number"}],
        }
    ]

    # Test: Missing block structure
    with pytest.raises(TypeError) as e:
        project.set_blockstructure(None)
    assert "must be a list" in str(e.value)

    # Test: Invalid block structure type
    with pytest.raises(TypeError) as e:
        project.set_blockstructure("invalid_structure")
    assert "must be a list" in str(e.value)

    project.set_blockstructure(block_structure)

    # Test: second call to set_blockstructure should fail
    with pytest.raises(ValueError) as e:
        project.set_blockstructure(block_structure)
    assert "already created" in str(e.value)

    # Test: Missing or incorrect sample data
    invalid_samples_df = pd.DataFrame(
        {
            "Image ID": ["image-1", "image-2"],
            # Missing "My context 2" and "My groundtruth 1"
            "My context 1": ["A", "B"],
        }
    )
    with pytest.raises(ValueError) as e:
        project.add_samples_pd(invalid_samples_df)
    assert "My context 2" in str(e.value)
    assert "missing" in str(e.value)

    # Test: Add invalid sample data type
    with pytest.raises(TypeError) as e:
        project.add_samples_pd({"Invalid": "data"})
    assert "must be a pandas DataFrame" in str(e.value)

    # Test: Add empty DataFrame
    empty_df = pd.DataFrame()
    assert not project.add_samples_pd(empty_df)

    # # Test: Adding duplicate samples
    # # Duplicate samples should replace existing samples
    # valid_samples_df_1 = pd.DataFrame(
    #     {
    #         "Image ID": ["image-1", "image-2"],
    #         "My context 1": ["A", "B"],
    #         "My context 2": [0.28, 0.388],
    #         "My groundtruth 1": [8, 7],
    #     }
    # )
    # assert project.add_samples_pd(valid_samples_df_1)
    # get_samples_df = project.get_dataframe()
    # assert get_samples_df.shape[0] == 2
    # assert get_samples_df["My context 1"].tolist() == ["A", "B"]

    # valid_samples_df_2 = pd.DataFrame(
    #     {
    #         "Image ID": ["image-1", "image-2"],
    #         "My context 1": ["D", "E"],
    #         "My context 2": [0.28, 0.388],
    #         "My groundtruth 1": [8, 7],
    #     }
    # )
    # assert project.add_samples_pd(valid_samples_df_2)
    # new_samples_df = project.get_dataframe()
    # assert new_samples_df.shape[0] == 2
    # assert new_samples_df["My context 1"].tolist() == ["D", "E"]

    # Test: Retrieve samples with an empty project
    with pytest.raises(ValueError) as e:
        project_empty = debiai_instance.get_project(EMPTY_PROJECT_NAME)
        project_empty.get_dataframe()
    assert "structure hasn't been set" in str(e.value)

    # Test: Create selection with missing sample_id
    with pytest.raises(ValueError) as e:
        project.create_selection(selection_name=SELECTION_NAME, samples_id=None)
    assert "list is required" in str(e.value)

    # Test: Create selection with invalid sample_id type
    with pytest.raises(TypeError) as e:
        project.create_selection(selection_name=SELECTION_NAME, samples_id="invalid")
    assert "must be a list" in str(e.value)
    with pytest.raises(ValueError) as e:
        project.create_selection(selection_name=SELECTION_NAME, samples_id=[1, 2, 3])
    assert "list of string" in str(e.value)

    # Test: Create selection with non-existent sample_id
    invalid_sample_id = "non_existent_sample_id"
    with pytest.raises(ValueError) as e:
        project.create_selection(
            selection_name=SELECTION_NAME, samples_id=[invalid_sample_id]
        )
    assert invalid_sample_id in str(e.value)
    assert "do not exist" in str(e.value)

    # Test: Retrieve non-existent selection
    assert project.get_selection("non_existent_selection") is None

    # Test: Delete non-existent selection
    with pytest.raises(ValueError) as e:
        project.delete_selection("non_existent_selection")
    assert "does not exist" in str(e.value)

    # Test: Invalid deletion of project
    with pytest.raises(ValueError) as e:
        debiai_instance.delete_project(None)
    assert "cannot be None" in str(e.value)
    with pytest.raises(ValueError) as e:
        debiai_instance.delete_project_byId(None)
    assert "cannot be empty" in str(e.value)
    with pytest.raises(ValueError) as e:
        debiai_instance.delete_project_byId(20)
    assert "string" in str(e.value)

    # Cleanup
    assert debiai_instance.delete_project(project)
    assert debiai_instance.get_project(PROJECT_NAME) is None
    assert debiai_instance.delete_project_byId(EMPTY_PROJECT_NAME)
    assert debiai_instance.get_project(EMPTY_PROJECT_NAME) is None
