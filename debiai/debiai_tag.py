from typing import List
import numpy as np
import pandas as pd
import hashlib

import utils as utils
import debiai_utils as debiai_utils

DEBIAI_TYPES = ["contexts", "inputs", "groundTruth", "others"]


class Debiai_tag:
    """
    A Debiai tag : a list of sample id and a tag value
    """

    def __init__(self, project: str, id: str, name: str, creation_date: int, update_date: int):
        # Only the overvew is loaded at init
        self.project = project
        self.id = id
        self.name = name
        self.creation_date = creation_date
        self.update_date = update_date
        self.tags = None

    def load_tags(self):
        if self.tags is None:
            # TODO: check if version has changed before loading
            tag = utils.get_tag(self.project.backend_url,
                                self.project.id, self.id)

            if tag is None or "tags" not in tag or tag["tags"] is None:
                raise ValueError("Error while loading the tag values")

            self.tags = tag["tags"]

    @property
    def tag_number(self) -> dict:
        # Return the number each tag is present in the tag list
        self.load_tags()

        values = {}

        for sampleHash in self.tags.keys():
            if self.tags[sampleHash] in values:
                values[self.tags[sampleHash]] += 1
            else:
                values[self.tags[sampleHash]] = 1

        return values

    def __repr__(self):
        return (
            "DEBIAI tag : '" + str(self.name) + "'\n"
            "creation date : '" +
            utils.timestamp_to_date(self.creation_date) + "'\n"
            "update date : '" +
            utils.timestamp_to_date(self.update_date) + "'\n"
        )

    def get_numpy(self, tag_value: int) -> np.array:
        # Pull all samples with the given tag value
        sampleTree = utils.get_samples_from_tag(
            self.project.backend_url, self.project.id, self.id, tag_value)

        block_structure = self.project.project_infos()['blockLevelInfo']

        # TODO : regroup in one service

        columns = np.array([])
        # Create the first row with the column names
        for block in block_structure:
            columns = np.append(columns, block['name'])
            for debiai_type in DEBIAI_TYPES:
                if debiai_type in block:
                    for column in block[debiai_type]:
                        columns = np.append(columns, column['name'])

        data = debiai_utils.tree_to_array(block_structure, sampleTree)
        if len(data) == 0:
            return np.array([columns])
        return np.vstack([columns, data])

    def get_dataframe(self, tag_value: int) -> pd.DataFrame:
        # Pull the tagged samples from the backend
        # returns a pd.DataFrame
        numpy = self.get_numpy(tag_value)
        col = numpy[0]
        df = pd.DataFrame(data=numpy[1:], columns=col)

        # Convert object columns to number columns
        cols = df.columns[df.dtypes.eq('object')]
        df[cols] = df[cols].apply(pd.to_numeric, errors='ignore')

        return df
