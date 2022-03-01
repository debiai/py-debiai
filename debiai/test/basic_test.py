# -*- coding: utf-8 -*-
"""
    DEBIAI Tests - Tests used for the debiai testsuite using unittest
    In order to execute it properly, you need to be in the same folder as this file.

    Author : Quentin Le Helloco
"""

#Import
import os
import sys
import json
# Tricks to get the import from parent directory 
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import debiai
import importlib
import test_utils as utils
import unittest
import numpy as np
import pandas as pd

# GLOBAL VARIABLES 
importlib.reload(debiai)
my_debiai = debiai.Debiai("http://localhost:3000/")

# TODO - Add an option to change this path
data_path = "../../../DEBIAI_backend/data/"

# GLOBAL DATA
"""
wine_block_structure = [
        {
            # Block N°1
            "name": "region",
            "contexts": [
                {
                    "name": "Average temperature",
                    "type": "number"
                    # No default
                },
                {
                    "name": "region type",
                    "type": "text",
                    "default": "NA"
                }
            ],
            "inputs": [],
            "groundTruth": [],
            "others": [],
        },
        {
            # Block N°2
            "name": "winemaker",
            "contexts": [
                {
                    "name": "field area",
                    "type": "number"
                    # Requiered ?
                },
                {
                    "name": "experience (years)",
                    "type": "number"
                }
            ],
        },
        {
            # Final block : sample
            "name": "wine test",
            "contexts": [
                {
                    "name": "color",
                    "type": "text"
                },
            ],
            "inputs": [
                {
                    "name": "density",
                    "type": "number"
                },
                {
                    "name": "pH",
                    "type": "number"
                },
                {
                    "name": "alcohol",
                    "type": "number"
                },
            ],
            "groundTruth": [
                {
                    "name": "quality",
                    "type": "number"
                }
            ]
        },]
wine_expected_results = [
    {
        "name": "quality guess",
        "type": "number"
    },
    {
        "name": "quality error",
        "type": "number"
    }]
wine_expected_results_add = {
    "name": "loss",
    "type": "number",
    "default": 0 }
samples = np.array([
    ["region", "Average temperature", "region type", "winemaker", "field area",
        "experience (years)", "wine test", "color", "density", "pH", "alcohol", "quality"],
    ["Alsace", 24, "Cold", 1, 6264, 24, "a_11981", 6, 0.8948, 3.51, 9.16, 5],
    ["Alsace", 24, "Cold", 1, 6264, 24, "a_11982", 6, 0.8594, 3.52, 9.19, 6],
    ["Alsace", 24, "Cold", 1, 6264, 24, "a_11983", 5, 0.1848, 3.52, 8.60, 8],
    ["Alsace", 24, "Cold", 2, 49898, 413, "b_65464", 6, 0.1689, 3.20, 9.00, 4],
    ["Alsace", 24, "Cold", 2, 49898, 413, "b_65465", 7, 0.7948, 3.10, 9.20, 5],
    ["Alsace", 24, "Cold", 2, 49898, 413, "b_65466", 8, 0.8968, 3.00, 8.16, 4],
    # ....
    ])
results = np.array([
    ["region", "winemaker", "wine test", "quality guess", "quality error"],
    ["Alsace", 1, "a_11981", 1, 5],
    ["Alsace", 1, "a_11982", 1, 8],
    ["Alsace", 1, "a_11983", 2, 8],
    ["Alsace", 2, "b_65464", 1, 2],
    ["Alsace", 2, "b_65465", 5, 5],
    ["Alsace", 2, "b_65466", 1, 4]])
results_dict = {
    "Alsace": {  # Block 1 : Region
        1: {  # Block 2 : Winemaker
            "a_11981": [1, 5],  # Block 3 : Wine test (sample) & Results
            "a_11982": [1, 8],
            "a_11983": [2, 8]
        },
        2: {
            "b_65464": [1, 2],
            "b_65465": [5, 5],
            "b_65466": [1, 4]
        }
    }}
"""
block_structure = []
expected_results = []
new_expected_results = []
samples = []
results = []
results_dist = {}
compfiles = {}

