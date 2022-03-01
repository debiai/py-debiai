import numpy as np

"""
    debiai_utils : common function for all debiai classes
"""

DEBIAI_TYPES = ["contexts", "inputs", "groundTruth", "others"]


def tree_to_array(block_structure, sample_tree):
    """
        Convert a sample tree to a 2d array
    """

    if len(sample_tree) == 0:
        return []

    # Add recursively each one of the blocks
    PATCH_SIZE = 700  # Regroup the blocks after each PATCH_SIZE block
    i = 0

    ret = []
    ret_tmp = get_block_data(block_structure, 0, sample_tree[0])
    for block in sample_tree[1:]:
        i = i + 1
        if i == PATCH_SIZE:
            ret.append(ret_tmp)
            ret_tmp = get_block_data(block_structure, 0, block)
            i = 0
            continue

        ret_tmp = np.vstack(
            [ret_tmp, get_block_data(block_structure, 0, block)])

    ret.append(ret_tmp)
    ret_final = ret[0]
    for r in ret[1:]:
        ret_final = np.vstack([ret_final, r])

    return ret_final


def get_block_data(block_structure, level, block: object):
    """
        Used by tree_to_array, returns recursively a 2d array with
        a block and his childrens data
    """
    # Add the block ID
    block_line = np.array([block['name']])

    # Add the gdt, inputs, ...
    for debiai_type in DEBIAI_TYPES:
        if debiai_type in block_structure[level]:
            for i in range(len(block_structure[level][debiai_type])):
                block_line = np.append(block_line, block[debiai_type][i])

    # Load the childrens blocks data
    if 'childrenInfoList' in block and len(block['childrenInfoList']) > 0:
        childs_data = np.array([])
        for child_block in block['childrenInfoList']:

            child_data = get_block_data(
                block_structure, level + 1, child_block)

            if childs_data.size == 0:
                childs_data = np.array(child_data)
            else:
                childs_data = np.vstack([childs_data, child_data])

        # Merge block data with childrens
        block_line = np.repeat(
            [block_line], repeats=np.shape(childs_data)[0], axis=0)

        block_line = np.concatenate((block_line, childs_data), axis=1)
        return block_line
    else:
        return [block_line]


def get_inputs_and_gdt_patch(block_structure, sample_tree):
    """
       return from a sample tree a list of inputs and gdt
       used to create tf datasets
    """
    data = tree_to_array(block_structure, sample_tree)

    # Filter the array to keep the inputs & gdt
    inputs = []
    gdt = []

    # TODO can be done faster and cleaner
    for d in data:
        tmp_inputs = []
        tmp_gdt = []
        ind = -1
        for block in block_structure:
            ind += 1
            for debiai_type in DEBIAI_TYPES:
                if debiai_type in block:
                    for column in block[debiai_type]:
                        ind += 1
                        if debiai_type == "inputs":
                            tmp_inputs.append(float(d[ind]))
                        elif debiai_type == "groundTruth":
                            tmp_gdt.append(float(d[ind]))
        inputs.append(tmp_inputs)
        gdt.append(tmp_gdt)

    return inputs, gdt


def get_samples_and_gdt_patch(block_structure, sample_tree):
    """
       return from a sample tree a list of samples and gdt
       used to create tf datasets
    """

    data = tree_to_array(block_structure, sample_tree)

    # Filter the array to keep the samples & gdt
    samples = []
    gdt = []

    # TODO can be done faster and cleaner
    for d in data:
        tmp_samples = {}
        tmp_gdt = []
        ind = -1
        for block in block_structure:
            ind += 1
            tmp_samples[block['name']] = d[ind]
            for debiai_type in DEBIAI_TYPES:
                if debiai_type in block:
                    for column in block[debiai_type]:
                        ind += 1
                        if column['type'] == 'text':
                            tmp_samples[column['name']] = d[ind]
                        else:
                            tmp_samples[column['name']] = float(d[ind])

                        if debiai_type == "groundTruth":
                            if column['type'] == 'text':
                                tmp_gdt.append(d[ind])
                            else:
                                tmp_gdt.append(float(d[ind]))
        samples.append(tmp_samples)
        gdt.append(tmp_gdt)

    return samples, gdt
