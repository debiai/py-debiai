import numpy as np
import pandas as pd

import utils as utils

DEBIAI_TYPES = ["contexts", "inputs", "groundTruth", "others"]


class Debiai_selection:
    """
    A Debiai data selection : a list of sample id
    It can belongs to a request
    """

    def __init__(
        self,
        project,
        name: str,
        id: str,
        creationDate: int,
        nbSamples: int,
        requestId: str,
    ):
        self.project = project
        self.name = name
        self.id = id
        self.creationDate = creationDate
        self.nbSamples = nbSamples
        self.requestId = requestId

    def __repr__(self):
        return (
            "DEBIAI selection : '" + str(self.name) + "'\n"
            "creation date : '" + utils.timestamp_to_date(self.creationDate) + "'\n"
            "number of samples  : '" + str(self.nbSamples) + "'\n"
        )

    def get_numpy(self) -> np.array:
        # Pulls all the selection data
        # samples_id = utils.get_samples_from_selection(
        #     self.project.debiai_url, self.project.id, self.id
        # )

        return

    def get_dataframe(self) -> pd.DataFrame:
        # Pull the selected samples from the backend
        # returns a pd.DataFrame
        numpy = self.get_numpy()
        col = numpy[0]
        df = pd.DataFrame(data=numpy[1:], columns=col)

        # Convert object columns to number columns
        cols = df.columns[df.dtypes.eq("object")]
        df[cols] = df[cols].apply(pd.to_numeric, errors="ignore")

        return df
