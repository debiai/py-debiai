import numpy as np
import pandas as pd
from debiai.debiai import Debiai
from debiai.debiai_project import Debiai_project
from debiai.config import get_config

config = get_config()
debiai_instance = Debiai(config.debiai_app_url)

project_name = "test_project_samples"
projects = debiai_instance.get_projects()
for project in projects:
    debiai_instance.delete_project(project)

block_structure = [
    {
        "name": "Image ID",
        "contexts": [
            {"name": "My context 1",     "type": "text"},
            {"name": "My context 2",     "type": "number"}
        ],
        "groundTruth": [
            {"name": "My groundtruth 1", "type": "number"}
        ]
    }
]


def create_empty_project():
    if debiai_instance.get_project(project_name) is not None:
        debiai_instance.delete_project_byId(project_name)

    project = debiai_instance.create_project(project_name)
    project.set_blockstructure(block_structure)
    return project


def test_samples_df():
    project = create_empty_project()
    samples_df = pd.DataFrame({
        "Image ID":         ["image-1", "image-2", "image-3"],
        "My context 1":     ["A", "B", "C"],
        "My context 2":     [0.28, 0.388, 0.5],
        "My groundtruth 1": [8, 7, 19],
    })
    assert project.add_samples_pd(samples_df)


def test_samples_np():
    project = create_empty_project()
    samples_np = np.array([
        ["Image ID", "My context 1", "My context 2", "My groundtruth 1"],
        ["image-1", "D", 0.98, 1],
        ["image-2", "E", 0.97, 3],
        ["image-3", "F", 0.8, 2]
    ])
    assert project.add_samples(samples_np)
