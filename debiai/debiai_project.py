import hashlib
import pandas as pd
import numpy as np
from typing import List

# Models
from .debiai_model import Debiai_model
from .debiai_selection import Debiai_selection
from .debiai_tag import Debiai_tag

# Services
import utils as utils
import debiai_utils as debiai_utils
from .debiai_services.df_to_dict_tree import df_to_dict_tree
from .debiai_services.np_to_dict import check_np_array, np_to_dict

DEBIAI_TYPES = ["contexts", "inputs", "groundTruth", "others"]


class Debiai_project:
    """
    A Debiai project
    """

    def __init__(self, name: str, id: str, backend_url: str):
        self.name = name
        self.id = id
        self.backend_url = backend_url

        self.block_structure = None
        self.expected_results = None

        self.models = None
        self.creation_date = None
        self.update_date = None

        self.project_infos()  # Load block_structure & expected_results

        # TODO : load creation date, datasets, etc...

    def __repr__(self):
        return "DEBIAI project :  " + str(self.name) + "\n" +\
               "Creation date : " + utils.timestamp_to_date(self.creation_date) + "\n" +\
               "Update date : " + \
            utils.timestamp_to_date(self.update_date) + "\n"

    def project_infos(self):
        project_info = utils.get_project(self.backend_url, self.id)
        if 'blockLevelInfo' in project_info:
            self.block_structure = project_info['blockLevelInfo']
        if 'resultStructure' in project_info:
            self.expected_results = project_info['resultStructure']
        if 'models' in project_info:
            self.models = project_info['models']
        if 'creationDate' in project_info:
            self.creation_date = project_info['creationDate']
        if 'updateDate' in project_info:
            self.update_date = project_info['updateDate']
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
            raise ValueError("The " + str(self.name) +
                             " DEBIAI project block_structure hasn't been set yet")

    def set_blockstructure(self, block_structure: List[dict]) -> bool:
        """
         Add a block structure to the project
         This step is requiered before uploading data
         Throw error if the block structure is already created

         block_structure syntax:

         [
             {
                 "name": str
                 "contexts": [
                     {
                         "name": str,
                         "type": 'text', 'number', 'boolean',
                         "default"?: str, number
                     },
                     ...
                 ],
                 "inputs": [
                     {
                         "name": str,
                         "type": 'text', 'number', 'boolean',
                         "default"?: str, number
                     },
                     ...
                 ],
                 "groundtruth": [
                     {
                         "name": str,
                         "type": 'text', 'number', 'boolean',
                         "default"?: str, number
                     },
                     ...
                 ],
                 "results": [
                     {
                         "name": str,
                         "type": 'text', 'number', 'boolean',
                         "default"?: str, number
                     },
                     ...
                 ]
             },
             ...
         ]

         The last block will be considered the sample block, and will mark the end of the tree
         At least one block is requiered

         """

        # Check if blocklevel structure is already created
        proj_info = self.project_infos()
        if proj_info["blockLevelInfo"] != []:
            raise ValueError(
                "Cannot set the blocklevel structure - already created")

        # Check that there is at least one block
        if not len(block_structure):
            raise ValueError(
                "At least a block is requiered in the block structure")

        # Check that all the properties are correct
        for i, block in enumerate(block_structure):
            if 'name' not in block:
                raise ValueError(
                    "The 'name' is requiered in the block n°" + (i + 1))

            for type_ in block:
                if type_ not in DEBIAI_TYPES and type_ != 'name':
                    print("Warning : unknown block type '" + type_ +
                          "'. Use those block types : " + str(DEBIAI_TYPES))

            for debiai_type in DEBIAI_TYPES:
                if debiai_type in block:
                    for collumn in block[debiai_type]:
                        if 'name' not in collumn:
                            raise ValueError("The name of the column is requiered in the '" +
                                             debiai_type + "' in the block '" + block['name'] + "'")
                        if 'type' not in collumn:
                            raise ValueError("The type of the column is requiered in the '" +
                                             debiai_type + "' in the block '" + block['name'] + "'")
                        if collumn['type'] not in ['text', 'number', 'boolean']:
                            raise ValueError(
                                "Unknown type of the column '" + collumn['name'] + "' in the block '" + block['name'] + "'. Use : ['text', 'number', 'boolean']")

        # Set the block_structure
        utils.add_blocklevel(self.backend_url, self.id, block_structure)
        self.block_structure = block_structure
        return True

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
            raise ValueError("The " + str(self.name) +
                             " DEBIAI project expected_results hasn't been set yet")

    def set_expected_results(self, expected_results: List[dict]) -> List[dict]:
        if self.expected_results is not None:
            raise ValueError(
                "The project expected results have been already set")

        expResults = []

        for column in expected_results:
            if "name" not in column:
                raise ValueError(
                    "The attribute 'name' is requiered in each column")
            if "type" not in column:
                raise ValueError(
                    "The attribute 'type' is requiered in each column")

            col = [c for c in expResults if c["name"] == column["name"]]
            if len(col) > 0:
                raise ValueError("Each result name need to be unique")

            newRes = {
                "name": column["name"],
                "type": column["type"]
            }

            if "default" in column:
                newRes["default"] = column["default"]
                # TODO check default type same as col type

            expResults.append(newRes)

        utils.post_expected_results(self.backend_url, self.id, expResults)
        self.expected_results = expResults
        return expResults

    def add_expected_result(self, column: dict) -> List[dict]:

        if self.expected_results is None:
            raise ValueError(
                "The project does not have an expected results to update")

        if "name" not in column:
            raise ValueError(
                "The attribute 'name' is requiered in the new result column")
        if "type" not in column:
            raise ValueError(
                "The attribute 'type' is requiered in the new result column")
        if "default" not in column:
            raise ValueError(
                "The attribute 'default' is requiered in the new result column")

        # TODO check default type same as col type

        col = [c for c in self.expected_results if c["name"] == column["name"]]
        if len(col) > 0:
            raise ValueError(
                "'" + column["name"] + "' is already expected as a result")

        newRes = {
            "name": column["name"],
            "type": column["type"],
            "default": column["default"]
        }

        ret = utils.post_add_expected_results(
            self.backend_url, self.id, newRes)
        self.expected_results = ret
        return ret

    def remove_expected_result(self, column: str) -> List[dict]:
        if self.expected_results is None:
            raise ValueError(
                "The project does not have an expected results to update")

        # TODO check default type same as col type

        ret = utils.remove_expected_results(self.backend_url, self.id, column)
        self.expected_results = ret
        return ret

    # Add samples

    def add_samples(self, samples: np.array) -> bool:
        """
            Add samples to the curent project, based on his block structure.
            Each one of the block structure elements need to be present in the samples numpy array, exept for the results one.

            Exemple :
            Simple block structure :
                                    =======block_1=======   ======block_2======   ========samples=========
                                    context_a, context_b,   context_c, input_d,   input_e, GDT_f, result_g

            The numpy array first row should containt the folowing labels in any order:
                                    block_1, context_a, context_b, block_2, context_c, input_d, samples, input_e, GDT_f
            note that the result_g is not asked.

            If one the the requiered labels are missing, the samples wont be uploaded.
            Any labels that are not requiered will be ignored
            The folowing rows, if the types are correct, will be added to the database.
        """

        self.get_block_structure()  # Check that the block_structure has been set

        # Check that the array is correct and create a column index map
        indexMap = check_np_array(self.block_structure, samples)

        SAMPLE_CHUNK_SIZE = 5000  # Nuber of sample that will be added in one chunk
        SAMPLE_TO_UPLOAD = samples.shape[0] - 1

        p_bar = utils.progress_bar('Adding samples', SAMPLE_TO_UPLOAD)
        nb_sample_added = 0

        while nb_sample_added < SAMPLE_TO_UPLOAD:
            np_to_add = samples[nb_sample_added + 1:
                                nb_sample_added + 1 + SAMPLE_CHUNK_SIZE]

            dict_to_add = np_to_dict(self.block_structure, np_to_add, indexMap)

            utils.post_add_tree(self.backend_url, self.id, dict_to_add)

            nb_sample_added += SAMPLE_CHUNK_SIZE
            p_bar.update(min([nb_sample_added, SAMPLE_TO_UPLOAD]))

        return True

    def add_samples_pd(self, df: pd.DataFrame, get_hash=None) -> bool:
        """
            Add samples to the curent project, based on his block structure.
            Each one of the block structure elements need to be present in the samples dataframe

            Exemple :
            Simple block structure :
                                    =======block_1=======   ======block_2======   ========samples=========
                                    context_a, context_b,   context_c, input_d,   input_e, GDT_f, result_g

            The dataframe columns should containt the folowing labels in any order:
                                    block_1, context_a, context_b, block_2, context_c, input_d, samples, input_e, GDT_f
            note that the result_g is not asked.

            If one the the requiered labels are missing, the samples wont be uploaded.
            Any labels that aren't requiered will be ignored
        """
        self.get_block_structure()  # Check that the block_structure has been set

        SAMPLE_CHUNK_SIZE = 5000  # Nuber of sample that will be added in one chunk
        SAMPLE_TO_UPLOAD = df.shape[0]
        p_bar = utils.progress_bar('Adding samples', SAMPLE_TO_UPLOAD)

        nb_sample_added = 0

        while nb_sample_added < SAMPLE_TO_UPLOAD:

            df_to_add = df[nb_sample_added:nb_sample_added + SAMPLE_CHUNK_SIZE]
            dict_to_add = df_to_dict_tree(df_to_add, self.block_structure)

            utils.post_add_tree(self.backend_url, self.id, dict_to_add)
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

    def get_model(self, model_name: str) -> Debiai_model or None:
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
            raise ValueError(
                "Can't create the model: The model name is requiered")

        # Call the backend
        if utils.post_model(self.backend_url, self.id, name, metadata):
            return Debiai_model(self, name, name)
        else:
            return False

    def delete_model(self, model_name: str) -> bool:
        #  check parameters
        if not model_name:
            raise ValueError(
                "Can't delete the model: The model name is requiered")
        # Find the model ID
        model = self.get_model(model_name)
        if not model:
            raise ValueError(
                "The model '" + model_name + "' does not exist")

        # Call the backend
        utils.delete_model(self.backend_url, self.id, model.id)

    # Hash

    def check_hash(self, hash_list: list) -> list:
        """ Check list of hashs with backend """
        res = utils.check_hash_exist(self.backend_url, self.id, hash_list)
        return res

    def __get_hash_from_df(self, block_name: list, row, map_id: str):
        """ Subfunction creating a path from a row of df and hashing it """
        path = ""

        for name in block_name:
            if name == map_id:
                path += str(row.name)
            else:
                path += str(row[name])
            path += "/"

        hash = hashlib.sha256(path.encode("utf-8")).hexdigest()

        return hash

    def create_hash(self, df: pd.DataFrame, map_id: str = None) -> pd.DataFrame:
        """
        Create a hash column into the df
        """
        # Get block names
        block_name = []

        for block in self.block_structure:
            block_name.append(block["name"])

        # Create path to hash for each row

        df["hash"] = df.apply(lambda row: self.__get_hash_from_df(
            block_name, row, map_id), axis=1)

        return df

    # Selections

    def get_selections(self) -> List[Debiai_selection]:
        """
        Get from the backend the list of selections, convert it in objects and returns it
        """
        selections_json = utils.get_selections(self.backend_url, self.id)

        selections = []
        for s in selections_json:
            selections.append(Debiai_selection(
                self, s['name'], s['id'], s['creationDate'], s['nbSamples'], s.get('requestId', None)))
        return selections

    def get_selection(self, selection_name: str) -> Debiai_selection or None:
        selections = self.get_selections()
        for selection in selections:
            if selection.name == selection_name:
                return selection
        return None

    # Tags

    def get_tags(self) -> List[Debiai_tag]:
        """
        Get from the backend the list of tags, convert it in objects and returns it
        """
        tags_json = utils.get_tags(self.backend_url, self.id)

        # Convert each request into a debiai_selection object
        tags = []
        for t in tags_json:
            tags.append(Debiai_tag(
                self, t['id'], t['name'], t['creationDate'], t['updateDate']))
        return tags

    def get_tag(self, tag_name: str) -> Debiai_tag or None:
        """
        Get from the backend the list of tags,
        returns the tag with the given name or none
        """
        tags = self.get_tags()

        for t in tags:
            if t.name == tag_name:
                return t

        return None

    # Pull data

    def get_numpy(self) -> np.array:
        self.get_block_structure()  # Check that the block_structure has been set

        # Pulls all the data
        sample_tree = utils.get_project_samples(self.backend_url, self.id)
        # print(sample_tree)
        # Create the first row with the column names
        columns = np.array([])
        for block in self.block_structure:
            columns = np.append(columns, block['name'])
            for debiai_type in DEBIAI_TYPES:
                if debiai_type in block:
                    for column in block[debiai_type]:
                        columns = np.append(columns, column['name'])

        data = debiai_utils.tree_to_array(self.block_structure, sample_tree)
        return np.vstack([columns, data])

    def get_dataframe(self) -> pd.DataFrame:
        # Pull the selected samples from the backend
        # returns a pd.DataFrame
        numpy = self.get_numpy()
        col = numpy[0]
        df = pd.DataFrame(data=numpy[1:], columns=col)

        # Convert object columns to number columns
        cols = df.columns[df.dtypes.eq('object')]
        df[cols] = df[cols].apply(pd.to_numeric, errors='ignore')

        return df

    def get_tf_dataset(self) -> 'tf.data.Dataset':
        import tensorflow as tf

        self.get_block_structure()  # Check that the block_structure has been set

        excepted_inputs = []
        excepted_gdt = []

        for level in self.block_structure:
            if "inputs" in level:
                excepted_inputs += level['inputs']
            if "groundTruth" in level:
                excepted_gdt += level['groundTruth']

        return tf.data.Dataset.from_generator(
            self.__load_samples, (tf.float32, tf.int32),
            ((len(excepted_inputs), ), (len(excepted_gdt), ))
        )

    def __load_samples(self):
        PACH_SIZE = 1000  # Pull samples each PACH_SIZE samples

        i = 0
        while True:
            # Pull a sample tree
            sample_tree = utils.get_project_training_samples(
                self.backend_url, self.id, i, PACH_SIZE)

            # Extract inputs & gdt
            inputs, gdt = debiai_utils.get_inputs_and_gdt_patch(
                self.block_structure, sample_tree)

            if len(inputs) == 0:
                break

            # Yield each one of the samples to the dataset
            for j in range(len(inputs)):
                yield inputs[j], gdt[j]

            # TODO : clean progress bar
            i += PACH_SIZE

    def get_tf_dataset_with_provided_inputs(self,
                                            input_function: 'function',
                                            output_types: tuple,
                                            output_shapes: tuple,
                                            classes: list
                                            ) -> 'tf.data.Dataset':
        import tensorflow as tf

        self.get_block_structure()  # Check that the block_structure has been set

        self.dataset_generator_input_function = input_function
        self.dataset_generator_classes = classes

        return tf.data.Dataset.from_generator(self.__load_samples_with_provided_inputs,
                                              output_types=output_types,
                                              output_shapes=output_shapes)

    def __load_samples_with_provided_inputs(self):
        PACH_SIZE = 1000  # Pull samples each PACH_SIZE samples

        # Only deal with 1 gdt TODO : deal with the case with more than 1 gdt

        i = 0
        while True:
            # Pull a sample tree
            sample_tree = utils.get_project_training_samples(
                self.backend_url, self.id, i, PACH_SIZE)

            # Extract samples & gdt
            samples, gdt = debiai_utils.get_samples_and_gdt_patch(
                self.block_structure, sample_tree)

            if len(samples) == 0:
                break

            # Yield each one of the samples to the dataset
            for j in range(len(samples)):
                inputs = self.dataset_generator_input_function(samples[j])
                gdt_number = self.dataset_generator_classes.index(gdt[j][0])
                yield inputs, [gdt_number]

            i += PACH_SIZE

            # TODO : create a clean progress bar
