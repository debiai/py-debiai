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
logging.basicConfig(filename='debiai.log', filemode='w', level=logging.INFO)


# Progress bar
class progress_bar():
    BAR_SIZE = 40

    def __init__(self, name: str, size: int, para: str = ""):
        self.name = name
        self.size = size
        self.para = para

        self.start = time.time()
        self.update(0)

    def update(self, current_progression: int):
        percent = 100.0 * current_progression / self.size
        sys.stdout.write('\r')
        sys.stdout.write(self.name + " : [{:{}}] {:>3}%"
                         .format('=' * int(percent / (100.0 / self.BAR_SIZE)),
                                 self.BAR_SIZE, int(percent)))
        sys.stdout.write(" " + str(current_progression) + "/" + str(self.size))
        sys.stdout.write(" " + str(self.para))
        sys.stdout.write(" " + str(math.floor(time.time() - self.start)) + "s")
        sys.stdout.flush()

        if percent == 100:
            print('')


# Dates
def timestamp_to_date(timestamp):
    ''' Convert timestamp to date '''
    return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp / 1000)))

# Connection


def check_back(backend_url):
    ''' Check the connection with backend'''
    try:
        ret = requests.get(backend_url + "version")

        if "Online" not in ret.text:
            try:
                ret2 = requests.get(backend_url)
                if "Online" not in ret2.text:
                    raise ConnectionError(
                        "An application is running on the url : " + backend_url + " but this is not DEBIAI")
                logging.info("DEBIAI Server is up !\n")
                return True
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.RequestException
            ):
                logging.warning("Backend is down")
                raise ConnectionError(
                    "Unable to connect to the DEBIAI backend at the url : " + backend_url)

        logging.info("DEBIAI Server is up !\n")
        return True
    except (
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        requests.exceptions.RequestException
    ):
        logging.warning("Backend is down")
        raise ConnectionError(
            "Unable to connect to the DEBIAI backend at the url : " + backend_url)


# Projects
def get_projects(backend_url):
    ''' Return projects list as JSON '''
    try:
        r = requests.request("GET", backend_url +
                             "projects", headers={}, data={})
        logging.info("Get_projects response: " + str(r.status_code))
        logging.info(r.text)
        return json.loads(r.text)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def get_project(backend_url, id):
    ''' Return project (JSON) from id '''
    try:
        r = requests.request("GET", backend_url + "projects/" + id)
        logging.info("Get_project response: " + str(r.status_code))
        logging.info(r.text)
        return json.loads(r.text)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def post_project(backend_url, name):
    ''' Post new project and return project id '''
    data = {'projectName': name, 'blockLevelInfo': [{'name': 'file'}]}

    try:
        r = requests.request("POST", url=backend_url + "projects", json=data)
        if r.status_code != 200:
            raise ValueError(json.loads(r.text))
        info = json.loads(r.text)
        return info["id"]
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def delete_project(backend_url, id):
    ''' Delete project from id '''
    try:
        r = requests.request("DELETE", url=backend_url +
                             "projects/" + id, headers={}, json={})
        if r.status_code != 200:
            raise ValueError(json.loads(r.text))

        logging.info("Deleted project: " + id)
        return True
    except requests.exceptions.RequestException:
        return False


# Block struture
def post_expected_results(backend_url, id, expected_results):
    ''' set the expected_results to a project'''
    try:
        r = requests.request("POST", url=backend_url +
                             "projects/" + id + "/resultsStructure", json=expected_results)
        if r.status_code != 200:
            raise ValueError(json.loads(r.text))
        return json.loads(r.content)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def add_blocklevel(backend_url, id, blocklevel):
    '''
    Add blocklevel to a project block strucure
    Not used very much, should be removed
    TODO - Check if blocklevel already exists
    '''
    try:
        r = requests.request("POST", url=backend_url +
                             "projects/" + id + "/blocklevels", json=blocklevel)
        logging.info("Add block response :" +
                     str(r.status_code) + "-" + str(r.text))
        if r.status_code != 200:
            raise ValueError(json.loads(r.text))
        logging.info("Added blocklevel to project " + id)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def post_add_expected_results(backend_url, id, expected_result):
    ''' Add expected_result to a project'''
    try:
        r = requests.request("POST", url=backend_url +
                             "projects/" + id + "/expectedResult", json=expected_result)
        if r.status_code != 200:
            raise ValueError(json.loads(r.text))
        return json.loads(r.content)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def remove_expected_results(backend_url, id, expected_result):
    ''' remove expected_result from a project'''
    obj = {"value": expected_result}

    try:
        r = requests.request("POST", url=backend_url +
                             "projects/" + id + "/del_expectedResult", json=obj)
        if r.status_code != 200:
            raise ValueError(json.loads(r.text))
        return json.loads(r.content)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


# Selections
def get_selections(backend_url, project_id):
    ''' Return a project get_selections as JSON '''
    try:
        r = requests.request("GET", backend_url +
                             "projects/" + project_id + "/selections")
        logging.info("get_requests response: " + str(r.status_code))
        logging.info(r.text)
        return json.loads(r.text)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


