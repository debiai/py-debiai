"""
Debiai Utils Module.

Provides common functions used across various classes.
"""

import numpy as np

DEBIAI_TYPES = ["contexts", "inputs", "groundTruth", "others"]


def _tree_to_array(block_structure, sample_tree):
    """
    Convert a hierarchical sample tree into a flattened 2D numpy array.

    Each row in the array represents a block from the sample tree, concatenated with
    its children's data recursively. This function aggregates data across multiple
    levels of the sample tree, making it suitable for analysis or model training.

    Parameters:
    - block_structure (list): Structure defining how blocks and their attributes are
    organized within the sample tree.
    - sample_tree (list): Hierarchical sample tree, where each element represents a
    block with potential children blocks.

    Returns:
    - numpy.ndarray: 2D numpy array with concatenated data from a block and its
    children within the sample tree.
    """

    if len(sample_tree) == 0:
        return []

    # Add recursively each one of the blocks
    PATCH_SIZE = 700  # Regroup the blocks after each PATCH_SIZE block
    i = 0

    ret = []
    ret_tmp = _get_block_data(block_structure, 0, sample_tree[0])
    for block in sample_tree[1:]:
        i = i + 1
        if i == PATCH_SIZE:
            ret.append(ret_tmp)
            ret_tmp = _get_block_data(block_structure, 0, block)
            i = 0
            continue

        ret_tmp = np.vstack([ret_tmp, _get_block_data(block_structure, 0, block)])

    ret.append(ret_tmp)
    ret_final = ret[0]
    for r in ret[1:]:
        ret_final = np.vstack([ret_final, r])

    return ret_final


def _get_block_data(block_structure, level, block: object):
    """
    Recursively retrieves data from a given block and its children.

    This function supports the `tree_to_array` function by processing individual blocks
    and their hierarchical structure.

    Parameters:
    - block_structure (list): The structure defining block attributes
    across different levels.
    - level (int): The current level in the block structure being processed.
    - block (dict): The block from which to extract data, which may
    include child blocks.

    Returns:
    - numpy.ndarray: A 2D numpy array containing data from the block and its children.
    """

    # Add the block ID
    block_line = np.array([block["name"]])

    # Add the gdt, inputs, ...
    for debiai_type in DEBIAI_TYPES:
        if debiai_type in block_structure[level]:
            for i in range(len(block_structure[level][debiai_type])):
                block_line = np.append(block_line, block[debiai_type][i])

    # Load the children blocks data
    if "childrenInfoList" in block and len(block["childrenInfoList"]) > 0:
        child_data_list = np.array([])
        for child_block in block["childrenInfoList"]:
            child_data = _get_block_data(block_structure, level + 1, child_block)

            if child_data_list.size == 0:
                child_data_list = np.array(child_data)
            else:
                child_data_list = np.vstack([child_data_list, child_data])

        # Merge block data with children
        block_line = np.repeat(
            [block_line], repeats=np.shape(child_data_list)[0], axis=0
        )

        block_line = np.concatenate((block_line, child_data_list), axis=1)
        return block_line
    else:
        return [block_line]
