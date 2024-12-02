# -*- coding: utf-8 -*-
"""
    Utils : request manager
"""
# IMPORT
import sys
import requests
import logging
import json
from typing import List
import time
import math
import pandas as pd

# GLOBAL VARIABLES
logging.basicConfig(filename="debiai.log", filemode="w", level=logging.INFO)

PYTHON_DATA_PROVIDER_ID = "Python module Data Provider"

CONNECTION_ERROR_MESSAGE = "Unable to connect to the DebiAI backend at the url : "


# Progress bar
class progress_bar:
    BAR_SIZE = 40

    def __init__(self, name: str, size: int, para: str = ""):
        self.name = name
        self.size = size
        self.para = para

        self.start = time.time()
        self.update(0)

    def update(self, current_progression: int):
        if self.size == 0:
            sys.stdout.write(self.name + " : Progression bar size is 0")
            return

        percent = 100.0 * current_progression / self.size
        sys.stdout.write("\r")
        sys.stdout.write(
            self.name
            + " : [{:{}}] {:>3}%".format(
                "=" * int(percent / (100.0 / self.BAR_SIZE)),
                self.BAR_SIZE,
                int(percent),
            )
        )
        sys.stdout.write(" " + str(current_progression) + "/" + str(self.size))
        sys.stdout.write(" " + str(self.para))
        sys.stdout.write(" " + str(math.floor(time.time() - self.start)) + "s")
        sys.stdout.flush()

        if percent == 100:
            print("")


# Dates
def timestamp_to_date(timestamp):
    """Convert timestamp to date"""
    return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp / 1000)))


# Connection
def check_back(debiai_url):
    """Check the connection with backend"""
    try:
        ret = requests.get(debiai_url + "/version")

        if "Online" not in ret.text:
            try:
                ret2 = requests.get(debiai_url)
                if "Online" not in ret2.text:
                    raise ConnectionError(
                        "An application is running on the url : "
                        + debiai_url
                        + " but this is not DebiAI"
                    )
                logging.info("DebiAI Server is up !\n")
                return True
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.RequestException,
            ):
                logging.warning("Backend is down")
                raise ConnectionError(CONNECTION_ERROR_MESSAGE + debiai_url)

        logging.info("DebiAI Server is up !\n")
        return True
    except (
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        requests.exceptions.RequestException,
    ):
        logging.warning("Backend is down")
        raise ConnectionError(
            "Unable to connect to the DebiAI backend at the url : " + debiai_url
        )


def projects_url(debiai_url):
    return debiai_url + "/data-providers/" + PYTHON_DATA_PROVIDER_ID + "/projects"


def project_url(debiai_url, project_id):
    return projects_url(debiai_url) + "/" + project_id


# Projects
def get_projects(debiai_url):
    """Return projects list as JSON"""
    r = requests.request("GET", projects_url(debiai_url))
    logging.info("Get_projects response: " + str(r.status_code))
    logging.info(r.text)
    return json.loads(r.text)


def get_project(debiai_url, id):
    """Return project (JSON) from id"""
    r = requests.request("GET", project_url(debiai_url, id))
    logging.info("Get_project response: " + str(r.status_code))
    logging.info(r.text)
    if r.status_code == 404:
        return None
    return json.loads(r.text)


def post_project(debiai_url, name):
    """Post new project and return project id"""
    data = {"projectName": name, "blockLevelInfo": [{"name": "file"}]}
    r = requests.request("POST", url=debiai_url + "/projects", json=data)
    if r.status_code != 200:
        raise ValueError(json.loads(r.text))
    info = json.loads(r.text)
    return info["id"]


def delete_project(debiai_url, id):
    """Delete project from id"""
    try:
        r = requests.request("DELETE", url=project_url(debiai_url, id))
        if r.status_code != 200:
            raise ValueError(json.loads(r.text))

        logging.info("Deleted project: " + id)
        return True
    except requests.exceptions.RequestException:
        return False


# Block structure
def post_expected_results(debiai_url, id, expected_results):
    """set the expected_results to a project"""
    r = requests.request(
        "POST",
        url=project_url(debiai_url, id) + "/resultsStructure",
        json=expected_results,
    )
    if r.status_code != 200:
        raise ValueError(json.loads(r.text))
    return json.loads(r.content)


def add_blocklevel(debiai_url, id, blocklevel):
    """
    Add blocklevel to a project block structure
    Not used very much, should be removed
    TODO - Check if blocklevel already exists
    """
    r = requests.request(
        "POST",
        url=project_url(debiai_url, id) + "/blocklevels",
        json=blocklevel,
    )
    logging.info("Add block response :" + str(r.status_code) + "-" + str(r.text))
    if r.status_code != 200:
        raise ValueError(json.loads(r.text))
    logging.info("Added blocklevel to project " + id)


