from debiai import debiai
import numpy as np
import pandas as pd

# In this tutorial, we will show how to use the debiai library with a simple example.
# - Creation  of a DEBIAI project
# - Insertion of data from a numpy array
# - Insertion of data from a dictionary
# - Insertion of data from a dataframe
# - Insertion of model results from a numpy array
# - Insertion of model results from a dictionary
# - Insertion of model results from a dataframe

DEBIAI_URL = "http://localhost:3000/"
DEBIAI_PROJECT_NAME = "Wine quality v0"

# Initialisation

my_debiai = debiai.Debiai(DEBIAI_URL)

# Creating and selecting project
debiai_project = my_debiai.get_project(DEBIAI_PROJECT_NAME)

if debiai_project:
    # Deleting the project if already existing
    my_debiai.delete_project_byId(DEBIAI_PROJECT_NAME)

debiai_project = my_debiai.create_project(DEBIAI_PROJECT_NAME)

# Creating the project block structure
# Based on the wine quality dataset : http://archive.ics.uci.edu/ml/datasets/Wine+Quality

wine_block_structure = [
    {
        # Block N°1
        "name": "region",
        "contexts": [
            {"name": "Average temperature", "type": "number"},
            {"name": "region type",         "type": "text", }
        ],
        "inputs": [],
        "groundTruth": [],
        "others": [],
    },
    {
        # Block N°2
        "name": "winemaker",
        "contexts": [
            {"name": "field area",         "type": "number"},
            {"name": "experience (years)", "type": "number"}
        ],
    },
    {
        # Final block : sample
        "name": "wine test",
        "contexts": [
            {"name": "color",             "type": "text"},
        ],
        "inputs": [
            {"name": "density",           "type": "number"},
            {"name": "pH",                "type": "number"},
            {"name": "alcohol",           "type": "number"},
        ],
        "groundTruth": [
            {"name": "quality",           "type": "number"}
        ]
    },
]

debiai_project.set_blockstructure(wine_block_structure)

# ============= Project samples =============

# Add samples with a numpy array
samples_np = np.array([
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

debiai_project.add_samples(samples_np)

# Add second patch of samples with a numpy array
samples_np_2 = np.array([
    ["region", "Average temperature", "region type", "winemaker", "field area",
        "experience (years)", "wine test", "color", "density", "pH", "alcohol", "quality"],
    ["Sud", 30, "Hot", 3, 4898, 43, "c_87854", 2, 0.1690, 2.00, 8.00, 5],
    ["Sud", 30, "Hot", 3, 4898, 43, "c_87855", 3, 0.8968, 4.90, 7.20, 7],
    ["Sud", 30, "Hot", 3, 4898, 43, "c_87856", 4, 0.7948, 1.05, 8.16, 6],
])

debiai_project.add_samples(samples_np_2)

# Add third patch of samples with a dataframe
samples_df = pd.DataFrame({
    "region": ["Nord", "Nord"],
    "Average temperature": [22, 22],
    "region type": ["Cold", "Cold"],
    "winemaker": [1, 2],
    "field area": [3890, 390],
    "experience (years)": [12, 2],
    "wine test": ["d_0029", "d_0002"],
    "color": [3, 3],
    "density": [0.28, 0.388],
    "pH": [3.0, 3.1],
    "alcohol": [9.0, 8.87],
    "quality": [8.0, 7.9],
})

debiai_project.add_samples_pd(samples_df)

# The project samples should be available on the backend and ready to be analysed with the Debiai dashboard

# ============= Model results =============

# Setting the project models expected results

wine_expected_results = [
    {"name": "quality guess",  "type": "number"},
    {"name": "quality error",  "type": "number"}
]

debiai_project.set_expected_results(wine_expected_results)

# Once the expected results are set, we can add the model results

# Create model and add results
debiai_model_1 = debiai_project.create_model("Model 1")
debiai_model_2 = debiai_project.create_model(
    "Model 2", {"Metadata title": "meta data"})
debiai_model_3 = debiai_project.create_model("Model 3")

# === Adding results with a numpy Array
results_np = np.array(
    [["region", "winemaker", "wine test", "quality guess", "quality error"],
     ["Alsace", 1, "a_11981", 1, 5],
     ["Alsace", 1, "a_11982", 1, 8],
     ["Alsace", 1, "a_11983", 2, 8],
     ["Alsace", 2, "b_65464", 1, 2],
     ["Alsace", 2, "b_65465", 5, 5],
     ["Alsace", 2, "b_65466", 1, 4]]
)

debiai_model_1.add_results_np(results_np)

# === Adding results with a dict
results_dict = {
    "Alsace": {  # Block 1 : Region
        1: {  # Block 2 : Winemaker
            "a_11981": [5, 1],  # Block 3 : Wine test (sample) & Results
            "a_11982": [4, 0],
            "a_11983": [5, 0]
        },
        2: {
            "b_65464": [6, 0],
            "b_65465": [4, 2],
            "b_65466": [4, -1]
        }
    }
}

# Order of the given results array,
# The default order is the expected_results order
results_order = ["quality guess", "quality error"]

debiai_model_2.add_results_dict(results_dict)

results_dict = {
    "Alsace": {
        1: {
            "a_11981": [4, 0],
            "a_11983": [6, 1]
        },
    }
}

# Will overwrite the Alsace/1/a_11981 and the Alsace/1/a_11983 last results
debiai_model_2.add_results_dict(results_dict, results_order)

# === Adding results with a dataframe

results_df = pd.DataFrame({
    "region": ["Nord", "Nord"],
    "winemaker": [1, 2],
    "wine test": ["d_0029", "d_0002"],
    "quality guess": [8.0, 8.0],
    "quality error": [0, 0.1],
})

debiai_model_3.add_results_df(results_df)

# The model results should be available on the backend and ready to be analysed with the Debiai dashboard
