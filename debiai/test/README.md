# Testsuite DEBIAI
_created by Quentin Le Helloco_

## Requirements
* unittest
* debiai (obviously)

## Usage
### Starting the testsuite
Using the command
```python3 basic_test.py```
will launch the testsuite.
You can add -v for verbose.
### Adding new data to test
To add data, you have to add a directory to the tests_inputs directory:

Your directory needs to respect the following architecture inside the tests_inputs:
* blockstructure.json = a json dict with information for each block in the blockstructure
* expected_results.json = a json dict with information for each results block in the expected_results structure
* new_expected_results.json = a json dict directly defining the new expected_results to add
* results_dict.json = a json dict of the results like you would have on debiai python module
* results.csv = results to add to the project, as a csv with "," delimiter and first row as headers
* samples.csv = samples to add to the project, as a csv with "," delimiter and first row as headers
* compfiles.json = a informative json dict (specific info just below)

_you can use tests_inpits/wine_small_data/ as an example if needed_

### About compfiles.json 
For each already created project you want to compare with the sample/results put into the testsuite, create a element in the json dict.

Each element must have those attributes:
* "name", name of the project's dir in Control_projects/
* "assert", true/false to define is the specified project is valid or intentionally false

You can also add optional attributes:
* "msg", a string that will be prompted if an assertion failed while comparing with this project
* "tests", a list of string specifing which tests should use this project. If there is not, all tests will use this project.

All projects added to this file must be placed in the Control_projects/ dir

### Adding new tests
In order to add tests, you can create a new function or a new class in the basic_test.py for now.

In the future, it would be good to use different .py
