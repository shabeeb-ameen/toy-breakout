import numpy as np
from FIREminimization import calculateForceVelocityProjections
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

def plot_configuration(polygon, filename = "initial.png"):
    fig, ax = plt.subplots(figsize=(10,10))
    for i in range(len(polygon.vertices_)):
        # ax.plot(P.vertices_[i].position_,P.vertices_[i-1].position_,color='black')
        ax.plot(polygon.vertices_[i].position_[0],polygon.vertices_[i].position_[1],'o',color='black')
        # Only draw the force if it is not if it is not too small
        if np.linalg.norm(polygon.vertices_[i].force_) > 1e-15:
            ForceArrow = FancyArrowPatch(posA = polygon.vertices_[i].position_,
                                    posB = np.add(polygon.vertices_[i].position_,polygon.vertices_[i].force_),
                                    arrowstyle='->,head_width=5,head_length=10',
                                    color='blue', linewidth=2)
            ax.add_patch(ForceArrow)
        EdgeArrow = FancyArrowPatch(posA = polygon.vertices_[i].position_,
                                posB = polygon.vertices_[i-1].position_,
                                arrowstyle='-',
                                color='black', linewidth=2)

        ax.add_patch(EdgeArrow)
        


        # ax.add_patch(arrow)
    plt.xlim(-2, 2)
    plt.ylim(-2, 2)
    plt.savefig(filename)
    plt.close()

    return
# overdamped dynamics: 
#   calculate NET forces on each vertex
#   set v = mu * F
#   r=r0+v*dt
#   repeat until velocities are 0.

def overdampedDynamics(polygon):
    dt = 1e-4
    mu = 1e-2
    itermax = int(1e6)
    equilibrium_tolerance = 1e-30
    print("Calculating an overdamped trajectory for the polygon")
    for iter in range(itermax):

        # Step 1: Update positions, forces, and velocities. 
        # note that initial velocities are zero (from the initialized Vertex objects)
        
        # Update positions of polygon vertices
        for j in range(len(polygon.vertices_)):
            if not polygon.vertices_[j].is_fixed_:
                polygon.vertices_[j].position_ = np.add(polygon.vertices_[j].position_,
                                                        np.multiply(dt,
                                                                    polygon.vertices_[j].velocity_))

        
        # Calculate forces on polygon vertices
        polygon.do_reconnections()
        polygon.compute_forces()

        # Update velocities of polygon vertices
        for j in range(len(polygon.vertices_)):
            if not polygon.vertices_[j].is_fixed_:
                polygon.vertices_[j].velocity_ = np.add(polygon.vertices_[j].velocity_,
                                                        np.multiply(mu * dt,
                                                                    polygon.vertices_[j].force_))
            
        _,vv,_ = calculateForceVelocityProjections(polygon)

        if iter%int(1e3) == 0:
            print(iter, vv)
            plot_configuration(polygon,"{}.png".format(iter))
        if vv<equilibrium_tolerance:
            print("Equilibrium configuration found!")
            break






