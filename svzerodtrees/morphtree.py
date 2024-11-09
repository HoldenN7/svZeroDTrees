import numpy as np
from scipy.io import savemat

class MorphTree():

    def __init__(self, parent_order, connectivity, length, diameter, viscosity,
                 remainder, total_elements_created):
        
        self.parent_order = parent_order
        self.connectivity = connectivity
        self.length = length
        self.diameter = diameter
        self.viscosity = viscosity
        self.remainder = remainder
        self.total_elements_created = total_elements_created


    def generate_morphometric_tree(self):
    
        if self.parent_order <= 15:
            N = 30000000
        elif self.parent_order > 11 and self.parent_order <= 13:
            N = 5000000
        elif self.parent_order > 7 and self.parent_order <= 11:
            N = 400000
        else:
            N = 10000
    
        # Calculate initial children and remainders
        children = self.connectivity[:, self.parent_order] + self.remainder[:, self.parent_order]
        self.remainder[:, self.parent_order] = children - np.round(children)
        children = np.round(children).astype(int)
        self.total_elements_created += np.sum(children)
        number_of_children = np.sum(children)

        # Create a sorted list of child orders from smallest to largest
        child_orders = []
        for order in range(1, self.parent_order + 1):
            child_orders.extend([order] * children[order - 1])
        child_orders = np.array(child_orders)

        # Initialize parent and segment arrays
        current_working_elem = 0
        parent_seg_elem = np.zeros((N, 3), dtype=int)
        parent_seg_elem[0, :] = [0, 0, self.parent_order]  # First element setup
        max_elem = 1
        max_seg = 0
        seg_connectivity = np.zeros((N, 3), dtype=int)
        seg_size = np.zeros((N, 3))

        # Handling first element based on the number of children
        if number_of_children < 2:
            print("children for root < 2, stop")
        else:
            for i in range(number_of_children - 1):
                if i < number_of_children - 2:
                    seg_connectivity[max_seg, :] = [i - 1, -1, i + 1]
                else:
                    seg_connectivity[max_seg, :] = [i - 1, -1, -1]
        
                seg_size[max_seg, :] = [self.diameter[self.parent_order - 1] / 2, 
                                        self.length[self.parent_order - 1] / (number_of_children - 1), 
                                        self.parent_order]
                max_seg += 1

        # Reordering child elements if conditions are met
        if child_orders[-1] == self.parent_order and len(child_orders) != 2:
            child_orders = np.concatenate((child_orders[:-3], [child_orders[-1], child_orders[-3], child_orders[-2]]))

        # Add last two child elements to the outlet of the current element
        parent_seg_elem[max_elem:max_elem + 2, :] = [[max_seg, 1, child_orders[-1]], [max_seg, 2, child_orders[-2]]] # editied to 1, 2 instead of 2, 3????
        max_elem += 2
        child_orders = child_orders[:-2]

        # For each remaining child element, add to the interior segment's left side???
        for i in range(len(child_orders)):
            parent_seg_elem[max_elem, :] = [max_seg - i, 2, child_orders[-(i + 1)]]
            max_elem += 1

        current_working_elem += 1

        # create elements and assign to segments for the rest of the elements
        while current_working_elem <= max_elem:
            print("current", current_working_elem)
            print("max", max_elem)
            print(parent_seg_elem) # this seems to be really off
            par_index, side, current_order = parent_seg_elem[current_working_elem]
            #print("parent", par_index)
            #print("side", side)
            #print("current order", current_order)
            first_seg_index = max_seg + 1
            children = self.connectivity[:, current_order] + self.remainder[:, current_order]
            self.remainder[:, current_order] = children - np.round(children)
            children = np.round(children).astype(int)
            self.total_elements_created += children
            number_of_children = np.sum(children)
        
            child_orders = []  
            for order in range(1, self.parent_order + 1):
                child_orders.extend([order] * children[order - 1])
        
            if number_of_children == 0:
                seg_connectivity[par_index, side] = first_seg_index
                seg_connectivity[max_seg, :] = [par_index, 0, 0]
                seg_size[max_seg, :] = [self.diameter[current_order - 1] / 2, self.length[current_order - 1], current_order]
                max_seg += 1

            if number_of_children == 1 and child_orders[0] == 1 and current_order == 1:
                seg_connectivity[par_index, side] = first_seg_index
                seg_connectivity[max_seg:max_seg + 2, :] = [[par_index, -1, first_seg_index + 1], [first_seg_index, 0, 0]]
                seg_size[max_seg:max_seg + 2, :] = [[self.diameter[0] / 2, self.length[0] / 2, 1], [self.diameter[0] / 2, self.length[0] / 2, 1]]
                max_seg += 2
                parent_seg_elem[max_elem] = [first_seg_index, 2, 1]
                max_elem += 1
            elif number_of_children == 1 and child_orders[0] != 1 and current_order != 1:
                seg_connectivity[par_index, side] = first_seg_index
                seg_connectivity[max_seg:max_seg + 2, :] = [[par_index, -1, first_seg_index + 1], [first_seg_index, 0, 0]]
                seg_size[max_seg:max_seg + 2, :] = [[self.diameter[current_order - 1] / 2, self.length[current_order - 1] / 2, current_order],
                                                    [self.diameter[current_order - 1] / 2, self.length[current_order - 1] / 2, current_order]]
                max_seg += 2
                parent_seg_elem[max_elem] = [first_seg_index, 2, child_orders[0]]
                max_elem += 1
            elif number_of_children == 1:
                seg_connectivity[par_index, side] = first_seg_index
                seg_connectivity[max_seg:max_seg + 2, :] = [[par_index, -1, first_seg_index + 1], [first_seg_index, 0, 0]]
                seg_size[max_seg:max_seg + 2, :] = [[self.diameter[current_order - 1] / 2, self.length[current_order - 1] / 2, current_order],
                                        [self.diameter[current_order - 1] / 2, self.length[current_order - 1] / 2, current_order]]
                max_seg += 2
                parent_seg_elem[max_elem] = [first_seg_index, 2, child_orders[0]]
                max_elem += 1

            # Handling case for two or more children
            if number_of_children >= 2:
                seg_size[max_seg:max_seg + number_of_children - 1, :] = np.array([
                    [self.diameter[current_order - 1] / 2, self.length[current_order - 1] / (number_of_children - 1), current_order]
                    for _ in range(number_of_children - 1)
                ])

                if child_orders[-1] == self.parent_order and len(child_orders) != 2:
                    child_orders = np.concatenate((child_orders[:-3], [child_orders[-1], child_orders[-3], child_orders[-2]]))
                
                seg_connectivity[par_index, side] = first_seg_index

                if number_of_children == 2:
                    seg_connectivity[max_seg, :] = [par_index, -1, -1]
                    max_seg += 1
                else:
                    for i in range(number_of_children - 1):
                        if i == 0:
                            seg_connectivity[max_seg] = [par_index, -1, first_seg_index + 1]
                        elif i < number_of_children - 2:
                            seg_connectivity[max_seg] = [first_seg_index + i - 1, -1, first_seg_index + i]
                        else:
                            seg_connectivity[max_seg] = [first_seg_index + i - 1, -1, -1]
                        max_seg += 1

                parent_seg_elem[max_elem:max_elem + 2, :] = [[max_seg, 1, child_orders[-1]], [max_seg, 2, child_orders[-2]]] # editied to 1, 2 instead of 2, 3????
                max_elem += 2

                child_orders = child_orders[:-2]

                for i, child_order in enumerate(reversed(child_orders)): # WHAT!?
                    parent_seg_elem[max_elem] = [max_seg - i, 2, child_order]
                    max_elem += 1
            if(max_seg>100): # this is getting increased infinitely and creating an infinite loop somewhere
                break
            current_working_elem += 1

        print(children)


