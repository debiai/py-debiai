import pandas as pd
from debiai.debiai import Debiai
from debiai.debiai_project import Debiai_project, Debiai_selection
from debiai.config import get_config

config = get_config()
debiai_instance = Debiai(config.debiai_app_url)

PROJECT_NAME = "test_get_data"
SELECTION_NAME = "test_selection"


def test_get_data():
    # Create or recreate a project
    if debiai_instance.get_project(PROJECT_NAME) is not None:
        assert debiai_instance.delete_project_byId(PROJECT_NAME)
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
    project.set_blockstructure(block_structure)

    # Add samples
    samples_df = pd.DataFrame(
        {
            "Image ID": ["image-1", "image-2", "image-3"],
            "My context 1": ["A", "B", "C"],
            "My context 2": [0.28, 0.388, 0.5],
            "My groundtruth 1": [8, 7, 19],
        }
    )
    assert project.add_samples_pd(samples_df)

    # Get samples
    samples_df_ret = project.get_dataframe()
    assert isinstance(samples_df_ret, pd.DataFrame)
    assert (
        samples_df_ret["My context 1"].tolist() == samples_df["My context 1"].tolist()
    )
    assert (
        samples_df_ret["My context 2"].tolist() == samples_df["My context 2"].tolist()
    )
    assert (
        samples_df_ret["My groundtruth 1"].tolist()
        == samples_df["My groundtruth 1"].tolist()
    )
    assert "sample_id" in samples_df_ret.columns

    # Create a selection
    # Get the "sample_id" of the "image-2" sample
    sample_id = samples_df_ret[samples_df_ret["Image ID"] == "image-2"][
        "sample_id"
    ].iloc[0]
    assert isinstance(sample_id, str)
    new_selection = project.create_selection(
        selection_name=SELECTION_NAME, samples_id=[sample_id]
    )
    assert isinstance(new_selection, Debiai_selection)

    # Get the selections
    selections = project.get_selections()
    assert len(selections) == 1
    assert isinstance(selections[0], Debiai_selection)
    assert selections[0].name == SELECTION_NAME
    assert selections[0].get_samples_id() == [sample_id]

    # Get the selection
    selection = project.get_selection(SELECTION_NAME)
    assert isinstance(selection, Debiai_selection)
    assert selection.name == SELECTION_NAME
    assert selection.get_samples_id() == [sample_id]

    # Get the selection samples
    selection_samples_df = selection.get_dataframe()
    assert isinstance(selection_samples_df, pd.DataFrame)
    assert selection_samples_df["Image ID"].tolist() == ["image-2"]
    assert selection_samples_df["My context 1"].tolist() == ["B"]
    assert selection_samples_df["My context 2"].tolist() == [0.388]
    assert selection_samples_df["My groundtruth 1"].tolist() == [7]

    # Delete selection
    assert project.delete_selection(SELECTION_NAME)
    assert project.get_selection(SELECTION_NAME) is None
    assert project.get_selections() == []

    # Delete project
    assert debiai_instance.delete_project(project)
    assert debiai_instance.get_project(PROJECT_NAME) is None
