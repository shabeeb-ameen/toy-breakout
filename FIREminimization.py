import numpy as np
from Configuration import plot_configuration

def calculateForceVelocityProjections(polygon, fiber):
    ff = 0
    vv = 0
    power = 0
    # Calculate the force and velocity projections on polygon vertices
    for vertex in polygon.vertices_:
        if not vertex.is_fixed_:
            ff += np.dot(vertex.force_,vertex.force_)
            vv += np.dot(vertex.velocity_,vertex.velocity_)
            power += np.dot(vertex.force_,vertex.velocity_)
    
    # Calculate the force and velocity projections on fiber nodes
    for edge in fiber.edges_:
        for node in edge.nodes_:
            if not node.is_fixed_:
                ff += np.dot(node.force_,
                             node.force_)
                vv += np.dot(node.velocity_,
                             node.velocity_)
                power += np.dot(node.force_,
                                node.velocity_)
    return ff, vv, power

def FIREminimize(polygon, fiber):
    # FIRE algorithm parameters
    FIRE_finc = 1.1
    FIRE_fdec = 0.5
    FIRE_acoef0 = 0.1
    FIRE_acoef = 0.1
    FIRE_falpha = 0.99
    FIRE_dtmax = 5e-3
    FIRE_dt = 1e-4
    FIRE_equilibrium_tolerance = 5e-28
    FIRE_equilibrium_count = 0
    FIRE_itermax = 1000000
    FIRE_n_since_positive = 0

    for iter in range(FIRE_itermax):

        # Step 1: Update positions, forces, and velocities. 
        # note that initial velocities are zero (from the initialized Vertex objects)
        
        # Update positions of polygon vertices
        for vertex in polygon.vertices_:
            if not vertex.is_fixed_:
                vertex.position_ = np.add(vertex.position_,
                                          np.multiply(FIRE_dt,
                                                      vertex.velocity_))
        # Update positions of fiber vertices
        for edge in fiber.edges_:
            for node in edge.nodes_:
                if not node.is_fixed_:
                    node.position_ = np.add(node.position_,
                                              np.multiply(FIRE_dt,node.velocity_))
        
        # Calculate forces on polygon vertices
        polygon.do_reconnections()
        polygon.compute_forces()

        # Calculate forces on fiber_vertices
        fiber.compute_forces()

        ################# Maybe we can move this to Configuration.py
        # Calculate addition to force from linker spring

        link_l0 = 0.2
        link_kS = 10
        link_vector = np.subtract(fiber.edges_[0].nodes_[0].position_,
                                  polygon.vertices_[0].position_)
        link_length = np.linalg.norm(link_vector)
        link_force = np.multiply(link_kS * (link_length - link_l0) / link_length,
                                 link_vector)
            # if edge.length_>l0, the 0th vertex should have a force in the direction of the edge vector.
            # if edge.length_<l0, the force is in the opposite direction.
            # Either way, the edge force has the correct sign multiple from the strain.
        polygon.vertices_[0].force_ = np.add(polygon.vertices_[0].force_,
                                             link_force)
        fiber.edges_[0].nodes_[0].force_ = np.subtract(fiber.edges_[0].nodes_[0].force_,
                                                       link_force)
        
        #################




        # Update velocities of polygon vertices
        for vertex in polygon.vertices_:
            if not vertex.is_fixed_:
                vertex.velocity_ = np.add(vertex.velocity_,
                                          np.multiply(FIRE_dt,
                                                      vertex.force_))
                
        # Update velocities of fiber vertices
                
        for edge in fiber.edges_:
            for node in edge.nodes_:
                if not node.is_fixed_:
                    node.velocity_ = np.add(node.velocity_,
                                            np.multiply(FIRE_dt,
                                                        node.force_))
                

            

        # Step 2: Calculate ff, vv, and power
        ff, vv, power = calculateForceVelocityProjections(polygon, fiber)

            
        if (ff<FIRE_equilibrium_tolerance):
            FIRE_equilibrium_count += 1
            if (FIRE_equilibrium_count>1000):
                break
            
        
        
        else: FIRE_equilibrium_count = 0
        

        # Step 3: Check if  power is positive. 

        # If it is:
        # FIRE update the velocities.

        # If it is, and if it has been positive for 5 consecutive iterations:
        # increase the timestep, decrease acoef
        # Reset the counter for the number of iterations since the dot product was positive.

        # If it is not:
        # decrease the timestep, reset acoef and reset the velocities to zero.
        if power>0:
            FIRE_n_since_positive += 1
            if (FIRE_n_since_positive > 5):
                FIRE_dt = min(FIRE_dt * FIRE_finc, FIRE_dtmax)
                FIRE_acoef *= FIRE_falpha
                FIRE_n_since_positive = 0 
            

            force_multiple = np.sqrt(vv/ff)
            # Edit polygon vertex velocities
            for vertex in polygon.vertices_:
                if not vertex.is_fixed_:
                    vertex.velocity_ = np.add(np.multiply((1 - FIRE_acoef),vertex.velocity_),
                                              np.multiply(force_multiple * FIRE_acoef, vertex.force_))
            # Edit fiber node velocities
            for edge in fiber.edges_:
                for node in edge.nodes_:
                    if not node.is_fixed_:
                        node.velocity_ = np.add(np.multiply((1 - FIRE_acoef),node.velocity_),
                                                np.multiply(force_multiple * FIRE_acoef, node.force_))
            
        else:
            FIRE_n_since_positive=0
            FIRE_acoef = FIRE_acoef0
            FIRE_dt *= FIRE_fdec
            for vertex in polygon.vertices_:
                vertex.velocity_ = np.zeros(2)
            for edge in fiber.edges_:
                for node in edge.nodes_:
                    node.velocity_ =np.zeros(2)

        #logging
        if (iter%10000 == 0):
            print("Iteration ", iter, "ff = ", ff, "vv = ", vv, "power = ", power)
            plot_configuration(polygon, fiber, "output/" + str(iter) + ".png")
            for vertex in polygon.vertices_:
                print("     Vertex ", vertex.force_)
            for edge in fiber.edges_:
                for node in edge.nodes_:
                    print("     Node ", node.force_)


    # plot_configuration(polygon, "output.png")
    return