# Models
def post_model(backend_url, project_id, name, metadata):
    ''' Add to an existing project a tree of samples '''
    data = {'name': name, 'metadata': metadata}

    try:
        r = requests.request("POST", url=backend_url +
                             "projects/" + project_id + "/models", json=data)

        if r.status_code != 200:
            raise ValueError("post_model : " + json.loads(r.text))
        return True
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def post_model_results_dict(backend_url, project_id, modelId, results: dict, expected_results_order: List[str]):
    ''' Add to an existing project model some results from a tree dict  '''
    data = {
        "results": results,
        "expected_results_order": expected_results_order
    }
    try:
        r = requests.request("POST", url=backend_url +
                             "projects/" + project_id +
                             "/models/" + modelId +
                             "/resultsDict", json=data)

        if r.status_code != 200:
            raise ValueError("post_model_results_dict : " + json.loads(r.text))
        return True
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    except json.decoder.JSONDecodeError as e:
        raise ValueError("internal server error")


def delete_model(backend_url, project_id, model_id):
    ''' Delete a model from a project '''
    try:
        r = requests.request("DELETE", url=backend_url +
                             "projects/" + project_id +
                             "/models/" + model_id)
        if r.status_code != 200:
            raise ValueError(json.loads(r.text))
        logging.info("Deleted model: " + model_id)
        return True
    except requests.exceptions.RequestException:
        return False

# Tags


def get_tags(backend_url, project_id):
    ''' Return a tag as JSON form id '''
    try:
        r = requests.request("GET", url=backend_url +
                             "projects/" + project_id + "/tags")
        logging.info("get_tags response: " + str(r.status_code))
        logging.info(r.text)
        return json.loads(r.text)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def get_tag(backend_url, project_id, tag_id):
    ''' Return a tag as JSON form id '''
    try:
        r = requests.request("GET", url=backend_url +
                             "projects/" + project_id + "/tags/" + str(tag_id))
        logging.info("get_tag response: " + str(r.status_code))
        logging.info(r.text)
        return json.loads(r.text)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def get_samples_from_tag(backend_url, project_id, tag_id, tag_value):
    ''' Return a sample tree (JSON) '''
    try:
        r = requests.request("GET", backend_url + "projects/" +
                             project_id + "/tags/" + str(tag_id) + "/samples/" + str(tag_value))
        logging.info("get_samples_from_tag response: " + str(r.status_code))
        return json.loads(r.text)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


# Sample tree
def post_add_tree(backend_url, name, tree):
    '''
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
    '''

    data = {'blockTree': tree}

    try:
        r = requests.request("POST", url=backend_url +
                             "projects/" + name + "/blocks", json=data)
        if r.status_code == 201:
            print('No block added')
        elif r.status_code != 200:
            raise ValueError("Internal server error while adding the datatree")
        return True
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def get_project_samples(backend_url, project_id, depth=0):
    ''' Return a sample tree (JSON) '''
    try:
        r = requests.request("GET", backend_url + "projects/" +
                             project_id + "/blocks?depth=" + str(depth))
        logging.info("get_project_samples response: " + str(r.status_code))
        return json.loads(r.text)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def get_samples_from_selection(backend_url, project_id, selectionId, depth=0):
    ''' Return a sample tree (JSON) '''
    try:
        r = requests.request("GET", backend_url + "projects/" +
                             project_id + "/blocks/" + selectionId + "?depth=" + str(depth))
        logging.info("get_samples_from_selection response: " +
                     str(r.status_code))
        return json.loads(r.text)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def get_project_training_samples(backend_url, project_id, start, size):
    ''' Return a sample inputs and gdt array ready to be processed '''
    try:
        r = requests.request(
            "GET", backend_url + "projects/" + project_id + "/trainingSamples?start=" + str(start) + "&size=" + str(size))
        logging.info("get_project_training_samples response: " +
                     str(r.status_code))
        return json.loads(r.text)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def get_training_samples_from_selection(backend_url, project_id, selectionId, start, size):
    ''' Return a sample inputs and gdt array ready to be processed '''
    try:
        r = requests.request(
            "GET", backend_url + "projects/" + project_id + "/trainingSamples?selectionId=" + selectionId + "&start=" + str(start) + "&size=" + str(size))
        logging.info("get_training_samples_from_selection response: " +
                     str(r.status_code))
        return json.loads(r.text)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


# Hash
def check_hash_exist(backend_url, project_id, hash_list):
    """ Check with backend if hashes exists """
    data = {"hash_list": hash_list}

    try:
        r = requests.request("POST", url=backend_url + "projects/" +
                             project_id + "/check_hash", json=data)
        if r.status_code != 200:
            raise ValueError("check_hash_exist : " + json.loads(r.text))
        return json.loads(r.text)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    except json.decoder.JSONDecodeError as e:
        raise ValueError("internal server error")


def post_results_hash(backend_url, project_id, modelId, results: dict):
    ''' Add to an existing project model some results from a hash tree  '''
    data = {
        "results": results,
    }
    try:
        r = requests.request("POST", url=backend_url +
                             "projects/" + project_id +
                             "/models/" + modelId +
                             "/resultsHash", json=data)

        if r.status_code != 200:
            raise ValueError("post_model_results_dict : " + json.loads(r.text))
        return True
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    except json.decoder.JSONDecodeError as e:
        raise ValueError("internal server error")