# SetUp test
class TestSetUpMethods(unittest.TestCase):
    def test_instance_project(self):
        """ Check create/delete project """
        my_debiai.create_project("TestSuite")
        
        # Check if folder exists
        check = os.path.isdir(data_path + "TestSuite")
        
        self.assertTrue(check, 'Project is missing from ' + data_path)

        result = my_debiai.delete_project_byId("TestSuite")

        check = os.path.isdir(data_path + "TestSuite")

        self.assertTrue(result, 'Error while deleting project')
        self.assertFalse(check, 'Project still in ' + data_path)

# Structure tests scenario
class TestStructureMethods(unittest.TestCase):

    # INIT
    def setUp(self):
        self.project = my_debiai.create_project("TestSuite")

    def tearDown(self):
        my_debiai.delete_project_byId("TestSuite")

    # TEST METHODS
    def test_set_blockstructure(self):
        """ Test adding blockstructure """
        self.project.set_blockstructure(block_structure)

        # Read json from file
        with open(data_path + 'TestSuite/info.json') as json_file:
            data = json.load(json_file)

        # Check if present in json
        self.assertTrue('blockLevelInfo' in data, 'Blockstructure not present in data')

        # Check if same as expected
        self.assertEqual(block_structure, data['blockLevelInfo'], 'Blockstructure not similar')
    
    def test_set_expected_results(self):
        """ Test set expected_results """
        self.project.set_expected_results(expected_results)

        # Read json from file
        with open(data_path + 'TestSuite/info.json') as json_file:
            data = json.load(json_file)

        # Check if present in json
        self.assertTrue('resultStructure' in data, 'No resultStructure in ' + data_path + 'TestSuite/info.json')

        # Check if same as expected
        self.assertEqual(expected_results, data['resultStructure'], \
            'Results_structure not same as in path: ' + data_path + 'TestSuite/info.json')

    # TO REVIEW WITH MORE INTERN TEST AND REFACTO
    def test_add_expected_results(self):
        """ Test adding to already existing expected_results """

        self.project.set_blockstructure(block_structure)
        self.project.set_expected_results(expected_results)

        # Add results - REPLACE WITH TEST LATER
        test_df = pd.DataFrame(samples[1:], columns=samples[0])
        self.project.add_samples_pd(test_df)

        model = self.project.create_model("model1")
        model.add_results_dict(results_dict)

        # Read json from file
        with open(data_path + 'TestSuite/info.json') as json_file:
            data = json.load(json_file)

        # Check if same as expected
        self.assertFalse(new_expected_results in data['resultStructure'], \
            'Already column loss in res_struct: ' + data_path + 'TestSuite/info.json')

        self.project.add_expected_result(new_expected_results)

        # Read json from file
        with open(data_path + 'TestSuite/info.json') as json_file:
            data = json.load(json_file)

        # Check if present in json
        self.assertTrue('resultStructure' in data, 'No resultStructure in ' + data_path + 'TestSuite/info.json')

        # Check if same as expected
        self.assertTrue(new_expected_results in data['resultStructure'], \
            'No new column loss in res_struct: ' + data_path + 'TestSuite/info.json')

        # Check if default added for values
        for model in os.listdir(data_path + 'TestSuite/models/'):
            result_file = data_path + 'TestSuite/models/' + model + "/results.json"
            with open(result_file) as json_file:
                data = json.load(json_file)

            for key in data:
                self.assertTrue(len(data[key]) == (len(expected_results) + 1), "Length is not " + str(len(expected_results) + 1))
                self.assertTrue(data[key][-1] == new_expected_results["default"], "Default value not applied")

    def test_remove_expected_results(self):
        """ Test removing an already existing expected_results """
        to_remove ={"name": "quality guess", "type": "number"}

        self.project.set_blockstructure(block_structure)
        self.project.set_expected_results(expected_results)

        # Add results - REPLACE WITH TEST LATER
        test_df = pd.DataFrame(samples[1:], columns=samples[0])
        self.project.add_samples_pd(test_df)

        model = self.project.create_model("model1")
        model.add_results_dict(results_dict)

        # Read json from file
        with open(data_path + 'TestSuite/info.json') as json_file:
            data = json.load(json_file)

        # Check if column is present
        self.assertTrue(to_remove in data['resultStructure'], \
            'Column already remvoed in res_struct: ' + data_path + 'TestSuite/info.json')

        self.project.remove_expected_result(to_remove["name"])

        # Read json from file
        with open(data_path + 'TestSuite/info.json') as json_file:
            data = json.load(json_file)

        # Check if results structure is present in json
        self.assertTrue('resultStructure' in data, 'No resultStructure in ' + data_path + 'TestSuite/info.json')

        # Check if column is removed
        self.assertFalse({"name": "quality guess", "type": "number"} in data['resultStructure'], \
            'Column still present in res_struct: ' + data_path + 'TestSuite/info.json')

        # Check if values as been cut from 1
        for model in os.listdir(data_path + 'TestSuite/models/'):
            result_file = data_path + 'TestSuite/models/' + model + "/results.json"
            with open(result_file) as json_file:
                data = json.load(json_file)

            for key in data:
                self.assertTrue(len(data[key]) == (len(expected_results) - 1), "Length is not " + str(len(expected_results) - 1))

