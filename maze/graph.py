class Graph:
    def __init__(self):
        self.edges = {}
        self.parents = {}
    
    def addEdge(self, nodeA: tuple, nodeB: tuple):
        if nodeA not in self.edges:
            self.edges[nodeA] = set()

        if nodeB not in self.edges:
            self.edges[nodeB] = set()

        self.edges[nodeA].add(nodeB)
        self.edges[nodeB].add(nodeA)
        
    def getEdges(self, node: tuple):
        return self.edges.get(node, set())

    def makeParent(self, node: tuple, parent: tuple):
        if node not in self.parents:
            self.parents[node] = node

        rootOfNode = self.root(node)

        if rootOfNode not in self.parents:
            self.parents[rootOfNode] = None
        if parent not in self.edges:
            self.parents[parent] = None
            

        self.parents[rootOfNode] = parent

    def root(self, node: tuple):
        if node == None:
            raise Exception("Somehow node is freakin' None")
        nodeParent = self.parents.get(node, node)
        if nodeParent == node:
            return node
        else:
            return self.root(nodeParent)

    def sharedRoot(self, node: tuple, other: tuple):
        return self.root(node) == self.root(other)
