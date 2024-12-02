import pandas as pd
import numpy as np
from typing import List, Union

# Models
from .debiai_model import Debiai_model
from .debiai_selection import Debiai_selection

# Services
import utils as utils
from .debiai_services.df_to_dict_tree import df_to_dict_tree, DEBIAI_TYPES
from .debiai_services.np_to_dict import check_np_array, np_to_dict
import json


class Debiai_project:
    """
    A Debiai project
    """

    def __init__(self, name: str, id: str, debiai_url: str):
        self.name = name
        self.id = id
        self.debiai_url = debiai_url

        self.block_structure = None
        self.expected_results = None

        self.models = None
        self.creation_date = None
        self.update_date = None

        self.project_infos()  # Load block_structure & expected_results

        # TODO : load creation date, datasets, etc...

    def __repr__(self):
        return (
            "DEBIAI project :  "
            + str(self.name)
            + "\n"
            + "Creation date : "
            + utils.timestamp_to_date(self.creation_date)
            + "\n"
            + "Update date : "
            + utils.timestamp_to_date(self.update_date)
            + "\n"
        )

    def project_infos(self):
        project_info = utils.get_project(self.debiai_url, self.id)
        if "blockLevelInfo" in project_info:
            self.block_structure = project_info["blockLevelInfo"]
        if "resultStructure" in project_info:
            self.expected_results = project_info["resultStructure"]
        if "models" in project_info:
            self.models = project_info["models"]
        if "creationDate" in project_info:
            self.creation_date = project_info["creationDate"]
        if "updateDate" in project_info:
            self.update_date = project_info["updateDate"]
        return project_info

    # Blocks structure
    def block_structure_defined(self):
        self.project_infos()
        if self.block_structure:
            return self.block_structure
        else:
            return False

    def get_block_structure(self):
        bs = self.block_structure_defined()
        if bs:
            return bs
        else:
            raise ValueError(
                "The "
                + str(self.name)
                + " DEBIAI project block_structure hasn't been set yet"
            )

    def set_blockstructure(self, block_structure: List[dict]) -> bool:
        """
        Add a block structure to the project
        This step is required before uploading data
        Throw error if the block structure is already created

        block_structure syntax:

        [
            {
                "name": str
                "contexts": [
                    {
                        "name": str,
                        "type": 'text', 'number', 'boolean', 'list', 'dict',
                        "default"?: str, number,
                        "group"?: str
                    },
                    ...
                ],
                "inputs": [
                    {
                        "name": str,
                        "type": 'text', 'number', 'boolean', 'list', 'dict',
                        "default"?: str, number
                        "group"?: str
                    },
                    ...
                ],
                "groundtruth": [
                    {
                        "name": str,
                        "type": 'text', 'number', 'boolean', 'list', 'dict',
                        "default"?: str, number
                        "group"?: str
                    },
                    ...
                ],
                "results": [
                    {
                        "name": str,
                        "type": 'text', 'number', 'boolean', 'list', 'dict',
                        "default"?: str, number
                        "group"?: str
                    },
                    ...
                ]
            },
            ...
        ]

        The last block will be considered the sample block,
        and will mark the end of the tree.

        At least one block is required
        """

        valid_types = ["text", "number", "boolean", "list", "dict"]

        # Check if blockLevel structure is already created
        proj_info = self.project_infos()
        if proj_info["blockLevelInfo"] != []:
            raise ValueError("Cannot set the blockLevel structure - already created")

        if not isinstance(block_structure, list):
            raise TypeError("The block structure must be a list")

        # Check that there is at least one block
        if not len(block_structure):
            raise ValueError("At least a block is required in the block structure")

        # Check that all the properties are correct
        for i, block in enumerate(block_structure):
            if "name" not in block:
                raise ValueError("The 'name' is required in the block n°" + str(i + 1))

            for type_ in block:
                if type_ not in DEBIAI_TYPES and type_ != "name":
                    print(
                        "Warning : unknown block type '"
                        + type_
                        + "'. Use those block types : "
                        + str(DEBIAI_TYPES)
                    )

            for debiai_type in DEBIAI_TYPES:
                if debiai_type in block:
                    for column in block[debiai_type]:
                        if "name" not in column:
                            raise ValueError(
                                "The name of the column is required in the '"
                                + debiai_type
                                + "' in the block '"
                                + block["name"]
                                + "'"
                            )
                        if "type" not in column:
                            raise ValueError(
                                "The type of the column is required in the '"
                                + debiai_type
                                + "' in the block '"
                                + block["name"]
                                + "'"
                            )
                        if column["type"] not in valid_types:
                            raise ValueError(
                                "Unknown type for column '"
                                + column["name"]
                                + "' in the block '"
                                + block["name"]
                                + "'. Use one of those types : "
                                + str(valid_types)
                            )

                        if "group" in column:
                            if not isinstance(column["group"], str):
                                raise ValueError(
                                    "The group of the column '"
                                    + column["name"]
                                    + "' in the block '"
                                    + block["name"]
                                    + "' must be a string"
                                )

        # Set the block_structure
        utils.add_blocklevel(self.debiai_url, self.id, block_structure)
        self.block_structure = block_structure

    # Results structure
    def expected_results_defined(self):
        self.project_infos()
        if self.expected_results:
            return self.expected_results
        else:
            return False

    def get_expected_results(self):
        rs = self.expected_results_defined()
        if rs:
            return rs
        else:
            raise ValueError(
                "The "
                + str(self.name)
                + " DEBIAI project expected_results hasn't been set yet"
            )

    def set_expected_results(self, expected_results: List[dict]) -> List[dict]:
        if self.expected_results is not None:
            raise ValueError("The project expected results have been already set")

        expResults = []

        for column in expected_results:
            if "name" not in column:
                raise ValueError("The attribute 'name' is required in each column")
            if "type" not in column:
                raise ValueError("The attribute 'type' is required in each column")

            col = [c for c in expResults if c["name"] == column["name"]]
            if len(col) > 0:
                raise ValueError("Each result name need to be unique")

            newRes = {"name": column["name"], "type": column["type"]}

            if "default" in column:
                newRes["default"] = column["default"]
                # TODO check default type same as col type

            if "group" in column:
                if type(column["group"]) is str:
                    raise ValueError("The group attribute must be a string")

                newRes["group"] = column["group"]

            expResults.append(newRes)

        utils.post_expected_results(self.debiai_url, self.id, expResults)
        self.expected_results = expResults

    def add_expected_result(self, column: dict) -> List[dict]:
        if self.expected_results is None:
            raise ValueError("The project does not have an expected results to update")

        if "name" not in column:
            raise ValueError(
                "The attribute 'name' is required in the new result column"
            )
        if "type" not in column:
            raise ValueError(
                "The attribute 'type' is required in the new result column"
            )
        if "default" not in column:
            raise ValueError(
                "The attribute 'default' is required in the new result column"
            )

        # TODO check default type same as col type

        col = [c for c in self.expected_results if c["name"] == column["name"]]
        if len(col) > 0:
            raise ValueError("'" + column["name"] + "' is already expected as a result")

        newRes = {
            "name": column["name"],
            "type": column["type"],
            "default": column["default"],
        }

        ret = utils.post_add_expected_results(self.debiai_url, self.id, newRes)
        self.expected_results = ret
        return ret

    def remove_expected_result(self, column: str) -> List[dict]:
        if self.expected_results is None:
            raise ValueError("The project does not have an expected results to update")

        # TODO check default type same as col type

        ret = utils.remove_expected_results(self.debiai_url, self.id, column)
        self.expected_results = ret
        return ret

    # Add samples
    def add_samples(self, samples: np.array) -> bool:
        """
        Add samples to the current project, based on his block structure.
        The defined block structure elements have to be present in the numpy array

        Example :
        If the defined block structure is:
            =======block_1=======   ======block_2======   ====samples===
            context_a, context_b,   context_c, input_d,   input_e, GDT_f

        The numpy array first row should contain the following labels in any order:
        block_1, context_a, context_b, block_2, context_c, input_d, samples, GDT_f

        Note that the result_g is not asked.

        If one the the required labels are missing, the samples wont be uploaded.
        Any labels that aren't required will be ignored
        """

        self.get_block_structure()  # Check that the block_structure has been set

        # Check that the array is correct and create a column index map
        indexMap = check_np_array(self.block_structure, samples)

        SAMPLE_CHUNK_SIZE = 5000  # Number of sample that will be added in one chunk
        SAMPLE_TO_UPLOAD = samples.shape[0] - 1

        p_bar = utils.progress_bar("Adding samples", SAMPLE_TO_UPLOAD)
        nb_sample_added = 0

        while nb_sample_added < SAMPLE_TO_UPLOAD:
            np_to_add = samples[
                nb_sample_added + 1 : nb_sample_added + 1 + SAMPLE_CHUNK_SIZE  # noqa
            ]

            dict_to_add = np_to_dict(self.block_structure, np_to_add, indexMap)

            utils.post_add_tree(self.debiai_url, self.id, dict_to_add)

            nb_sample_added += SAMPLE_CHUNK_SIZE
            p_bar.update(min([nb_sample_added, SAMPLE_TO_UPLOAD]))

        return True

    def add_samples_pd(self, df: pd.DataFrame) -> bool:
        """
        Add samples to the current project, based on its block structure.
        The defined block structure elements have to be present in the samples dataframe

        Example :
        If the defined block structure is:
            =======block_1=======   ======block_2======   ====samples===
            context_a, context_b,   context_c, input_d,   input_e, GDT_f

        The dataframe columns should contain the following labels in any order:
        block_1, context_a, context_b, block_2, context_c, input_d, samples, GDT_f

        Note that the result_g is not asked.

        If one the the required labels are missing, the samples wont be uploaded.
        Any labels that aren't required will be ignored
        """

        self.get_block_structure()  # Check that the block_structure has been set

        # Validate the dataframe
        if not isinstance(df, pd.DataFrame):
            raise TypeError("The samples must be a pandas DataFrame")

        if df.empty:
            return False

        SAMPLE_CHUNK_SIZE = 5000  # Number of sample that will be added in one chunk
        SAMPLE_TO_UPLOAD = df.shape[0]
        p_bar = utils.progress_bar("Adding samples", SAMPLE_TO_UPLOAD)

        nb_sample_added = 0

        while nb_sample_added < SAMPLE_TO_UPLOAD:
            df_to_add = df[
                nb_sample_added : nb_sample_added + SAMPLE_CHUNK_SIZE  # noqa
            ]
            dict_to_add = df_to_dict_tree(df_to_add, self.block_structure)

            utils.post_add_tree(self.debiai_url, self.id, dict_to_add)
            nb_sample_added += SAMPLE_CHUNK_SIZE
            p_bar.update(min([nb_sample_added, SAMPLE_TO_UPLOAD]))

        return True

    # Models
    def get_models(self) -> List[Debiai_model]:
        self.project_infos()
        if self.models:
            return self.models
        else:
            return []

    def get_model(self, model_name: str) -> Union[Debiai_model, None]:
        self.project_infos()
        for model in self.models:
            id = model["id"]
            name = model["name"]
            if name == model_name:
                return Debiai_model(self, id, name)
        return None

    def create_model(self, name: str, metadata: dict = {}) -> Debiai_model:
        #  check parameters
        if not name:
            raise ValueError("Can't create the model: The model name is required")

        try:
            json.dumps(metadata)
        except TypeError:
            raise ValueError("The metadata dictionary is not JSON serializable")

        # Call the backend
        if utils.post_model(self.debiai_url, self.id, name, metadata):
            return Debiai_model(self, name, name, metadata)
        else:
            return False

    def delete_model(self, model_name: str) -> bool:
        #  check parameters
        if not model_name:
            raise ValueError("Can't delete the model: The model name is required")
        # Find the model ID
        model = self.get_model(model_name)
        if not model:
            raise ValueError("The model '" + model_name + "' does not exist")

        # Call the backend
        utils.delete_model(self.debiai_url, self.id, model.id)

    # Selections
    def create_selection(
        self, selection_name: str, samples_id: List[str]
    ) -> Debiai_selection:
        """
        Create a selection of samples from an ID list provided by Debiai
        The ID list should be a list of strings corresponding to the samples ID hash
        generated by Debiai.

        You can get the samples ID list with the get_dataframe method

        params:
            selection_name : str : the name of the selection
            samples_id : list : the list of samples ID hash

        return:
            Debiai_selection : the created selection
        """
        # Check the parameters
        if not selection_name:
            raise ValueError("The selection name is required")
        if not samples_id:
            raise ValueError("The samples ID list is required")
        if not isinstance(samples_id, list):
            raise TypeError("The samples ID list must be a list")
        if not all(isinstance(i, str) for i in samples_id):
            raise ValueError("The samples ID list must be a list of strings")

        # Call the backend
        new_selection = utils.post_selection(
            self.debiai_url, self.id, selection_name, samples_id
        )

        return Debiai_selection(
            self,
            name=selection_name,
            id=new_selection["id"],
            creationDate=new_selection["creationDate"],
            nbSamples=len(samples_id),
        )

    def get_selections(self) -> List[Debiai_selection]:
        """
        Get the list of selections of the project
        """
        selections_json = utils.get_selections(self.debiai_url, self.id)

        selections = []
        for s in selections_json:
            selections.append(
                Debiai_selection(
                    self,
                    s["name"],
                    s["id"],
                    s["creationDate"],
                    s["nbSamples"],
                )
            )
        return selections

    def get_selection(self, selection_name: str) -> Union[Debiai_selection, None]:
        selections = self.get_selections()
        for selection in selections:
            if selection.name == selection_name:
                return selection
        return None

    def delete_selection(self, selection_name: str) -> bool:
        #  check parameters
        if not selection_name:
            raise ValueError(
                "Can't delete the selection: The selection name is required"
            )
        # Find the selection
        selection = self.get_selection(selection_name)
        if not selection:
            raise ValueError("The selection '" + selection_name + "' does not exist")

        # Call the backend
        return utils.delete_selection(self.debiai_url, self.id, selection.id)

    # Pull data
    def get_dataframe(self) -> pd.DataFrame:
        block_structure = self.get_block_structure()

        # Get the project samples_id list
        samples = utils.get_project_samples(self.debiai_url, self.id, block_structure)

        return samples
