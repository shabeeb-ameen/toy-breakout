import numpy as np

class Node:
    def __init__(self, position):
        self.position_ = np.array(position)
        self.force_ = np.zeros(2)
        self.velocity_ = np.zeros(2)
        self.is_fixed_ = False
        self.is_linked_ = False
        return