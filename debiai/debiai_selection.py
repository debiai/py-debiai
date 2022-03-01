from typing import List
import numpy as np
import pandas as pd
import hashlib

import utils as utils
import debiai_utils as debiai_utils

DEBIAI_TYPES = ["contexts", "inputs", "groundTruth", "others"]


class Debiai_selection:
    """
    A Debiai data selection : a list of sample id
    It can belongs to a request
    """

    def __init__(self, project, name: str, id: str, creationDate: int, nbSamples: str, requestId: str):
        self.project = project
        self.name = name
        self.id = id
        self.creationDate = creationDate
        self.nbSamples = nbSamples
        self.requestId = requestId

    def __repr__(self):
        return (
            "DEBIAI selection : '" + str(self.name) + "'\n"
            "creation date : '" +
            utils.timestamp_to_date(self.creationDate) + "'\n"
            "number of samples  : '" + str(self.nbSamples) + "'\n"
        )

    def get_numpy(self) -> np.array:
        # Pulls all the selection data
        sampleTree = utils.get_samples_from_selection(
            self.project.backend_url, self.project.id, self.id)

        block_structure = self.project.project_infos()['blockLevelInfo']

        """
            tree structure :
            [
                {
                    'id',
                    'creationDate',
                    'groundTruth',
                    'inputs',
                    'level',
                    'metaDataList',
                    'name',
                    'parentPath',
                    'path',
                    'updateDate',
                    'version',
                    'childrenInfoList' : {

                    }
                }
            ]
        """
        columns = np.array([])
        # Create the first row with the column names
        for block in block_structure:
            columns = np.append(columns, block['name'])
            for debiai_type in DEBIAI_TYPES:
                if debiai_type in block:
                    for column in block[debiai_type]:
                        columns = np.append(columns, column['name'])

        data = debiai_utils.tree_to_array(block_structure, sampleTree)
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

    # Tensorflow dataset generator

    def get_tf_dataset(self) -> 'tf.data.Dataset':
        import tensorflow as tf

        block_structure = self.project.project_infos()['blockLevelInfo']

        excepted_inputs = []
        excepted_gdt = []

        for level in block_structure:
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

        for i in range(0, self.nbSamples, PACH_SIZE):
            # Pull a sample tree
            sampleTree = utils.get_training_samples_from_selection(
                self.project.backend_url, self.project.id, self.id, i, PACH_SIZE)

            # Extract inputs & gdt
            inputs, gdt = debiai_utils.get_inputs_and_gdt_patch(
                self.project.block_structure, sampleTree)

            # Pull undirect inputs from external source (image, ...) from inputs
            # TODO : try with Faurecia
            # Yield each one of the samples to the dataset
            for j in range(len(inputs)):
                yield inputs[j], gdt[j]

            # TODO : create a clean progress bar
            print(str(i) + "/" + str(self.nbSamples))

    def get_tf_dataset_with_provided_inputs(self,
                                            input_function: 'function',
                                            output_types: tuple,
                                            output_shapes: tuple,
                                            classes: list
                                            ) -> 'tf.data.Dataset':
        import tensorflow as tf

        self.dataset_generator_input_function = input_function
        self.dataset_generator_classes = classes

        block_structure = self.project.project_infos()['blockLevelInfo']

        return tf.data.Dataset.from_generator(self.__load_samples_with_provided_inputs,
                                              output_types=output_types,
                                              output_shapes=output_shapes)

    def __load_samples_with_provided_inputs(self):
        PACH_SIZE = 1000  # Pull samples each PACH_SIZE samples

        # Only deal with 1 gdt TODO : deal with the case with more than 1 gdt

        for i in range(0, self.nbSamples, PACH_SIZE):
            # Pull a sample tree
            sampleTree = utils.get_training_samples_from_selection(
                self.project.backend_url, self.project.id, self.id, i, PACH_SIZE)

            # Extract samples & gdt
            samples, gdt = debiai_utils.get_samples_and_gdt_patch(
                self.project.block_structure, sampleTree)

            # Yield each one of the samples to the dataset
            for j in range(len(samples)):
                inputs = self.dataset_generator_input_function(samples[j])
                gdt_number = self.dataset_generator_classes.index(gdt[j][0])
                yield inputs, [gdt_number]

            # TODO : create a clean progress bar
