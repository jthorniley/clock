from typing import Any, Sequence

import numpy as np
from scipy.integrate import solve_ivp


class Pendulum:
    """Simulate a simple pendulum by solving the IVP.

    Examples:

        >>> # Create pendulum with drag coefficient
        >>> pendulum = Pendulum(0.1)
        >>> # Calculate the simulation
        >>> sol = pendulum.solve(init=[0., 1.], t=10.0, freq=50.0)
        >>> sol.t.shape  # There are 501 samples (0.02 secs between eachs)
        (501,)
        >>> (np.abs(np.diff(sol.t) - 0.02) < 1e-10).all()
        True
        >>> sol.t[:10]
        array([0.  , 0.02, 0.04, 0.06, 0.08, 0.1 , 0.12, 0.14, 0.16, 0.18])
        >>> sol.y.shape
        (2, 501)
        >>> sol.y[:, :10]
        array([[0.        , 0.01997868, 0.03990946, 0.05978448, 0.07959589,
                0.09933591, 0.11899699, 0.13857267, 0.15805515, 0.17743645],
               [1.        , 0.99780227, 0.99521023, 0.99222569, 0.98885063,
                0.98508718, 0.98093764, 0.97640454, 0.9714905 , 0.9661983 ]])
    """

    def __init__(self, 𝑘: float):
        self.𝑘 = 𝑘

    def __call__(self, t: float, y: Sequence[float]):
        """Derivative of system state.

        The equation is::

            𝜎̈ = -𝜎 - 𝑘𝜎̇

        Where 𝜎 is the angle of the pendulum and 𝜎̇, 𝜎̈ are the
        derivatives.

        Arguments:

            t: The time being solved for (this is not used here)
            y: The input state (an array of 𝜎, 𝜎̇)

        Returns:

            Array giving the derivative (𝜎̇, 𝜎̈)
        """

        𝜎, 𝜎̇ = y
        𝜎̈ = -𝜎 - self.𝑘 * 𝜎̇

        return [𝜎̇, 𝜎̈]

    def solve(self,
              init: Sequence[float],
              t: float = 1.0,
              freq: float = 50.0) -> Any:
        """Evaluate a time series simulation of the pendulum.

        Arguments:

            init: Initial state of the pendulum
            t: Number of seconds to simulate for
            freq: Sampling frequency - evaluate this many
                times per second.

        Returns:

            A solution object as per scipy.integrate.solve_ivp.
            In particular, we have the following fields:

            t (ndarray, shape (n_points,)):
                Time points.

            y (ndarray, shape (n, n_points)):
                Values of the solution at t.
        """

        t_eval = np.linspace(0.0, t, int(np.floor(t*freq+1)))
        return solve_ivp(self, [0.0, t], init, t_eval=t_eval)


class PendulumWithEscapement(Pendulum):
    """Pendulum model with idealised "escapement".

    The escapement gives the pendulum a push at each
    end of the swing, allowing it to continue swinging
    indefinitely (like a clock) even when there is drag.
    """

    def __init__(self, 𝑘: float, 𝑞: float):
        super().__init__(𝑘)
        self.𝑞 = 𝑞

    def __call__(self, t: float, y: Sequence[float]):
        """Calculate derivative.

        The pendulum component of the derivative is unchanged.
        We add an acceleration introduced by the escapement.
        """

        # This calls the base class to get the acceleration
        # due to the pendulum
        𝜎̈_pendulum = super().__call__(t, y)[1]

        # This calculates the additional acceleration provided
        # by the escapement
        𝜎̈_escapement = self.escapement(*y)

        𝜎̈ = 𝜎̈_pendulum + 𝜎̈_escapement
        return [y[1], 𝜎̈]

    def escapement(self, 𝜎, 𝜎̇):
        return self.𝑞 * np.tanh(5*𝜎)*np.exp(-(5*𝜎*𝜎̇ - 1)**2)
