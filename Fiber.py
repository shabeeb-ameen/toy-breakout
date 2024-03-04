import numpy as np
from Polygon import Vertex
import random

# We will use the Vertex class to denote nodes of the fiber.

# Currently the fiber only needs two edges, but to make the model more general, 
# we will use an Edge object to represent the edges of the fiber.
# This will also handle the edge (length) stiffnesses and natural lengths.
# Bending stiffnesses will be handled by the Fiber class.

# The linker spring between the polygon and the fiber will also be an Edge,
# so we include an attribute is_linker_

class Edge:
    def __init__(self, nodes, kS = 10, l0 = 0.5):
        self.nodes_ = nodes
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
        self.edge_vector_ = np.subtract(self.nodes_[1].position_,
                                        self.nodes_[0].position_)
        self.length_ = np.linalg.norm(self.edge_vector_)
        return

class Fiber:
    def __init__(self, edges, kB = 1):
        self.edges_ = edges
        self.kB_ = kB
        return
    def compute_forces(self):
        # First, initialize forces on all vertices to 0. This needs to happen 
        # in a separate loop because we will then add forces edge-by-edge
        for edge in self.edges_:
            for node in edge.nodes_:
                node.force_ = np.zeros(2)

        # Calculate strain forces on the edge vertices.
        for edge in self.edges_:
            edge.computeEdgeVectorAndLength()
            # edge_force: kS * strain * unit vector along edge
            edge_force = np.multiply(edge.kS_ * (edge.length_ - edge.l0_) / edge.length_,
                                     edge.edge_vector_)
            # if edge.length_>l0, the 0th vertex should have a force in the direction of the edge vector.
            # if edge.length_<l0, the force is in the opposite direction.
            # Either way, the edge force has the correct sign multiple from the strain.
            edge.nodes_[0].force_ = np.add(edge.nodes_[0].force_, edge_force)
            edge.nodes_[1].force_ = np.subtract(edge.nodes_[1].force_, edge_force)
        # Check FIRE minimization at this point...
            
        # Calculate bending forces on the edge vertices.
        # Idea: to take two adjacent edges at a time.
        # for i in range (len(self.edges)-1): pass
        return
    