def post_add_expected_results(debiai_url, id, expected_result):
    """Add expected_result to a project"""
    r = requests.request(
        "POST",
        url=project_url(debiai_url, id) + "/expectedResult",
        json=expected_result,
    )
    if r.status_code != 200:
        raise ValueError(json.loads(r.text))
    return json.loads(r.content)


def remove_expected_results(debiai_url, id, expected_result):
    """remove expected_result from a project"""
    obj = {"value": expected_result}

    r = requests.request(
        "POST",
        url=project_url(debiai_url, id) + "/del_expectedResult",
        json=obj,
    )
    if r.status_code != 200:
        raise ValueError(json.loads(r.text))
    return json.loads(r.content)


# Selections
def get_selections(debiai_url, id):
    """Return a project get_selections as JSON"""
    r = requests.request("GET", project_url(debiai_url, id) + "/selections")
    logging.info("get_requests response: " + str(r.status_code))
    logging.info(r.text)
    return json.loads(r.text)


def post_selection(debiai_url, id, name, samples_id) -> dict:
    """Post new selection and return selection id"""
    data = {"selectionName": name, "sampleHashList": samples_id}
    r = requests.request(
        "POST",
        url=project_url(debiai_url, id) + "/selections",
        json=data,
    )
    if r.status_code != 200:
        raise ValueError(json.loads(r.text))
    info = json.loads(r.text)
    return info


def get_samples_id_from_selection(debiai_url, project_id, selection_id) -> List[str]:
    """Return a list of samples id from a selection"""
    r = requests.request(
        "GET",
        url=project_url(debiai_url, project_id) + "/selections/" + selection_id,
    )
    logging.info("get_samples_id_from_selection response: " + str(r.status_code))
    return json.loads(r.text)


def delete_selection(debiai_url, project_id, selection_id):
    """Delete a selection from a project"""
    try:
        r = requests.request(
            "DELETE",
            url=project_url(debiai_url, project_id) + "/selections/" + selection_id,
        )
        if r.status_code != 200:
            raise ValueError(json.loads(r.text))
        logging.info("Deleted selection: " + selection_id)
        return True
    except requests.exceptions.RequestException:
        return False


# Models
def post_model(debiai_url, id, name, metadata):
    """Add to an existing project a tree of samples"""
    data = {"name": name, "metadata": metadata}

    r = requests.request("POST", url=project_url(debiai_url, id) + "/models", json=data)

    if r.status_code == 409:
        print("Warning : The model " + name + " already exists")
        return 409
    if r.status_code != 200:
        raise ValueError("post_model : " + json.loads(r.text))
    return True


def post_model_results_dict(
    debiai_url, project_id, modelId, results: dict, expected_results_order: List[str]
):
    """Add to an existing project model some results from a tree dict"""
    data = {"results": results, "expected_results_order": expected_results_order}
    try:
        r = requests.request(
            "POST",
            url=project_url(debiai_url, project_id)
            + "/models/"
            + modelId
            + "/resultsDict",
            json=data,
        )

        if r.status_code != 200:
            raise ValueError("post_model_results_dict : " + json.loads(r.text))
        return True

    except json.decoder.JSONDecodeError:
        raise ValueError("The server returned an unexpected response")


def delete_model(debiai_url, project_id, model_id):
    """Delete a model from a project"""
    try:
        r = requests.request(
            "DELETE",
            url=project_url(debiai_url, project_id) + "/models/" + model_id,
        )
        if r.status_code != 200:
            raise ValueError(json.loads(r.text))
        logging.info("Deleted model: " + model_id)
        return True
    except requests.exceptions.RequestException:
        return False


# Samples
def get_project_samples(debiai_url, project_id, block_structure) -> pd.DataFrame:
    DATA_TYPES = ["groundTruth", "contexts", "inputs", "others"]

    # Get the project number of samples
    project = get_project(debiai_url, project_id)
    project_nbSamples = project["nbSamples"]

    NB_SAMPLES_PER_REQUEST = 4000
    # Generate a random request ID
    request_id = str(int(time.time() * 1000000))

    # Get the list of samples
    dataframe = pd.DataFrame()
    for i in range(0, project_nbSamples, NB_SAMPLES_PER_REQUEST):
        r = requests.request(
            "POST",
            url=project_url(debiai_url, project_id) + "/dataIdList",
            json={
                "from": i,
                "to": i + NB_SAMPLES_PER_REQUEST - 1,
                "analysis": {
                    "id": request_id,
                    "start": i == 0,
                    "end": i + NB_SAMPLES_PER_REQUEST >= project_nbSamples,
                },
            },
        )
        sample_id_list = json.loads(r.text)

        # Download the samples
        r = requests.request(
            "POST",
            url=project_url(debiai_url, project_id) + "/blocksFromSampleIds",
            json={
                "sampleIds": sample_id_list,
                "analysis": {
                    "id": request_id,
                    "start": i == 0,
                    "end": i + NB_SAMPLES_PER_REQUEST >= project_nbSamples,
                },
            },
        )

        # Samples returned are in a {
        #  "{sample_id}": [sample_data],
        #  "{sample_id}": [sample_data],
        #  "{sample_id}": [sample_data],
        # } Format

        # Map each values to the block structure
        # Goal format: a DataFrame
        samples_data = json.loads(r.text)["data"]
        sample_dicts = []
        for sample_id in samples_data:
            sample = samples_data[sample_id]
            sample_dict = {"sample_id": sample_id}

            col_index = 0
            for block in block_structure:
                sample_dict[block["name"]] = sample[col_index]
                col_index += 1

                for block_category in DATA_TYPES:
                    if block_category not in block:
                        continue

                    for column in block[block_category]:
                        sample_dict[column["name"]] = sample[col_index]
                        col_index += 1
            sample_dicts.append(sample_dict)

        new_dataframe = pd.DataFrame(sample_dicts)
        dataframe = pd.concat([dataframe, new_dataframe])

    # Sort the dataframe rows by the blocks names
    block_names = []
    for block in block_structure:
        block_names.append(block["name"])

    dataframe = dataframe.sort_values(by=block_names)

    return dataframe


