class MazeGraph(object):
    ''' Class to represent a Graph
        Construction : Using Edges
    '''
    def __init__(self):
        self.edges = {}  # why are edges dictionary?

    def all_edges(self):
        return self.edges

    def neighbors(self, node):
        return self.edges[node]