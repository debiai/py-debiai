from typing import List
import numpy as np
import pandas as pd

import utils as utils


class Debiai_model:
    """
    A Debiai project model
    """

    def __init__(self, project, name: str, id: str, metadata: dict = {}):
        self.project = project
        self.name = name
        self.id = id
        self.metadata = metadata

    def expected_results_exists(self):
        """
        Check if the expected results are defined, raise an error if not
        """
        if self.project.expected_results is None:
            raise ValueError(
                "The project expected results need to be specified \
before doing this operation"
            )

    def add_results_dict(
        self, results: dict, expected_results_order: List[str] = None
    ) -> bool:
        """
        Add a result to the model from a dict.
        The tree allow the user to specify to what sample he created the result
        Each one of the block results structure elements need to be present at
        the end of the tree and in the expected_results_order array.
        """
        # Update the block structure & expected results
        self.project.project_infos()

        self.expected_results_exists()

        if type(results) is not dict:
            raise ValueError("Results must be of type dict")

        if expected_results_order is not None:
            for expected_result in self.project.expected_results:
                if expected_result["name"] not in expected_results_order:
                    raise ValueError(
                        "The expected result '"
                        + expected_result["name"]
                        + "' is missing from the expected_results_order Array"
                    )

            for given_expected_result in expected_results_order:
                result_expected = False
                for expected_result in self.project.expected_results:
                    if given_expected_result == expected_result["name"]:
                        result_expected = True
                if not result_expected:
                    raise ValueError(
                        "The given expected result '"
                        + given_expected_result
                        + "' is not an expected result"
                    )
        else:
            expected_results_order = list(
                map(lambda r: r["name"], self.project.expected_results)
            )

        # Start the results verification
        sampleIndex = len(self.project.block_structure) - 1

        for rootBlock in results:
            self.__checkResultDict(
                results[rootBlock],
                0,
                sampleIndex,
                expected_results_order,
                str(rootBlock),
            )

        # Upload the results
        return utils.post_model_results_dict(
            self.project.debiai_url,
            self.project.id,
            self.id,
            results,
            expected_results_order,
        )

    def add_results_df(self, results: pd.DataFrame, map_id=None) -> bool:
        """
        Add results from a dataFrame.
        """
        # Add results with __add_results_pd sequentially
        p_bar = utils.progress_bar("Adding results", results.shape[0], self.name)
        results_added = 0

        chunk_size = 5000
        for start in range(0, results.shape[0], chunk_size):
            results_subset = results.iloc[start : start + chunk_size]  # noqa

            self.__add_results_pd(results_subset, map_id=map_id)

            results_added = results_added + results_subset.shape[0]
            p_bar.update(results_added)

        return True

    def __add_results_pd(self, results: pd.DataFrame, map_id=None) -> bool:
        """Add results to the model from a pd dataframe"""
        self.expected_results_exists()

        # Check if block names are in df columns.
        for block in self.project.block_structure:
            if block["name"] not in results.columns and block["name"] != map_id:
                print("'" + block["name"] + "' is missing from the given samples")
                return False

        # Dataframe form
        # b1    b2    sample    res1  res2  res3
        # b1-1  b2-1  sample-1  1     2     "a"
        # ...   ...   ...       ...   ...   ...

        # Dict form :
        # {
        #     "b1-1": {
        #         "b2-1": {
        #             "sample-1": [1, 2, "a"],
        #             ...
        #         },
        #         ...
        #     },
        #     ...
        # }

        # Extract results name
        results_name = []
        for result in self.project.expected_results:
            results_name.append(result["name"])

        # Transform DataFrame into dic recursively
        dic_res = self.__pd_to_dict_recur(results, 0, results_name)

        return self.add_results_dict(dic_res)

    def __pd_to_dict_recur(self, df: pd.DataFrame, level: int, results_name) -> dict:
        blockLevel = self.project.block_structure[level]
        dictRet = {}

        if level == len(self.project.block_structure) - 1:
            # Sample level
            # Extract results

            df_results_dict = df.to_dict("records")

            # df_results_dict records :
            # [
            #     {"sampleId": 1, "res1": 1, "res2": 1, ...},
            #     ...
            # ]

            for record in df_results_dict:
                dictRet[record[blockLevel["name"]]] = []
                for resName in results_name:
                    dictRet[record[blockLevel["name"]]].append(record[resName])

        else:
            # Other levels
            dfs = dict(tuple(df.groupby(blockLevel["name"])))

            for key in dfs:
                dictRet[key] = self.__pd_to_dict_recur(
                    dfs[key], level + 1, results_name
                )

        return dictRet

    def add_results_np(self, results: np.array) -> bool:
        """
        Add a result to the model from a np array.
        simply convert it into a df and use the already coded df import function
        """
        col = results[0]
        df = pd.DataFrame(data=results[1:], columns=col)
        self.add_results_df(df)
        return True

    def __checkResultDict(
        self,
        block,
        level: int,
        sampleIndex: int,
        expected_results_order: List[str],
        path: str,
    ):
        """
        Check recursively if a result dict is coherent with the block_structure
        """

        if level == sampleIndex:
            #  Sample level : the results : they need to be verified
            if len(block) != len(expected_results_order):
                raise ValueError(
                    "in : "
                    + path
                    + ", "
                    + str(len(block))
                    + " value where given but "
                    + str(len(expected_results_order))
                    + "where expected"
                )

        else:
            for subBlockKey in block:
                self.__checkResultDict(
                    block[subBlockKey],
                    level + 1,
                    sampleIndex,
                    expected_results_order,
                    path + " / " + str(subBlockKey),
                )
