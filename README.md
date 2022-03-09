# DebiAI Python module
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

This Python module is an interface with DebiAI, you can use directly it in your Python project workflow to provide DebiAI with data.

## Features :
- Create projects
- Insert your project data
- Insert model metadata and model results
- Recovery of the samples selections made with the dashboard
- Create tf.dataset from the project or selection

## Requierements:
* A running DebiAI instance
* Numpy
* Pandas
* Eventualy Tensorflow

## Quickstart

```python
from debiai import debiai
import pandas as pd
import numpy as np

DEBIAI_BACKEND_URL = "http://localhost:3000/"
DEBIAI_PROJECT_NAME = "Hello DebiAI"

# Initialisation
my_debiai = debiai.Debiai(DEBIAI_BACKEND_URL)

# Creating a project
debiai_project = my_debiai.create_project(DEBIAI_PROJECT_NAME)

# Creating the project block structure
block_structure = [
    {
        # The sample: an image with contexts, GDT and an ID
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

debiai_project.set_blockstructure(block_structure)


# ======== Adding the project samples ========
# Adding samples with a dataframe
samples_df = pd.DataFrame({
    "Image ID":         ["image-1", "image-2", "image-3"],
    "My context 1":     ["A", "B", "C"],
    "My context 2":     [0.28, 0.388, 0.5],
    "My groundtruth 1": [8, 7, 19],
})

debiai_project.add_samples_pd(samples_df)

# The project samples are ready to be analysed with the dashboard


# ===== Adding the project model results =====
# Setting the project models expected results
expected_results = [
    {"name": "Model result",     "type": "number"},
    {"name": "Model confidence", "type": "number"},
    {"name": "Model error",      "type": "text"},
]

debiai_project.set_expected_results(expected_results)

# Create the models
debiai_model_1 = debiai_project.create_model("Model 1")
debiai_model_2 = debiai_project.create_model("Model 2")

# Adding results with a numpy Array
results_np = np.array(
    [["Image ID", "Model result", "Model confidence", "Model error"],
     ["image-1", 3,  0.98, "yes"],
     ["image-2", 7,  0.97, "no"],
     ["image-3", 10, 0.8, "yes"]]
)

debiai_model_1.add_results_np(results_np)

# Adding results with a dataframe
results_df = pd.DataFrame({
    "Image ID": ["image-1", "image-2", "image-3"],
    "Model result": [5, 7, 19],
    "Model confidence": [0.22, 0.8, 0.9],
    "Model error": ["yes", "no", "no"],
})

debiai_model_2.add_results_df(results_df)

# The model results are ready to be analysed with the Debiai dashboard
```
<img src="./images/quickstart_results.png">

## Installation

### With pip :

Comming soon

### By building the package :

**Requirements :**
* setuptools
* wheel
* pip


Clone the module repository :
```bash
git clone git@github.com:DebiAI/py-debiai.git

cd pythonModule
```
Execute
```bash
./build_package.sh
```
Install
```bash
pip install build_package/*.tar.gz
```
You can now use the DebiAI module inside your script with `from debiai import debiai`

_(if any script does not work due to bad permissions, use `chmod +x *.sh`_

### Update

```bash
cd pythonModule

git pull

./build_package.sh

pip install build_package/*.tar.gz
```

# Documentation

Comming soon

---

<p align="center" style="display:flex; align-items:center; justify-content:space-around" >
  Developed by :
  <a href="https://www.irt-systemx.fr/" title="IRT SystemX">
   <img src="https://www.irt-systemx.fr/wp-content/uploads/2013/03/system-x-logo.jpeg"  height="70">
  </a>
  Integrated in :
  <a href="https://www.confiance.ai/" title="Conf AI">
   <img src="https://pbs.twimg.com/profile_images/1443838558549258264/EvWlv1Vq_400x400.jpg"  height="70">
  </a>
</p>

---
