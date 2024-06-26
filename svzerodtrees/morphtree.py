# imports

class MorphometricTree():
    """
    An implimentation of morphometric trees modeled after Weiguang Yang et al.
    Uses a connectivity matrix and set diameters to generate a tree
    """
    def __init__(self, conn_matrix=None):

        self.treeMatrix = []
        self.conn_matrix = conn_matrix # a connectivity matrix must be supplied
    
    def buildMorphTree(self):
        print("building a morph tree\n")

        root = BloodVessel(order=1, location="Root")
        self.treeMatrix.append(root)
        
        rows = len(self.conn_matrix) - 1

        while rows >= 0:
            cols = len(self.conn_matrix) - 1
            while cols >= 0:
                pass
            pass
        
        


class BloodVessel():

    def __init__(self, order, leftChild=None, rightChild=None, location=None):

        self.order = order
        self.leftChild = leftChild
        self.rightChild = rightChild
        self.location = location

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