# Add samples tests scenario
class TestSamplesMethods(unittest.TestCase):

    # INIT
    def setUp(self):
        self.project = my_debiai.create_project("TestSuite")
        self.project.set_blockstructure(block_structure)

    def tearDown(self):
        my_debiai.delete_project_byId("TestSuite")

    def test_add_samples_df(self):
        """ Test pushing data from dataFrame without hash """
        
        # Create dataframe
        test_df = pd.DataFrame(samples[1:], columns=samples[0])

        # Add samples
        self.project.add_samples_pd(test_df)

        # Define both path
        p2 = data_path + "TestSuite/blocks/"

        # Check hash is df
        self.assertTrue("hash" in test_df.columns, "Hash column was not added to dataFrame")
    
        for key in compfiles:
            data = compfiles[key]

            # Check if the current compfile is to be used on that test
            if "test" in data and not "samples" in data["test"]:
                continue

            # Create custom msg
            msg_T = "Samples are not equals "
            msg_F = "Samples should not be equals " 

            if data["msg"]:
                msg_T += (" - " + data["msg"])
                msg_F += (" - " + data["msg"])

            # Test Samples insertion
            if data["assert"]:
                self.assertTrue(utils.isequal_samples("Control_projects/" + data["name"] + "/blocks/", p2), msg_T)
            else:
                self.assertFalse(utils.isequal_samples("Control_projects/" + data["name"] + "/blocks/", p2), msg_T)
        
    @unittest.skip("Not implemented")
    def test_add_samples_np(self):
        """ Test pushing data from dataFrame without hash """

        # Add samples
        self.project.add_samples_np(test_df)

        # Define both path
        p2 = data_path + "TestSuite/blocks/"

        for key in compfiles:
            data = compfiles[key]

            # Check if the current compfile is to be used on that test
            if "test" in data and not "samples" in data["test"]:
                continue

            # Create custom msg
            msg_T = "Samples are not equals "
            msg_F = "Samples should not be equals " 

            if data["msg"]:
                msg_T += (" - " + data["msg"])
                msg_F += (" - " + data["msg"])

            # Test Samples insertion
            if data["assert"]:
                self.assertTrue(utils.isequal_samples("Control_projects/" + data["name"] + "/blocks/", p2), msg_T)
            else:
                self.assertFalse(utils.isequal_samples("Control_projects/" + data["name"] + "/blocks/", p2), msg_T)

        """
        self.assertTrue(utils.isequal_samples("Control_projects/basicdataset/blocks/", p2), \
            "Samples are not equals")
        self.assertFalse(utils.isequal_samples("Control_projects/basicdataset_false1/blocks/", p2), \
            "Samples shoud not be equal - Too much dir")
        self.assertFalse(utils.isequal_samples("Control_projects/basicdataset_false2/blocks/", p2), \
            "Samples shoud not be equal - Info were modified")
        """

    def test_add_model(self):
        """ Test if dir and file for empty model are well created """
        model = self.project.create_model("model1")

        self.assertTrue(os.path.isdir(data_path + "TestSuite/models/model1"), "Model dir not created")
        self.assertTrue(os.path.isfile(data_path + "TestSuite/models/model1/info.json"), "Model info file not created")