def get_selection_samples(
    debiai_url, project_id, selection_id, block_structure
) -> pd.DataFrame:
    DATA_TYPES = ["groundTruth", "contexts", "inputs", "others"]
    NB_SAMPLES_PER_REQUEST = 4000

    # Get the selection samples
    samples = get_samples_id_from_selection(debiai_url, project_id, selection_id)

    # Get the samples
    dataframe = pd.DataFrame()
    for i in range(0, len(samples), NB_SAMPLES_PER_REQUEST):
        # Download the samples
        r = requests.request(
            "POST",
            url=project_url(debiai_url, project_id) + "/blocksFromSampleIds",
            json={"sampleIds": samples[i : i + NB_SAMPLES_PER_REQUEST]},  # noqa
        )

        # Samples returned are in a {
        #  "{sample_id}": [sample_data],
        #  "{sample_id}": [sample_data],
        #  "{sample_id}": [sample_data],
        # } Format

        # Map each values to the block structure
        # Goal format: a DataFrame
        samples_data = json.loads(r.text)["data"]
        sample_dicts = []
        for sample_id in samples_data:
            sample = samples_data[sample_id]
            sample_dict = {"sample_id": sample_id}

            col_index = 0
            for block in block_structure:
                sample_dict[block["name"]] = sample[col_index]
                col_index += 1

                for block_category in DATA_TYPES:
                    if block_category not in block:
                        continue

                    for column in block[block_category]:
                        sample_dict[column["name"]] = sample[col_index]
                        col_index += 1
            sample_dicts.append(sample_dict)

        new_dataframe = pd.DataFrame(sample_dicts)
        dataframe = pd.concat([dataframe, new_dataframe])

    # Sort the dataframe rows by the blocks names
    block_names = []
    for block in block_structure:
        block_names.append(block["name"])

    dataframe = dataframe.sort_values(by=block_names)

    return dataframe


# Tags
def get_tags(debiai_url, project_id):
    """Return a tag as JSON form id"""
    r = requests.request("GET", url=project_url(debiai_url, project_id) + "/tags")
    logging.info("get_tags response: " + str(r.status_code))
    logging.info(r.text)
    return json.loads(r.text)


def get_tag(debiai_url, project_id, tag_id):
    """Return a tag as JSON form id"""
    r = requests.request(
        "GET",
        url=project_url(debiai_url, project_id) + "/tags/" + str(tag_id),
    )
    logging.info("get_tag response: " + str(r.status_code))
    logging.info(r.text)
    return json.loads(r.text)


def get_samples_from_tag(debiai_url, project_id, tag_id, tag_value):
    """Return a sample tree (JSON)"""
    r = requests.request(
        "GET",
        url=project_url(debiai_url, project_id)
        + "/tags/"
        + str(tag_id)
        + "/samples/"
        + str(tag_value),
    )
    logging.info("get_samples_from_tag response: " + str(r.status_code))
    return json.loads(r.text)


# Sample tree
def post_add_tree(debiai_url, project_id, tree):
    """
    Add to an existing project a tree of samples

    The expected tree format :
    [
        {
            "name": "b1",
            "contexts": [..],
            "inputs": [...],
            "groundTruth": [...],
            "others: [...]"
            "childrenInfoList": [
                {
                    "name": "b1-1",
                    "contexts": [...],
                    "inputs": [...],
                    "groundTruth": [...],
                    "others: [...]"
                    "childrenInfoList": [...]
                },
                ...
            ]
        },
        ...
    ]
    """

    data = {"blockTree": tree}

    r = requests.request(
        "POST",
        url=project_url(debiai_url, project_id) + "/blocks",
        json=data,
    )
    if r.status_code == 201:
        print("No block added")
    elif r.status_code != 200:
        raise ValueError("Internal server error while adding the data tree")
    return True
