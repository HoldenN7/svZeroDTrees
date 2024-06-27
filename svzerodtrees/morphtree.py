# imports

class MorphometricTree():
    """
    An implimentation of morphometric trees modeled after Weiguang Yang et al.
    Uses a connectivity matrix and set diameters to generate a tree
    """
    def __init__(self, conn_matrix=None):

        self.conn_matrix = conn_matrix # a connectivity matrix must be supplied
    
    def buildMorphTree(self):
        print("building a morph tree\n")
        self.morph_tree_matrix = []

        root = MorphTreeVessel(order=len(self.conn_matrix) - 1, location="Root") # create root vessel of order/id 1
        self.morph_tree_matrix.append(root) # add vessel to the "tree"

        # This loop traverses conn_matrix starting at the top right corner
        # and going down the rows, then going through the cols right-left
        cols = len(self.conn_matrix[0]) - 1
        while cols >= 0:
            
            rows = 0

            while rows <= (len(self.conn_matrix) - 1):
                
                if self.conn_matrix[rows][cols] == 1:
                    child_elem = MorphTreeVessel(order=rows, location="Midpoint")
                    self.morph_tree_matrix.append(child_elem)
                elif self.conn_matrix[rows][cols] == 2:
                    child_elem_left = MorphTreeVessel(order=rows, location="End")
                    child_elem_right = MorphTreeVessel(order=rows, location="End")

                rows += 1


            cols -= 1
        
        
class MorphTreeVessel():

    def __init__(self, order, leftChild=None, middleChild=None, rightChild=None, location=None):

        self.order = order
        self.leftChild = leftChild
        self.middleChild = middleChild
        self.rightChild = rightChild # keep track of the branching children of vessels
        self.location = location # I think I need this variable. Distinguishes the root of the tree from
        # vessels that either bisect a vessels to bifuricate at the end

def testMorphTree():

    #create the same table from Yang et al.
    rows, cols = (3, 3)
    C = [[0.0 for i in range(cols)] for j in range(rows)]

    C[0][2] = 1
    C[0][1] = 2.4
    C[1][2] = 3

    morphTree = MorphometricTree(conn_matrix=C)

    morphTree.buildMorphTree()

testMorphTree()