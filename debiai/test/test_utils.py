# -*- coding: utf-8 -*-
"""
    DEBIAI Tests Utils - Functions used for tests

    Author : Quentin Le Helloco
"""


# IMPORT
import sys
import os
import json
import numpy as np
import pandas as pd
from filecmp import dircmp

# Compare files functions

def compare_info(f1, f2) -> bool:
    # Ignored
    ignored = ['creationDate','updateDate']

    if (os.path.isfile(f1) ^ os.path.isfile(f2)):
        #print("One of both file doesn't exist ! :" + f1 + " or " + f2)
        return False

    with open(f1) as json_file1:
        data1 = json.load(json_file1)

    with open(f2) as json_file2:
        data2 = json.load(json_file2)

    bigdata = data1
    smalldata = data2
    if len(data2) > len(data1):
        bigdata = data2
        smalldata = data1

    for key in bigdata:
        if key in ignored:
            continue
        if key not in smalldata:
            #print(key + " is not in both info.json")
            return False
        if bigdata[key] != smalldata[key]:
            #print(key + " is not equal")
            return False
    return True

def req_isequal_samples(dcmp, path1, path2):
    if dcmp.left_only != [] or dcmp.right_only != []:
        #for d in dcmp.left_only:
            #print(d + " is not supposed to exist")
       
        #for d in dcmp.right_only:
            #print(d + " is not supposed to exist")
        return False

    for d in dcmp.common_files:
        if not compare_info(path1 + d, path2 + d):
            return False

    for sub in dcmp.common_dirs:
        if not req_isequal_samples(dcmp.subdirs[sub], path1 + str(sub) + "/", path2 + str(sub) + "/"):
            return False

    return True

def isequal_samples(p1: str, p2: str) -> bool:
    """ Check that samples are sames by checking both path p1 and p2 """

    dcmp = dircmp(p1, p2)
    return req_isequal_samples(dcmp, p1, p2)

# Get tests input fuctions

def get_obj_from_json(path) -> list:
    res = []

    with open(path) as json_file:
            data = json.load(json_file)

    for blocks in data:
        res.append(data[blocks])

    return res

def get_raw_json(path):
    with open(path) as json_file:
        data = json.load(json_file)
    return data

def get_np_from_csv(path) -> np.array:
    return np.genfromtxt(path,delimiter=',',dtype=None, encoding="utf-8")