# Add results tests scenario
class TestResultMethods(unittest.TestCase):
    # INIT
    def setUp(self):
        self.project = my_debiai.create_project("TestSuite")
        self.project.set_blockstructure(block_structure)

        self.project.set_expected_results(expected_results)
        test_df = pd.DataFrame(samples[1:], columns=samples[0])
        self.project.add_samples_pd(test_df)

        self.model = self.project.create_model("model1")

    def tearDown(self):
        my_debiai.delete_project_byId("TestSuite")

    # METHODS
    @unittest.skip("Not implem test")
    def test_add_results_np(self):
        self.model.add_results_np(results)

        p2 = data_path + "TestSuite/models/" + self.model.id + "/"

        for key in compfiles:
            data = compfiles[key]

            # Check if the current compfile is to be used on that test
            if "test" in data and not "results" in data["test"]:
                continue

            # Create custom msg
            msg = data["name"]
            if data["msg"]:
                msg += " " + (data["msg"])

            if data["assert"]:
                self.assertTrue(utils.compare_info(p2 + "results.json", "Control_projects/" + data["name"] + "/models/" + self.model.id + "/results.json"), msg)
                self.assertTrue(utils.compare_info(p2 + "info.json", "Control_projects/" + data["name"] + "/models/" + self.model.id + "/info.json"), msg)
            else:
                self.assertFalse(utils.compare_info(p2 + "results.json", "Control_projects/" + data["name"] + "/models/" + self.model.id + "/results.json"), msg)
                #self.assertFalse(utils.compare_info(p2 + "info.json", "Control_projects/" + data["name"] + "/models/" + self.model.id + "/info.json"), msg)

    def test_add_results_df_nohash(self):
        df = pd.DataFrame(results[1:], columns=results[0])

        self.model.add_results_df(df)

        p2 = data_path + "TestSuite/models/" + self.model.id + "/"

        for key in compfiles:
            data = compfiles[key]

            # Check if the current compfile is to be used on that test
            if "test" in data and not "results" in data["test"]:
                continue

            # Create custom msg
            msg = data["name"]
            if data["msg"]:
                msg += " " + (data["msg"])

            if data["assert"]:
                self.assertTrue(utils.compare_info(p2 + "results.json", "Control_projects/" + data["name"] + "/models/" + self.model.id + "/results.json"), "results are not equal. " + msg)
                self.assertTrue(utils.compare_info(p2 + "info.json", "Control_projects/" + data["name"] + "/models/" + self.model.id + "/info.json"), "info are not equal. " + msg)
            else:
                self.assertFalse(utils.compare_info(p2 + "results.json", "Control_projects/" + data["name"] + "/models/" + self.model.id + "/results.json"), "results should not be equal. " + msg)
                #self.assertFalse(utils.compare_info(p2 + "info.json", "Control_projects/" + data["name"] + "/models/" + self.model.id + "/info.json"), "info should not be equal. " +  msg)

    def test_add_results_df_hash(self):
        df = pd.DataFrame(results[1:], columns=results[0])
        self.project.create_hash(df)

        self.model.add_results_df(df, use_hash=True)

        p2 = data_path + "TestSuite/models/" + self.model.id + "/"

        for key in compfiles:
            data = compfiles[key]

            # Check if the current compfile is to be used on that test
            if "test" in data and not "results" in data["test"]:
                continue

            # Create custom msg
            msg = data["name"]
            if data["msg"]:
                msg += " " + (data["msg"])

            if data["assert"]:
                self.assertTrue(utils.compare_info(p2 + "results.json", "Control_projects/" + data["name"] + "/models/" + self.model.id + "/results.json"), "results are not equal. " + msg)
                self.assertTrue(utils.compare_info(p2 + "info.json", "Control_projects/" + data["name"] + "/models/" + self.model.id + "/info.json"), "info are not equal. " + msg)
            else:
                self.assertFalse(utils.compare_info(p2 + "results.json", "Control_projects/" + data["name"] + "/models/" + self.model.id + "/results.json"), "results should not be equal. " + msg)
                #self.assertFalse(utils.compare_info(p2 + "info.json", "Control_projects/" + data["name"] + "/models/" + self.model.id + "/info.json"), "info should not be equal. " +  msg)

    def test_add_results_dict_no_hash(self):
        self.model.add_results_dict(results_dict)

        p2 = data_path + "TestSuite/models/" + self.model.id + "/"

        for key in compfiles:
            data = compfiles[key]

            # Check if the current compfile is to be used on that test
            if "test" in data and not "results" in data["test"]:
                continue

            # Create custom msg
            msg = data["name"]
            if data["msg"]:
                msg += " " + (data["msg"])

            if data["assert"]:
                self.assertTrue(utils.compare_info(p2 + "results.json", "Control_projects/" + data["name"] + "/models/" + self.model.id + "/results.json"), "results are not equal. " + msg)
                self.assertTrue(utils.compare_info(p2 + "info.json", "Control_projects/" + data["name"] + "/models/" + self.model.id + "/info.json"), "info are not equal. " + msg)
            else:
                self.assertFalse(utils.compare_info(p2 + "results.json", "Control_projects/" + data["name"] + "/models/" + self.model.id + "/results.json"), "results should not be equal. " + msg)
                #self.assertFalse(utils.compare_info(p2 + "info.json", "Control_projects/" + data["name"] + "/models/" + self.model.id + "/info.json"), "info should not be equal. " +  msg)
    
    def test_add_results_dict_hash(self):
        df = pd.DataFrame(results[1:], columns=results[0])
        self.project.create_hash(df)

        # Create hash dictionnary
        results_ = {}

        for i in range(len(df)):
            res = []
            for key in expected_results:
                if key["type"] == "number":
                    res.append(int(df.iloc[i][key["name"]]))
                else:
                    res.append(df.iloc[i][key["name"]])
            
            results_[df.iloc[i]["hash"]] = res

        self.model.add_results_hash(results_)

        p2 = data_path + "TestSuite/models/" + self.model.id + "/"

        for key in compfiles:
            data = compfiles[key]

            # Check if the current compfile is to be used on that test
            if "test" in data and not "results" in data["test"]:
                continue

            # Create custom msg
            msg = data["name"]
            if data["msg"]:
                msg += " " + (data["msg"])

            if data["assert"]:
                self.assertTrue(utils.compare_info(p2 + "results.json", "Control_projects/" + data["name"] + "/models/" + self.model.id + "/results.json"), "results are not equal. " + msg)
                self.assertTrue(utils.compare_info(p2 + "info.json", "Control_projects/" + data["name"] + "/models/" + self.model.id + "/info.json"), "info are not equal. " + msg)
            else:
                self.assertFalse(utils.compare_info(p2 + "results.json", "Control_projects/" + data["name"] + "/models/" + self.model.id + "/results.json"), "results should not be equal. " + msg)
                #self.assertFalse(utils.compare_info(p2 + "info.json", "Control_projects/" + data["name"] + "/models/" + self.model.id + "/info.json"), "info should not be equal. " +  msg)
        

