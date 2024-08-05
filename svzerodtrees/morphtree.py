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

        print("Tree Details")
        print("Parent Order: \n", self.parent_order)
        print("Conn Matrix: \n", self.conn_matrix)
        print("Length: \n", self.length)
        print("Diameter: \n", self.diameter)
        print("Viscosity: \n", self.viscosity)
    
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

        print("N: \n", N)

        remainder = np.zeros((self.parent_order+1, self.parent_order+1)) # create blank remainder array

        print("Remainder Array: \n", remainder)

        children = self.conn_matrix[:, self.parent_order] # children of parent order

        print("Children: \n", children)

        remainder[:, self.parent_order] = children - np.round(children) # make remainder array the absolute value of the remainder

        print("Remainder Array: \n", remainder)

        children = np.round(children) # rounding children up
        
        print("Children: \n", children)

        total_elems_created = np.copy(children)

        print("Total_elems_created: \n", total_elems_created)

        num_children = int(sum(children))

        print("Num_Children: \n", num_children)
        
        child_orders = []
        i = 0
        while i < self.parent_order: # create the child orders array
            child_orders += ([i]*int(children[i])) 
            i+=1
        child_orders = np.array(child_orders)

        print("Child Orders: \n", child_orders)

        current_elem = 1 # not sure what this block does 
        parent_seg = np.zeros((N, 3))
        parent_seg[0, 2] = self.parent_order
        max_elem = 1

        max_seg = 0 # not sure what this block doesc c 
        seg_connectivity = np.zeros((N, 3)) # 
        seg_size = np.zeros((N, 3))
        
        if num_children < 2:
            raise ValueError("Need at least 2 children on the parent root")
        elif num_children >= 2: # line 88 of jasons code
            i = 0
            while i < num_children-1:
                if i<num_children-1:
                    seg_connectivity[max_seg] = np.array([i, -1, i+1])
                else:
                    seg_connectivity[max_seg] = np.array([i, -1, -1])

                #print(seg_connectivity)

                seg_size[max_seg] = np.array([self.diameter[self.parent_order], 
                                                self.length[self.parent_order]/(num_children-1), 
                                                self.parent_order])
                
                #print(seg_size)

                max_seg += 1
                i += 1
        
        if child_orders[-1] == self.parent_order and len(child_orders) != 2:
            child_orders = [child_orders[:-4], child_orders[-1], child_orders[-3:-2]] # reorders things, but never seems to get called lol
        
        #line 110 Jasons Code

        parent_seg[max_elem] = np.array([max_seg, 2, child_orders[-1]])
        parent_seg[max_elem+1] = np.array([max_seg, 3, child_orders[-2]])
        max_elem+=2

        child_orders = child_orders[0:-2]
        
        i = 0
        while i < len(child_orders):
            parent_seg[max_elem+1] = np.array([max_seg-i, 2, child_orders[-1-i]])
            max_elem+=1
            i+=1
        
        current_elem +=1

        while current_elem <= max_elem:
            
            par_index = parent_seg[current_elem, 0]
            side = parent_seg[current_elem, 1]
            current_order = int(parent_seg[current_elem, 2])

            first_seg_index = max_seg+1
            children = np.add(self.conn_matrix[:, current_order], remainder[:, current_order]) # calculate num child
            total_elems_created += children
            num_children = sum(children)

            child_orders = []
            i = 0
            while i < self.parent_order: # create the child orders array
                child_orders += ([i]*int(children[i])) 
                i+=1

            child_orders = np.array(child_orders)
        
            current_elem+=1
            # line 137 MATLAB


def testMorphTree():

    #create the same table from Yang et al.
    rows, cols = (3, 3)
    C = [[0.0 for i in range(cols)] for j in range(rows)]

    C[0][2] = 1.5
    C[0][1] = 2.4
    C[1][2] = 3.4

    diameter = np.array([0.1, 0.2, 0.3])
    length = np.array([.3, .5, .7])

    morphTree = MorphometricTree(conn_matrix=C, parent_order=2, diameter=diameter, length=length)

    morphTree.buildMorphTree()

def testMorphTreeShinohara():

    C = [[0.19, 4.06, 2.48, 1.36, 0, 0, 0, 0, 0, 0],
         [0, 0.12, 1.55, 0.93, 0, 0, 0, 0, 0, 0],
         [0, 0, 0.17, 2.26, 0.31, 0.05, 0.11, 0.13, 0, 0],
         [0, 0, 0, 0.05, 2.0, 0.7, 0.62, 0.42, 0.39, 0],
         [0, 0, 0, 0, 0.18, 1.92, 1.56, 0.85, 0.83, 0.5],
         [0, 0, 0, 0, 0, 0.18, 2.05, 1.15, 1.0, 0.67],
         [0, 0, 0, 0, 0, 0, 0.05, 1.55, 1.06, 0.67],
         [0, 0, 0, 0, 0, 0, 0, 0.08, 1.67, 0.83], 
         [0, 0, 0, 0, 0, 0, 0, 0, 0.06, 1.67],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0.17]]
    
    diameter = np.array([0.004, 0.0057, 0.0082, 0.0118, 0.0171, 0.0246, 0.0354, 0.0509, 0.0733, 0.1056])
    length = np.array([0.077, 0.0123, 0.0197, 0.0316, 0.0505, 0.0809, 0.1294, 0.2070, 0.3313, 0.5300])
    
    shinoharaTree = MorphometricTree(conn_matrix=C, parent_order=9, diameter=diameter, length=length)

    shinoharaTree.buildMorphTree()

#testMorphTree()
testMorphTreeShinohara()