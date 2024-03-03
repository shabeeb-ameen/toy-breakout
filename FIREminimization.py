import numpy as np

def calculateForceVelocityProjections(polygon):
    ff = 0
    vv = 0
    power = 0

    for i in range(len(polygon.vertices_)):
        if not polygon.vertices_[i].is_fixed_:
            ff += np.dot(polygon.vertices_[i].force_,polygon.vertices_[i].force_)
            vv += np.dot(polygon.vertices_[i].velocity_,polygon.vertices_[i].velocity_)
            power += np.dot(polygon.vertices_[i].force_,polygon.vertices_[i].velocity_)

    return ff, vv, power

def FIREminimize(polygon):
    # FIRE algorithm parameters
    FIRE_finc = 1.1
    FIRE_fdec = 0.5
    FIRE_acoef0 = 0.1
    FIRE_acoef = 0.1
    FIRE_falpha = 0.99
    FIRE_dtmax = 5e-3
    FIRE_dt = 5e-4
    FIRE_equilibrium_tolerance = 5e-30
    FIRE_equilibrium_count = 0
    FIRE_itermax = 1000000
    FIRE_n_since_positive = 0

    for iter in range(FIRE_itermax):

        # Step 1: Update positions, forces, and velocities. 
        # note that initial velocities are zero (from the initialized Vertex objects)
        
        # Update positions of polygon vertices
        for j in range(len(polygon.vertices_)):
            if not polygon.vertices_[j].is_fixed_:

                polygon.vertices_[j].position_ = np.add(polygon.vertices_[j].position_,
                                                        np.multiply(FIRE_dt,
                                                                    polygon.vertices_[j].velocity_))

        
        # Calculate forces on polygon vertices
        polygon.do_reconnections()
        polygon.compute_forces()

        # Update velocities of polygon vertices
        for j in range(len(polygon.vertices_)):
            if not polygon.vertices_[j].is_fixed_:
                polygon.vertices_[j].velocity_ = np.add(polygon.vertices_[j].velocity_,
                                                        np.multiply(FIRE_dt,
                                                                    polygon.vertices_[j].force_))

        # Step 2: Calculate ff, vv, and power
        ff, vv, power = calculateForceVelocityProjections(polygon)

            
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
            if (FIRE_n_since_positive>5):
                FIRE_dt = min(FIRE_dt*FIRE_finc, FIRE_dtmax)
                FIRE_acoef *= FIRE_falpha
                FIRE_n_since_positive = 0 
            

            force_multiple = np.sqrt(vv/ff)

            for j in range(len(polygon.vertices_)):
                if not polygon.vertices_[j].is_fixed_:
                    polygon.vertices_[j].velocity_ = np.add(np.multiply((1 - FIRE_acoef),
                                                                        polygon.vertices_[j].velocity_),
                                                            np.multiply(force_multiple * FIRE_acoef, 
                                                                        polygon.vertices_[j].force_))
        else:
            FIRE_n_since_positive=0
            FIRE_acoef = FIRE_acoef0
            FIRE_dt *= FIRE_fdec
            for j in range(len(polygon.vertices_)):
                polygon.vertices_[j].velocity_ = [0, 0]

        #logging
        if (iter%10000 == 0):
            print("Iteration ", iter, "ff = ", ff, "vv = ", vv, "power = ", power)
    
    # plot_configuration(polygon, "output.png")
    return