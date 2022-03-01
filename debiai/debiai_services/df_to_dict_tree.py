import pandas as pd

DEBIAI_TYPES = ["contexts", "inputs", "groundTruth", "others"]


def df_to_dict_tree(df: pd.DataFrame, block_structure: list):
    col_index_map = {}
    data = df.to_dict('split')
    column = data['columns']

    # find the position of the columns of the block structure in the dataframe
    for block in block_structure:
        if block["name"] not in column:
            raise ValueError("'" + block["name"] +
                             "' is missing from the given samples")

        col_index_map[block["name"]] = column.index(block["name"])

        for type_ in DEBIAI_TYPES:
            if type_ in block:
                for col in block[type_]:
                    if col["name"] not in column:
                        raise ValueError("'" + col["name"] + "' " + type_ +
                                         " is missing from the given samples")

                    col_index_map[col["name"]] = column.index(col["name"])

    # Create a tree json with only the blocks names
    block_tree_dict = {"childrenInfoList": {}}
    for sample in data['data']:
        parent = block_tree_dict
        for (level, block_level) in enumerate(block_structure):
            block_name = sample[col_index_map[block_level["name"]]]
            if block_name not in parent["childrenInfoList"]:
                # Add the block to the dict
                parent["childrenInfoList"][block_name] = __create_block(
                    block_level,
                    sample,
                    col_index_map
                )

                # if level < len(block_structure) - 1:
                # Not the sample
                parent["childrenInfoList"][block_name]["childrenInfoList"] = {}

            parent = parent["childrenInfoList"][block_name]

    # Create the block tree from the dict (temporary)
    block_tree = __block_dict_to_array_tree(-1,
                                            block_tree_dict, block_structure)
    return block_tree['childrenInfoList']


def __create_block(blockLevel: dict, sample: list, col_index_map: dict):
    block = {"name": str(sample[col_index_map[blockLevel["name"]]])}
    for DEBIAI_type in DEBIAI_TYPES:
        if DEBIAI_type in blockLevel:
            block[DEBIAI_type] = []
            for col in blockLevel[DEBIAI_type]:
                block[DEBIAI_type].append(
                    sample[col_index_map[col['name']]])
    return block


def __block_dict_to_array_tree(level, block_dict, block_structure):
    if level == len(block_structure) - 1:
        # Sample level
        return block_dict

    children_info_list = []
    for child_name in block_dict['childrenInfoList']:
        children_info_list.append(__block_dict_to_array_tree(
            level + 1,
            block_dict['childrenInfoList'][child_name],
            block_structure
        ))

    block_dict['childrenInfoList'] = children_info_list
    return block_dict
