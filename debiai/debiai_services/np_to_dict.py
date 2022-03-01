import numpy as np

DEBIAI_TYPES = ["contexts", "inputs", "groundTruth", "others"]


def np_to_dict(block_structure: list, samples: np.array, indexMap: dict):
    ret = []

    for sample in samples:
        parent = None
        #  First block exception
        if len(block_structure) > 1:
            for (i, block) in enumerate(ret):
                if block["name"] == sample[indexMap[block_structure[0]["name"]]]:
                    # Block already created
                    parent = ret[i]
                    continue

        if parent is None:
            #  Block not created, creating block
            newBlock = __create_block(
                block_structure[0], sample, indexMap)
            ret.append(newBlock)
            parent = newBlock

        #  Deal with other blocks
        for blockStruct in block_structure[1:]:
            blockNameIndex = indexMap[blockStruct["name"]]

            nextParent = None
            for (i, block) in enumerate(parent["childrenInfoList"]):
                if block["name"] == sample[blockNameIndex]:
                    # Block already created
                    nextParent = block
                    parent = nextParent
                    continue

            if nextParent is None:
                #  Block not created, creating block
                newBlock = __create_block(
                    blockStruct, sample, indexMap)
                parent["childrenInfoList"].append(newBlock)
                parent = newBlock

    return ret


def check_np_array(block_structure: list, samples: np.array):
    indexMap = {}  #  map of the user structure position and there index in the samples

    # Check array compliance
    for block in block_structure:
        if block["name"] not in samples[0]:
            raise ValueError("'" + block["name"] +
                             "' is missing from the given samples")

        indexMap[block["name"]] = np.where(
            samples[0] == block["name"])[0][0]

        for type_ in DEBIAI_TYPES:
            if type_ in block:
                for col in block[type_]:
                    if col["name"] not in samples[0]:
                        raise ValueError("'" + col["name"] + "' " + type_ +
                                         " is missing from the given samples")

                    indexMap[col["name"]] = np.where(
                        samples[0] == col["name"])[0][0]
                    #  TODO check column type
    return indexMap


def __create_block(blockStruct, sample, indexMap):
    newBlock = {
        "name": str(sample[indexMap[blockStruct["name"]]]),
        "childrenInfoList": []
    }

    for type_ in DEBIAI_TYPES:
        if type_ in blockStruct:
            newBlock[type_] = []
            for col in blockStruct[type_]:
                colIndex = indexMap[col["name"]]
                if col['type'] == "text":
                    newBlock[type_].append(
                        sample[colIndex])
                else:
                    newBlock[type_].append(
                        float(sample[colIndex]))
    return newBlock
