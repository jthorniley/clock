from typing import Any, Union, Iterable, Text

from matplotlib.lines import Line2D
from matplotlib.patches import Circle, FancyArrow
import matplotlib.axes
import numpy as np


class EqualAspectAxis:
    """Configures axis to be suitable for rendering.

    The output is rendered by creating patches directly.
    To make this look nice, we want a specified set of
    boundaries for the plotting area, an equal aspect
    ratio (so things don't look stretched) and to remove
    the axis labels / lines.
    """
    def __init__(self, ax: matplotlib.axes.Axes):
        ax.axis((-1.5, 1.5, -1.5, 1.5))
        ax.set_aspect('equal')
        ax.set_axis_off()


class Pendulum(EqualAspectAxis):
    """Draws a pendulum onto a matplotlib axis.

    Examples:

        >>> import matplotlib.pyplot as plt
        >>> fig, ax = plt.subplots()
        >>> pendulum = Pendulum(ax)
        >>> pendulum.sigma = 0.1
        >>> # Use plt.show() to display the image

    Arguments:

        ax: Axis to be drawn on
        color:
            Color specification (hex, array etc as
            accepted by matplotlib) for the pendulum.

    """
    def __init__(self,
                 ax: matplotlib.axes.Axes,
                 color: Union[Text, Iterable] = '#f086dc',
                 zorder=1):
        super().__init__(ax)
        self.ax = ax
        self.color = color
        self._sigma = 0.0

        self._bar = Line2D([0], [0], lw=5, color=self.color, zorder=zorder)
        self._weight = Circle(xy=(0, 0),
                              radius=0.2,
                              facecolor=self.color,
                              zorder=zorder)
        self.ax.add_line(self._bar)
        self.ax.add_patch(self._weight)

    @property
    def sigma(self):
        """Angle of the pendulum."""
        return self._sigma

    @sigma.setter
    def sigma(self, value):
        """Set the pendulum angle."""
        self._sigma = value
        vector = np.array([[0, 0], [np.sin(self._sigma),
                                    -np.cos(self._sigma)]])
        vector *= 1.5
        vector[:, 1] += 0.5
        self._bar.set_xdata(vector[:, 0])
        self._bar.set_ydata(vector[:, 1])
        self._weight.set_center(vector[1, :])


class Trajectory(EqualAspectAxis):
    """Draw the state space trajectory of the system.

    This renders a plot of the whole trajectory (as a line
    plot) as well as a current position marker at the
    given time t.

    Example:

        >>> # Obtain a solution object from solve_ivp
        >>> import scipy.integrate
        >>> import matplotlib.pyplot as plt
        >>> solution = scipy.integrate.solve_ivp(lambda t, x: -x, (0, 1), [1, 1], t_eval=np.array([0.0, 0.1, 0.2]))
        >>> fig, ax = plt.subplots()
        >>> trajectory = Trajectory(ax, solution)
        >>> iterator = trajectory()
        >>> # Set the marker to show the next position of the solution
        >>> for pos in iterator:
        ...     print(pos)
        [1. 1.]
        [0.904... 0.904...]
        [0.818... 0.818...]
        >>> # Can now output a plot with plt.show()

    Arguments:

        ax: Axis to draw on
        solution: Trajectory data to plot
        color: Color to use in drawing
        radius: Size of state marker
        zorder: Z order of drawing objects
        n: Number of points in state trajectory to plot
            (default -1 means plot all points)

    """
    def __init__(self,
                 ax: matplotlib.axes.Axes,
                 solution: Any,
                 color: Union[Text, Iterable] = '#f086dc',
                 radius: int = 0.1,
                 zorder: int = 1,
                 n: int = -1):
        super().__init__(ax)
        self.ax = ax
        self.solution = solution
        self.color = color

        # Add arrows to represent axis labels
        xarrow = FancyArrow(-1.31,
                            -1.3,
                            0.3,
                            0,
                            width=0.02,
                            edgecolor='k',
                            facecolor='k')
        ax.text(-0.8,
                -1.3,
                r'$\sigma$',
                fontsize='xx-large',
                verticalalignment='center')
        ax.add_patch(xarrow)

        yarrow = FancyArrow(-1.3,
                            -1.31,
                            0,
                            0.3,
                            width=0.02,
                            edgecolor='k',
                            facecolor='k')
        ax.text(-1.3,
                -0.8,
                r'$\dot{\sigma}$',
                fontsize='xx-large',
                horizontalalignment='center')
        ax.add_patch(yarrow)

        # Add the marker to the axis
        self._marker = Circle(xy=self.solution.y[:, 0],
                              radius=radius,
                              facecolor=color,
                              zorder=zorder)
        ax.add_patch(self._marker)

        y = self.solution.y
        if n == -1:
            n = y.shape[1]
        ax.plot(y[0, :n], y[1, :n], color=color, zorder=zorder, lw=0.5)

    def __call__(self):
        for y in self.solution.y.T:
            yield y

    def set_marker(self, position):
        self._marker.set_center(position)
