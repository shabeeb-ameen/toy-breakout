import numpy as np
import matplotlib.pyplot as plt
class Vertex:
    def __init__(self, position):
        self.position_ = np.array(position)
        self.force_ = np.zeros(2)
        self.velocity_ = np.zeros(2)
        return

class Polygon:
    def __init__(self, vertices):
        self.Lth_ = 0.001
        self.vertices_ = vertices 
        self.perimeter_ = None
        self.area_ = None
        self.P0_ = 3.5
        self.A0_ = 1
        self.energy_ = None
        self.stress_ = np.zeros((2,2))
        self.do_reconnections()
        self.compute_perimeter()
        self.compute_area()
        self.compute_forces()
        return
    
    def compute_perimeter(self):
        self.perimeter_ = 0.
        for i in range(len(self.vertices_)):
            self.perimeter_ += np.linalg.norm(
                np.subtract(self.vertices_[i-1].position_,
                            self.vertices_[i].position_))
        return
    
    def compute_area(self):
        self.area_ = 0.
        for i in range(len(self.vertices_)):
            self.area_ += np.cross(self.vertices_[i-1].position_,
                                   self.vertices_[i].position_)
        self.area_ = 0.5*self.area_
        return
    def do_reconnections(self):
        indices_to_remove = []
        for i in range(len(self.vertices_)):
            l_i = np.linalg.norm(
                    np.subtract(self.vertices_[i-1].position_,
                                self.vertices_[i].position_))
            if l_i < self.Lth_:
                indices_to_remove.append(i)

        for i in sorted(indices_to_remove, reverse=True):
            del self.vertices_[i]        
        return

    def compute_forces(self):

        for i in range(len(self.vertices_)):
            
            # initialize forces to zero
            self.vertices_[i].force_ = np.zeros(2)
            # Calculate area and perimeter derivatives.
            A = np.subtract(
                    self.vertices_[i-len(self.vertices_)+1].position_,
                    self.vertices_[i-1].position_)
            del_A_i = np.array([A[1]/2, -A[0]/2])

            n_i_minus_1 = np.subtract(
                    self.vertices_[i].position_,
                    self.vertices_[i-1].position_)
            n_i_minus_1 = np.multiply(
                    1./np.linalg.norm(n_i_minus_1),
                    n_i_minus_1)
            
            n_i = np.subtract(
                    self.vertices_[i-len(self.vertices_)+1].position_,
                    self.vertices_[i].position_)
            n_i = np.multiply(
                    1./np.linalg.norm(n_i),
                    n_i)
            del_P_i = np.subtract(n_i_minus_1, n_i)

            # Calculate the force on the vertex
            self.vertices_[i].force_ = np.add(
                    self.vertices_[i].force_,
                    np.multiply(self.A0_ - self.area_, del_A_i))
            self.vertices_[i].force_ = np.add(
                    self.vertices_[i].force_,
                    np.multiply(self.P0_ - self.perimeter_, del_P_i))

        return
    
    def plot_polygon(self):
        # plot lines between consecutive pairs of vertices
        for i in range(len(self.vertices_)):
            plt.plot([self.vertices_[i-1].position_[0],
                      self.vertices_[i].position_[0]],
                     [self.vertices_[i-1].position_[1],
                      self.vertices_[i].position_[1]],
                     'k')
        return
