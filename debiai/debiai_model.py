from typing import List
import numpy as np
import pandas as pd
import hashlib

import utils as utils


class Debiai_model:
    """
    A Debiai project model
    """

    def __init__(self, project: 'Debiai_project', name: str, id: str):
        self.project = project
        self.name = name
        self.id = id

    def add_results_dict(self, results: dict, expected_results_order: List[str] = None) -> bool:
        """
        Add a result to the model from a dict.
        The tree allow the user to specify to what sample he created the result
        Each one of the block results structure elements need to be present at
        the end of the tree and in the expected_results_order array.
        """
        # Update the block structure & expected results
        self.project.project_infos()

        if self.project.expected_results is None:
            raise ValueError(
                "The project expected results need to be specified before adding results")

        if type(results) != dict:
            raise ValueError("Results must be of type dict")

        if expected_results_order is not None:
            for expected_result in self.project.expected_results:
                if expected_result["name"] not in expected_results_order:
                    raise ValueError("The expected result '" + expected_result["name"] +
                                     "' is missing from the expected_results_order Array")

            for given_expected_result in expected_results_order:
                result_expected = False
                for expected_result in self.project.expected_results:
                    if given_expected_result == expected_result["name"]:
                        result_expected = True
                if not result_expected:
                    raise ValueError("The given expected result '" + given_expected_result +
                                     "' is not an expected result")
        else:
            expected_results_order = list(map(
                lambda r: r["name"], self.project.expected_results))

        # Start the results verification
        sampleIndex = len(self.project.block_structure) - 1

        for rootBlock in results:
            self.__checkResultDict(
                results[rootBlock], 0, sampleIndex, expected_results_order, str(rootBlock))

        # Upload the results
        return utils.post_model_results_dict(self.project.backend_url, self.project.id, self.id, results, expected_results_order)

    def add_results_df(self, results: pd.DataFrame, map_id=None, use_hash=False) -> dict:
        """
        Add results from a dataFrame depending on use_hash parameter.
        """
        if not use_hash:
            # Add results with __add_results_pd sequentialy
            p_bar = utils.progress_bar(
                'Adding results', results.shape[0], self.name)
            results_added = 0

            chunk_size = 5000
            for start in range(0, results.shape[0], chunk_size):
                results_subset = results.iloc[start:start + chunk_size]

                self.__add_results_pd(results_subset, map_id=map_id)

                results_added = results_added + results_subset.shape[0]
                p_bar.update(results_added)

            return {}
        else:
            dic_results = {}
            length = len(results)

            if 'hash' not in results.columns:
                raise ValueError(
                    "The dataframe does not contain 'hash' expected column.")

            for i in range(length):
                res = []
                for block in self.project.expected_results:
                    if not block["name"] in results.columns:
                        raise ValueError(
                            "The dataframe does not contain '" + block['name'] + "' expected results column.")

                    if block["type"] == "number":
                        res.append(float(results.iloc[i][block["name"]]))
                    else:
                        res.append(results.iloc[i][block["name"]])
                dic_results[results.iloc[i]['hash']] = res

            return self.add_results_hash(dic_results)

    def __add_results_pd(self, results: pd.DataFrame, map_id=None) -> bool:
        """ Add results to the model throught DataFrame """
        if self.project.expected_results is None:
            raise ValueError(
                "The project expected results need to be specified before adding results")

        # Check if block names are in df columns.
        for block in self.project.block_structure:
            if block["name"] not in results.columns and block["name"] != map_id:
                print("'" + block["name"] +
                      "' is missing from the given samples")
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

        # Exctract results name
        results_name = []
        for resu in self.project.expected_results:
            results_name.append(resu["name"])

        # Transform DataFrame into dic recursively
        dic_res = self.__pd_to_dict_recur(results, 0, results_name)

        return self.add_results_dict(dic_res)

    def __pd_to_dict_recur(self, df: pd.DataFrame, level: int, results_name) -> dict:
        blockLevel = self.project.block_structure[level]
        dictRet = {}

        if level == len(self.project.block_structure) - 1:
            # Sample level
            # Exctract results

            df_results_dict = df.to_dict('records')

            # df_results_dict records :
            # [
            #     {"sampleId": 1, "res1": 1, "res2": 1, ...},
            #     ...
            # ]

            for record in df_results_dict:
                dictRet[record[blockLevel['name']]] = []
                for resName in results_name:
                    dictRet[record[blockLevel['name']]].append(
                        record[resName])

        else:
            # Other levels
            dfs = dict(tuple(df.groupby(blockLevel['name'])))

            for key in dfs:
                dictRet[key] = self.__pd_to_dict_recur(
                    dfs[key], level + 1, results_name)

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

    def __checkResultDict(self, block, level: int, sampleIndex: int, expected_results_order: List[str], path: str):
        """
        Check recursively if a result dict is coherent with the block_structure
        """

        if level == sampleIndex:
            #  Sample level : the results : they need to be verified
            if len(block) != len(expected_results_order):
                raise ValueError("in : " + path + ", " +
                                 str(len(block)) + " value where given but " + str(len(expected_results_order)) + "where expected")

        else:
            for subBlockKey in block:
                self.__checkResultDict(
                    block[subBlockKey],
                    level + 1,
                    sampleIndex,
                    expected_results_order,
                    path + " / " + str(subBlockKey)
                )

    def add_results_hash(self, results: dict, expected_results_order: List[str] = []) -> dict:
        """
        Add results from a dict oh hash:results
        """
        if self.project.expected_results is None:
            raise ValueError(
                "The project expected results need to be specified before adding results")

        # Get wrong hash
        hash_list = []

        for key in results:
            hash_list.append(key)

        wrong_hash = utils.check_hash_exist(
            self.project.backend_url, self.project.id, hash_list)

        # Add expected results order
        if expected_results_order != []:
            for dic in results:
                new_results = []
                for block in self.project.expected_results:
                    new_results.append(
                        results[dic][expected_results_order.index(block["name"])])
                results[dic] = new_results

        # Remove wrong hash from the dico and add them to false dic to return
        wrong_values = {}

        for key in wrong_hash:
            wrong_values[key] = results.pop(key)

        # Push new results in backend
        err = utils.post_results_hash(
            self.project.backend_url, self.project.id, self.id, results)

        return wrong_values
