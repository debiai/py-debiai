"""Debiai selection class."""

import numpy as np
import pandas as pd

import utils as utils
import debiai_utils as debiai_utils

DEBIAI_TYPES = ["contexts", "inputs", "groundTruth", "others"]


class Debiai_selection:
    """A Debiai data selection is a list of sample id."""

    def __init__(
        self,
        project,
        name: str,
        id: str,
        creationDate: int,
        nbSamples: str,
        requestId: str,
    ):
        """Create a Debiai selection object."""
        self.project = project
        self.name = name
        self.id = id
        self.creationDate = creationDate
        self.nbSamples = nbSamples
        self.requestId = requestId

    def __repr__(self) -> str:
        """Return the string representation of the selection."""
        return (
            "DEBIAI selection : '" + str(self.name) + "'\n"
            "creation date : '" + utils.timestamp_to_date(self.creationDate) + "'\n"
            "number of samples  : '" + str(self.nbSamples) + "'\n"
        )

    def get_numpy(self) -> np.array:
        """Get the selected samples as a numpy array."""
        # Pulls all the selection data
        sampleTree = utils.get_samples_from_selection(
            self.project.debiai_url, self.project.id, self.id
        )

        block_structure = self.project._project_infos()["blockLevelInfo"]

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
            columns = np.append(columns, block["name"])
            for debiai_type in DEBIAI_TYPES:
                if debiai_type in block:
                    for column in block[debiai_type]:
                        columns = np.append(columns, column["name"])

        data = debiai_utils._tree_to_array(block_structure, sampleTree)
        return np.vstack([columns, data])

    def get_dataframe(self) -> pd.DataFrame:
        """Get the selected samples as a pandas DataFrame."""
        numpy = self.get_numpy()
        col = numpy[0]
        df = pd.DataFrame(data=numpy[1:], columns=col)

        # Convert object columns to number columns
        cols = df.columns[df.dtypes.eq("object")]
        df[cols] = df[cols].apply(pd.to_numeric, errors="ignore")

        return df
