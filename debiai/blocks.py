import pandas as pd

class block:
    # Constructor
    def __init__(self, name: str, path: str):
        self.name = name
        self.__path = path + "/" + name
        self.children = []

    def __repr__(self):
        print("Block path %s" % (self.__path))
    
    # Methods

    def add_samples(self, df: pd.DataFrame):
        # TODO
        raise NotImplementedError

