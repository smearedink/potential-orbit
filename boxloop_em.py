import numpy as np

# Based on C code written by Brett Gladman in the olden days

def orbit(x0, p0, q=0.9, dt=0.001, maxtime=2.*np.pi, record_every=1):
    """
    x0: array for initial position (ie, [x, y])
    p0: array for initial velocity (ie, [xdot, ydot])
     q: asymmetry parameter for potential
    dt: time step (orbital period = 2pi)
    maxtime: total integration time
    record_every: if you want thinned-out data, make this a higher integer

    returns N-column matrix with the following columns:
     0: time
     1: energy
     2: energy error
     3-N: position
    """
    ndegfr = len(x0)
    x = np.array(x0)
    p = np.array(p0)

    # Evaluate the initial energy
    e0 = get_energy(x, p, q)

    time = 0.0
    counter = 0

    time_output = []
    energy_output = []
    energy_err_output = []
    pos_output = []

    while time < maxtime:
        # Output positions and energy error every <record_every> steps
        # May want to change this if time step is changed
        if counter % record_every == 0:
            time_output.append(time/(2.*np.pi))
            energy = get_energy(x, p, q)
            energy_output.append(energy)
            energy_err_output.append((energy-e0)/e0)
            pos_output.append(x)
        x, p = sia4(x, p, time, dt, ndegfr, q)
        time += dt
        counter += 1

    results_arr = [np.array(time_output), np.array(energy_output),\
        np.array(energy_err_output)]
    pos = np.array(pos_output)
    for i in range(ndegfr):
        results_arr.append(pos[:,i])
    results_arr = np.array(results_arr)

    return results_arr.transpose()

def surfsect(esurf=0.5, q=0.9, dt=0.001, dx=0.2, maxtime=2.*np.pi):
    """
    esurf: energy for this surface of section
     q: asymmetry parameter for potential
    dt: time step (orbital period = 2pi)
    dx: size of change in x between each contour of the surface
    maxtime: total integration time

    returns x and xdot coordinates for plotting a surface of section

    NOTE: this could be generalized to more than 2 degrees of freedom, but
     for now ndegfr is set to 2
    """
    ndegfr = 2

    xmax = np.sqrt(np.exp(2.*esurf)-(0.15*0.15))
    xstart = xmax - 0.0000001

    time_output = []
    energy_output = []
    energy_err_output = []
    x_output = []
    xdot_output = []

    while xstart > -xmax:

        x = np.array([xstart, 0.0])
        p = np.array([0.0, np.sqrt(2.*esurf-np.log(0.15*0.15+x[0]*x[0]))])

        lasty = -1.0

        # Evaluate the initial energy
        e0 = get_energy(x, p, q)

        # Reset time to zero
        time = 0.0

        while time < maxtime:
            if p[1] > 0.0 and x[1]*lasty < 0.0:
                time_output.append(time)
                energy = get_energy(x, p, q)
                energy_output.append(energy)
                energy_err_output.append((energy-e0)/e0)
                x_output.append(x[0])
                xdot_output.append(p[0])
            lasty = x[1]
            x, p = sia4(x, p, time, dt, ndegfr, q)
            time += dt

        xstart = xstart - dx
        print "new xstart:", xstart

#        results_arr = [np.array(time_output), np.array(energy_output),\
#            np.array(energy_err_output)]
#        pos = np.array(pos_output)
#        for i in range(ndegfr):
#            results_arr.append(pos[:,i])
#        results_arr = np.array(results_arr)

    results_arr = np.array([np.array(time_output), np.array(energy_output),\
        np.array(energy_err_output), np.array(x_output), np.array(xdot_output)])

    return results_arr.transpose()

# Momentum gradient function
# For any quadratic kinetic energy, unit mass
def gradt(i, p):
    return p[i]

# Potential gradient function
# Return the gradient of the potential
# This routine for logarithmic galactic potential model
def force(i, x, q):
    vo = 1.
    rc = 0.15

    factor = rc*rc + x[0]*x[0] + x[1]*x[1]/(q*q)
    factor = vo*vo/factor
    if i == 0: outforce = -x[0]*factor
    elif i == 1: outforce = -x[1]*factor/(q*q)

    return outforce

# Fourth-order symplectic integration algorithm
# Unlike the C version, this will not advance the system time itself, but
# it will return updated x and p arrays
def sia4(x, p, t, dt, n, q):
    x_out = np.array(x)
    p_out = np.array(p)
    a = np.zeros(5)
    b = np.zeros(5)
    oneth = 1./3.
    a[1] = a[4] = ( 2.0 + pow(2.0,oneth) + pow(2.0,-oneth) )/6.0
    a[2] = a[3] = ( 1.0 - pow(2.0,oneth) - pow(2.0,-oneth) )/6.0
    b[2] = b[4] = 1.0 / (2.0 - pow(2.0,oneth) )
    b[3] = 1.0 / (1.0 - pow(2.0, 2.0*oneth) )

    adt = a[1]*dt

    for i in range(n):
        x_out[i] += adt*gradt(i, p_out)

    t += adt

    for j in range(2, 5):
        bdt = b[j]*dt
        adt = a[j]*dt

        for i in range(n): p_out[i] += bdt*force(i, x_out, q)
        for i in range(n): x_out[i] += adt*gradt(i, p_out)

        t += adt

    return x_out, p_out

# Energy evaluation function
def get_energy(x_vals, p_vals, q):
    kin = 0.5*(p_vals[0]*p_vals[0]+p_vals[1]*p_vals[1])
    pot = 0.5*np.log(0.15*0.15+x_vals[0]*x_vals[0]+x_vals[1]*x_vals[1]/(q*q))
    return kin+pot

