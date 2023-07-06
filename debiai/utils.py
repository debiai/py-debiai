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

# GLOBAL VARIABLES
logging.basicConfig(filename="debiai.log", filemode="w", level=logging.INFO)

PYTHON_DATA_PROVIDER_ID = "Python module Data Provider"

CONNECTION_ERROR_MESSAGE = "Unable to connect to the DebiAI backend at the url : "
APPLICATION_ERROR_MESSAGE = "Something went wrong the DebiAI, is your module version the same as the application ?"


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
        ret = requests.get(debiai_url + "version")

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
    Add blocklevel to a project block strucure
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

    except json.decoder.JSONDecodeError as e:
        raise ValueError("internal server error")


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
        raise ValueError("Internal server error while adding the datatree")
    return True


def get_project_samples(debiai_url, project_id, depth=0):
    """Return a sample tree (JSON)"""
    r = requests.request(
        "GET",
        url=project_url(debiai_url, project_id) + "/blocks?depth=" + str(depth),
    )
    logging.info("get_project_samples response: " + str(r.status_code))
    return json.loads(r.text)


def get_samples_from_selection(debiai_url, project_id, selectionId, depth=0):
    """Return a sample tree (JSON)"""
    r = requests.request(
        "GET",
        url=project_url(debiai_url, project_id)
        + "/blocks/"
        + selectionId
        + "?depth="
        + str(depth),
    )
    logging.info("get_samples_from_selection response: " + str(r.status_code))
    return json.loads(r.text)


def get_project_training_samples(debiai_url, project_id, start, size):
    """Return a sample inputs and gdt array ready to be processed"""
    r = requests.request(
        "GET",
        url=project_url(debiai_url, project_id)
        + "/trainingSamples?start="
        + str(start)
        + "&size="
        + str(size),
    )
    logging.info("get_project_training_samples response: " + str(r.status_code))
    return json.loads(r.text)


def get_training_samples_from_selection(
    debiai_url, project_id, selectionId, start, size
):
    """Return a sample inputs and gdt array ready to be processed"""
    r = requests.request(
        "GET",
        url=project_url(debiai_url, project_id)
        + "/trainingSamples?selectionId="
        + selectionId
        + "&start="
        + str(start)
        + "&size="
        + str(size),
    )
    logging.info("get_training_samples_from_selection response: " + str(r.status_code))
    return json.loads(r.text)


# Hash
def check_hash_exist(debiai_url, project_id, hash_list):
    """Check with backend if hashes exists"""
    data = {"hash_list": hash_list}

    try:
        r = requests.request(
            "POST",
            url=project_url(debiai_url, project_id) + "/check_hash",
            json=data,
        )
        if r.status_code != 200:
            raise ValueError("check_hash_exist : " + json.loads(r.text))
        return json.loads(r.text)
    except json.decoder.JSONDecodeError as e:
        raise ValueError("internal server error")


def post_results_hash(debiai_url, project_id, modelId, results: dict):
    """Add to an existing project model some results from a hash tree"""
    data = {
        "results": results,
    }
    try:
        r = requests.request(
            "POST",
            url=project_url(debiai_url, project_id)
            + "/models/"
            + modelId
            + "/resultsHash",
            json=data,
        )

        if r.status_code != 200:
            raise ValueError("post_model_results_dict : " + json.loads(r.text))
        return True
    except json.decoder.JSONDecodeError as e:
        raise ValueError("internal server error")
