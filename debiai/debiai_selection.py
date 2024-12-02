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
    ):
        self.project = project
        self.name = name
        self.id = id
        self.creationDate = creationDate
        self.nbSamples = nbSamples

    def __repr__(self):
        return (
            "DEBIAI selection : '" + str(self.name) + "'\n"
            "creation date : '" + utils.timestamp_to_date(self.creationDate) + "'\n"
            "number of samples  : '" + str(self.nbSamples) + "'\n"
        )

    def get_dataframe(self) -> pd.DataFrame:
        block_structure = self.project.get_block_structure()

        # Get the project samples_id list
        samples = utils.get_selection_samples(
            self.project.debiai_url, self.project.id, self.id, block_structure
        )

        return samples

    def get_samples_id(self):
        return utils.get_samples_id_from_selection(
            self.project.debiai_url, self.project.id, self.id
        )