def testMorphTreeBeta():

    #create the same table from Yang et al.
    rows, cols = (3, 3)
    C = [[0.0 for i in range(cols)] for j in range(rows)]

    C[0][2] = 1.5
    C[0][1] = 2.4
    C[1][2] = 3.4

    diameter = np.array([0.1, 0.2, 0.3])
    length = np.array([.3, .5, .7])
    remainder = np.zeros((10, 10))

    morphTree = MorphTree(connectivity=C, parent_order=9, 
                                  diameter=diameter, length=length, 
                                  viscosity=None, remainder=remainder, 
                                  total_elements_created=0)

    morphTree.generate_morphometric_tree()

def testMorphTreeShinohara():

    conn_matrix = [[0.19, 4.06, 2.48, 1.36, 0, 0, 0, 0, 0, 0],
         [0, 0.12, 1.55, 0.93, 0, 0, 0, 0, 0, 0],
         [0, 0, 0.17, 2.26, 0.31, 0.05, 0.11, 0.13, 0, 0],
         [0, 0, 0, 0.05, 2.0, 0.7, 0.62, 0.42, 0.39, 0],
         [0, 0, 0, 0, 0.18, 1.92, 1.56, 0.85, 0.83, 0.5],
         [0, 0, 0, 0, 0, 0.18, 2.05, 1.15, 1.0, 0.67],
         [0, 0, 0, 0, 0, 0, 0.05, 1.55, 1.06, 0.67],
         [0, 0, 0, 0, 0, 0, 0, 0.08, 1.67, 0.83], 
         [0, 0, 0, 0, 0, 0, 0, 0, 0.06, 1.67],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0.17]]
    
    C = np.array(conn_matrix)
    
    diameter = np.array([0.004, 0.0057, 0.0082, 0.0118, 0.0171, 0.0246, 0.0354, 0.0509, 0.0733, 0.1056])
    length = np.array([0.077, 0.0123, 0.0197, 0.0316, 0.0505, 0.0809, 0.1294, 0.2070, 0.3313, 0.5300])
    remainder = np.zeros((10, 10))
    
    shinoharaTree = MorphTree(connectivity=C, parent_order=9, 
                                  diameter=diameter, length=length, 
                                  viscosity=None, remainder=remainder, 
                                  total_elements_created=0)
    print("gen tree")
    shinoharaTree.generate_morphometric_tree()
    print("DONE!")

#testMorphTree()
testMorphTreeShinohara()