file_path = "tests_inputs/"
inputs = ["wine_small_data/"]

if __name__ == '__main__':
    inputs_ = map(lambda x: file_path + x, inputs)

    for data in inputs_:
        print("Testing " + data)
        # Change local variable to use tests
        block_structure = utils.get_raw_json(data + "blockstructure.json")
        expected_results = utils.get_raw_json(data + "expected_results.json")
        new_expected_results = utils.get_raw_json(data + "new_expected_results.json")
        results_dict = utils.get_raw_json(data + "results_dict.json")
        compfiles = utils.get_raw_json(data + "compfiles.json")

        samples = utils.get_np_from_csv(data + "samples.csv")
        results = utils.get_np_from_csv(data + "results.csv")

        """
        print(block_structure)
        print(expected_results)
        print(new_expected_results)
        print(results_dict)
        print(samples)
        print(results)
        """

        unittest.main()
        
# =========TODO==========
# Use mock to get value before they'r sent to backend and check ?
# Check add new samples with same hash don't push them into backend

# === WORKING ONE ===
# Works with unittest lib but no color at prompt - trying to change for pytest soon
# Need to add another way to select which project to compare with our testsuite : DONE (but not clean)

#=== DONE ===:
# Check add new expected_results to already created one: DONE
# Check remove expected results: DONE
# Check create model
# Check add results to model as np: DONE
# Check add results to model as pd without hash: DONE
# Check add results to model as pd with hash: DONE
# Check add results to model as dict: DONE
# Check add results to model as dict with hash: DONE
# Make easy to add new case to test (others projects struct, samples and results) from dic or file : DONE