import numpy as np
from Polygon import Vertex
import random
import copy


def initialize_a_fiber():
    l0 = 1
    num_edges = 2  
    edges = []

    Node0 = np.random.uniform(low = 1, high = 1+l0/2, size=2)

    for i in range(num_edges):

        # initialize an edge with a natural length of l0,
        # a random direction, and a random strain between -0.1 and 0.1,

        theta = random.uniform(-np.pi/2, np.pi/2)
        length = random.uniform(l0 -l0/10, l0 +l0/10)
        Node1 = np.add(Node0,
                       [length*np.cos(theta), length*np.sin(theta)])
        edges.append(Edge([Vertex(Node0), Vertex(Node1)],
                          l0 = l0))
        Node0 = copy.deepcopy(Node1)

    # the first node connects to a linker spring; the last node is fixed.
    edges[0].vertices_[0].is_linked_ = True
    edges[-1].vertices_[1].is_fixed_ = True

    return Fiber(edges)

# We will use the Vertex class to represent the vertices of the fiber.

# Currently the fiber only needs two edges, but to make the model more general, 
# we will use an Edge object to represent the edges of the fiber.
# This will also handle the edge (length) stiffnesses and natural lengths.
# Bending stiffnesses will be handled by the Fiber class.

# The linker spring between the polygon and the fiber will also be an Edge,
# so we include an attribute is_linker_

class Edge:
    def __init__(self, vertices, kS = 10, l0 = 1.0):
        self.vertices_ = vertices
        self.kS_ = kS
        self.l0_ = l0
        self.is_linker_ = False
        # edge_vector_: vector from vertices_[0] to vertices_[1]
        # Note: this is NOT normalized!
        self.edge_vector_ = np.zeros(2)
        self.length_ = 0
        self.computeEdgeVectorAndLength()
        return
    
    def computeEdgeVectorAndLength(self):  
        self.edge_vector_ = np.subtract(self.vertices_[1].position_,
                                        self.vertices_[0].position_)
        self.length_ = np.linalg.norm(self.edge_vector_)
        return



class Fiber:
    def __init__(self, edges, kB = 1):
        self.edges_ = edges
        self.kB_ = kB
        return
    def compute_forces(self):
        # First, initialize forces on all vertices to 0. This needs to be in a
        # separate loop because we will then add forces edge-by-edge

        for edge in self.edges_:
            for vertex in edge.vertices_:
                vertex.force_ = np.zeros(2)
                if vertex.is_linked_: vertex.link_force_ = np.zeros(2)

        # Calculate strain forces on the edge vertices.
        for edge in self.edges:
            edge.computeEdgeVectorAndLength()
            # edge_force: kS * strain * unit vector along edge
            edge_force = np.multiply(edge.kS_ * (edge.length_ - edge.l0_) / edge.length_,
                                     edge.edge_vector_)
            # if edge.length_>l0, the 0th vertex should have a force in the direction of the edge vector.
            # if edge.length_<l0, the force is in the opposite direction.
            # Either way, the edge force has the correct sign multiple from the strain.
            edge.vertices_[0].force_ = np.add(edge.vertices_[0].force_, edge_force)
            edge.vertices_[1].force_ = np.subtract(edge.vertices_[1].force_, edge.force_)
        # Check FIRE minimization at this point...
            
        # Calculate bending forces on the edge vertices.
        # Idea: to take two adjacent edges at a time.
        
        # for i in range (len(self.edges)-1): pass
            

        return