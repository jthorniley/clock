__version__ = '0.1.0'

import numpy as np
from matplotlib import pyplot as plt
from scipy.integrate import solve_ivp


def pendulum(t, y):
    """Simple pendulum model."""

    return np.array([-y[1], y[0]])



def solve_and_plot_pendulum():
    sol = solve_ivp(pendulum, (0, 10), [0, 1])

    plt.plot(sol.t, sol.y.T)
    plt.savefig('image.png')