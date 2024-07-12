# imports
import numpy as np

class MorphometricTree():
    """
    An implimentation of morphometric trees modeled after Weiguang Yang et al.
    Uses a connectivity matrix and set diameters to generate a tree
    """
    def __init__(self, parent_order=None, conn_matrix=None, length=None, 
                 diameter=None, viscosity=None):

        self.parent_order = parent_order
        self.conn_matrix = np.array(conn_matrix) # a connectivity matrix must be supplied
        self.length = length
        self.diameter = diameter
        self.viscosity = viscosity
    
    def buildMorphTree(self):
        print("building a morph tree\n")
        print(self.conn_matrix)
        print()
        if self.parent_order <= 7: # assign a value of N
            N = 10000
        elif self.parent_order <= 11:
            N = 400000
        elif self.parent_order <= 13:
            N = 5000000
        else:
            N = 30000000

        remainder = np.zeros((self.parent_order+1, self.parent_order+1)) # create blank remainder array

        children = self.conn_matrix[:, self.parent_order] # children of parent order

        remainder[:, self.parent_order] = np.absolute(children - np.round(children)) # make remainder array the absolute value of the remainder

        #print("heyo", children)
        #print
        #print(np.round(children))
        #print()
        #print(remainder)

        children = np.round(children) # rounding children up
        total_elems_created = np.copy(children)
        num_children = int(sum(children))

        # print(children)

        child_orders = []
        i = 0
        while i < self.parent_order: # create the child orders array
            child_orders += ([i]*int(children[i])) 
            i+=1
        #print(child_orders)
        child_orders = np.array(child_orders)
        #print(child_orders, "yay")

        current_elem = 1 # not sure what this block does 
        parent_seg = np.zeros((N, 3))
        parent_seg[0, 2] = self.parent_order
        max_elem = 1

        max_seg = 0 # not sure what this block doesc c 
        seg_connectivity = np.zeros((N, 3))
        seg_size = np.zeros((N, 3))
        
        if num_children < 2:
            raise ValueError("Need at least 2 children on the parent root")
        elif num_children >= 2: # line 88 of jasons code
            i = 0
            while i < num_children-1:
                i += 1

def testMorphTree():

    #create the same table from Yang et al.
    rows, cols = (3, 3)
    C = [[0.0 for i in range(cols)] for j in range(rows)]

    C[0][2] = 1.5
    C[0][1] = 2.4
    C[1][2] = 3.4

    morphTree = MorphometricTree(conn_matrix=C, parent_order=2)

    morphTree.buildMorphTree()

testMorphTree()