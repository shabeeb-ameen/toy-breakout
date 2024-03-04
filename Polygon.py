import numpy as np
import random


# def initialize_a_polygon(P0 = 3.7):
#     num_vertices = random.randint(5, 8)
#     theta = 2 * np.pi / num_vertices
#     vertices = []
#     for i in range(num_vertices):
#         r_vertex = np.sqrt(1/np.pi) + random.uniform(-0.1, 0.1)
#         theta_vertex = i*theta + random.uniform(-0.001, 0.001)
#         x = r_vertex * np.cos(theta_vertex)
#         y = r_vertex * np.sin(theta_vertex)
#         vertices.append(Vertex([x, y]))

#     # the first vertex connects to a linker spring.
#     # Some other vertex, chosen at random, is fixed.
#     vertices[0].is_linked_ = True
#     vertices[random.randint(1, num_vertices-1)].is_fixed_ = True
#     return Polygon(vertices,P0)

class Vertex:
    def __init__(self, position):
        self.position_ = np.array(position)
        self.force_ = np.zeros(2)
        self.velocity_ = np.zeros(2)
        self.is_fixed_ = False
        self.is_linked_ = False

        return

# Link
class Polygon:
    def __init__(self, vertices, P0):
        self.Lth_ = 0.001
        self.vertices_ = vertices
        self.fixed_vertex_index_ = None
        self.linked_vertex_index_ = None
        self.perimeter_ = None
        self.area_ = None
        self.P0_ = P0
        self.A0_ = 1
        self.kA_ = 1
        self.kP_ = 1
        self.energy_ = None
        self.stress_ = np.zeros((2,2))
        self.do_reconnections()
        self.compute_forces()
        self.compute_stress()
        return
    
    def compute_perimeter(self):
        self.perimeter_ = 0.
        for i, vertex in enumerate(self.vertices_):
            self.perimeter_ += np.linalg.norm(
                np.subtract(self.vertices_[i-1].position_,
                            vertex.position_))
        return
    
    def compute_area(self):
        # An interesting note:
        # For 2D vectors, np.cross returns the number only.
        # I guess this is sensible behavior!
        self.area_ = 0.
        for i, vertex in enumerate(self.vertices_):
            self.area_ += np.cross(self.vertices_[i-1].position_,
                                   vertex.position_)
        self.area_ = 0.5 * self.area_
        return
    
    def do_reconnections(self):
        indices_to_remove = []
        for i, vertex in enumerate(self.vertices_):
            l_i = np.linalg.norm(
                    np.subtract(self.vertices_[i-1].position_,
                                vertex.position_))
            if l_i < self.Lth_:
                indices_to_remove.append(i)

        for i in sorted(indices_to_remove, reverse=True):
            del self.vertices_[i]        
        return

    # Calculates forces on polygon vertices using only the polygon geometry
    # This information is stored in vertex.force_
    # For the vertex that is connected to a linker spring, 
    # we will calculate and store the linker force separately (in vertex._link_force_)

    def compute_forces(self):
        # Calculate current area and perimeter
        self.compute_perimeter()
        self.compute_area()

        for i,vertex in enumerate(self.vertices_):  
            # initialize forces to zero
            vertex.force_ = np.zeros(2)
            # Calculate area and perimeter derivatives.
            A = np.subtract(
                    self.vertices_[i-len(self.vertices_)+1].position_,
                    self.vertices_[i-1].position_)
            del_A_i = np.array([A[1]/2, -A[0]/2])

            n_i_minus_1 = np.subtract(vertex.position_,
                                      self.vertices_[i-1].position_)
            n_i_minus_1 = np.multiply(1./np.linalg.norm(n_i_minus_1),
                                      n_i_minus_1)
            
            n_i = np.subtract(self.vertices_[i-len(self.vertices_)+1].position_,
                              vertex.position_)
            n_i = np.multiply(1./np.linalg.norm(n_i),
                              n_i)
            del_P_i = np.subtract(n_i_minus_1, n_i)

            # Calculate the force on the vertex
            vertex.force_ = np.add(vertex.force_,
                                   np.multiply(self.A0_ - self.area_,
                                               self.kA_ * del_A_i))
            vertex.force_ = np.add(vertex.force_,
                                   np.multiply(self.P0_ - self.perimeter_,
                                               del_P_i))
        return
    
    # compute_stress: This calculates the polygon stress based only on the polygon-
    def compute_stress(self):
        self.stress_ = np.zeros((2,2))
        for vertex in self.vertices_:
            self.stress_ = np.add(self.stress_,
                                  np.outer(vertex.position_,
                                           vertex.force_))
        return
