import numpy as np
import pandas as pd
from debiai.debiai import Debiai
from debiai.config import get_config

config = get_config()
debiai_instance = Debiai(config.debiai_app_url)

projects = debiai_instance.get_projects()
for p in projects:
    debiai_instance.delete_project(p)

PROJECT_NAME = "test_samples"

block_structure = [
    {
        "name": "Image ID",
        "contexts": [
            {"name": "My context 1", "type": "text"},
            {"name": "My context 2", "type": "number"},
        ],
        "groundTruth": [{"name": "My groundtruth 1", "type": "number"}],
    }
]


expected_results = [
    {"name": "Model result", "type": "number"},
    {"name": "Model confidence", "type": "number"},
    {"name": "Model error", "type": "text"},
]


def create_empty_project():
    if debiai_instance.get_project(PROJECT_NAME) is not None:
        debiai_instance.delete_project_byId(PROJECT_NAME)

    project = debiai_instance.create_project(PROJECT_NAME)
    project.set_blockstructure(block_structure)
    project.set_expected_results(expected_results)
    return project


def test_samples_df():
    project = create_empty_project()
    samples_df = pd.DataFrame(
        {
            "Image ID": ["image-1", "image-2", "image-3"],
            "My context 1": ["A", "B", "C"],
            "My context 2": [0.28, 0.388, 0.5],
            "My groundtruth 1": [8, 7, 19],
        }
    )
    assert project.add_samples_pd(samples_df)

    model_1 = project.create_model("Model 1")
    results_df = pd.DataFrame(
        {
            "Image ID": ["image-1", "image-2", "image-3"],
            "Model result": [5, 7, 19],
            "Model confidence": [0.22, 0.8, 0.9],
            "Model error": ["yes", "no", "no"],
        }
    )
    assert model_1.add_results_df(results_df)
    debiai_instance.delete_project(project)


def test_samples_np():
    project = create_empty_project()
    samples_np = np.array(
        [
            ["Image ID", "My context 1", "My context 2", "My groundtruth 1"],
            ["image-1", "D", 0.98, 1],
            ["image-2", "E", 0.97, 3],
            ["image-3", "F", 0.8, 2],
        ]
    )
    assert project.add_samples(samples_np)

    model_2 = project.create_model("Model 2")
    results_np = np.array(
        [
            ["Image ID", "Model result", "Model confidence", "Model error"],
            ["image-1", 3, 0.98, "yes"],
            ["image-2", 7, 0.97, "no"],
            ["image-3", 10, 0.8, "yes"],
        ]
    )
    assert model_2.add_results_np(results_np)
    debiai_instance.delete_project(project)


def test_samples_multi_levels():
    multi_block_structure = [
        {"name": "Dataset ID"},
        {
            "name": "Image ID",
            "contexts": [
                {"name": "Context", "type": "text"},
            ],
            "groundTruth": [{"name": "GDT", "type": "number"}],
        },
        {"name": "Obst ID"},
    ]

    if debiai_instance.get_project("test Multi Levels") is not None:
        debiai_instance.delete_project_byId("test Multi Levels")

    project = debiai_instance.create_project("test Multi Levels")
    project.set_blockstructure(multi_block_structure)

    samples = np.array(
        [
            ["Dataset ID", "Image ID", "Context", "GDT", "Obst ID"],
            ["A", "image-1", "D", 1, 3000],
            ["A", "image-2", "E", 3, 2000],
            ["A", "image-2", "F", 2, 1000],
            ["A", "image-2", "F", 2, 1000],
        ]
    )

    assert project.add_samples(samples)
    debiai_instance.delete_project(project)
