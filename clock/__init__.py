__version__ = '0.1.0'
__author__ = 'James Thorniley <james.thorniley@gmail.com'
__license__ = 'GPL 3'

import argparse
from typing import Sequence, Optional, Callable

from matplotlib.axes import Axes
from matplotlib import animation
from matplotlib import pyplot as plt
import numpy as np

from . import drawing, models


def save_to_file() -> Optional[str]:
    """Detect whether -o filename has been supplied.

    If the command line option -o filename was supplied
    when the script was invoked, this returns filename
    as a string. Otherwise returns None.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output')

    args = parser.parse_args()
    return args.output


class PendulumAnimation:
    def __init__(self, t: float, color: str,
                 state: Axes, illustration: Axes, zorder: int,
                 model: models.Pendulum, init=[1., 0.]):
        self.model = model
        self.sol = self.model.solve(init, t, 20)
        self.trajectory = drawing.Trajectory(state,
                                             self.sol,
                                             color,
                                             zorder=zorder,
                                             radius=0.05,
                                             n=self.sol.t.shape[0])
        self.pendulum = drawing.Pendulum(illustration, color, zorder)
        self.state_iterator = self.trajectory()

    def update(self):
        try:
            state = next(self.state_iterator)
        except StopIteration:
            # Retstart the animation when we get to the end
            self.state_iterator = self.trajectory()
            state = next(self.state_iterator)
        self.trajectory.set_marker(state)
        self.pendulum.sigma = state[0]


def pendulum():
    """Draw an illustration of the dynamics of a draggy pendulum."""
    bgcolor = "white"
    fig, (state, illustration) = plt.subplots(ncols=2)
    fig.tight_layout(pad=0)
    fig.set_size_inches(6, 3)
    fig.set_facecolor(bgcolor)

    animations = []

    configs = ((0.1, 12*np.pi, '#f086dc'), (0.0, 2*np.pi, '#5cad69'))
    for i, (drag, t, color) in enumerate(configs):
        p = PendulumAnimation(t, color, state, illustration, i,
                              model=models.Pendulum(drag))
        animations.append(p)

    def update(t: float):
        for a in animations:
            a.update()

    ani = animation.FuncAnimation(
        fig, update, animations[0].sol.t, interval=20, blit=False)

    save_file = save_to_file()
    if save_file:
        ani.save_count = (animations[0].sol.t.shape[0])
        ani.save(save_file,
                 writer='imagemagick',
                 fps=50,
                 dpi=150,
                 savefig_kwargs=dict(facecolor=bgcolor))
    plt.show()


def escapement():
    """Draw trajectories from pendulum with escapement."""
    bgcolor = "white"
    fig, (state, illustration) = plt.subplots(ncols=2)
    fig.tight_layout(pad=0)
    fig.set_size_inches(6, 3)
    fig.set_facecolor(bgcolor)

    animations = []

    configs = ((.6, '#f086dc'), (1.2, '#5cad69'))
    for i, (init, color) in enumerate(configs):
        p = PendulumAnimation(24*np.pi, color, state, illustration, i,
                              model=models.PendulumWithEscapement(0.1, 0.3),
                              init=[init, 0.])
        animations.append(p)

    def update(t: float):
        for a in animations:
            a.update()

    ani = animation.FuncAnimation(
        fig, update, animations[0].sol.t, interval=20, blit=False)

    save_file = save_to_file()
    if save_file:
        ani.save_count = (animations[0].sol.t.shape[0])
        ani.save(save_file,
                 writer='imagemagick',
                 fps=50,
                 dpi=150,
                 savefig_kwargs=dict(facecolor=bgcolor))
    plt.show()


def escapement_surface():
    # This import registers the 3D projection, but is otherwise unused.
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import

    import matplotlib.pyplot as plt
    from matplotlib import cm
    from matplotlib.ticker import LinearLocator, FormatStrFormatter
    import numpy as np

    fig = plt.figure()
    ax = fig.gca(projection='3d')

    # Make data.
    Q = 1.0
    sigma = np.linspace(-Q, Q, 500)
    dsigma = np.linspace(-Q, Q, 500)
    sigma, dsigma = np.meshgrid(sigma, dsigma)
    R = np.tanh(5*sigma)*np.exp(-(5*sigma*dsigma - 1)**2)

    # Plot the surface.
    surf = ax.plot_surface(sigma, dsigma, R, cmap=cm.viridis,
                           linewidth=0, antialiased=False)

    # Customize the z axis.
    ax.set_zlim(-1.01, 1.01)
    ax.zaxis.set_major_locator(LinearLocator(10))
    ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

    # Add a color bar which maps values to colors.
    fig.colorbar(surf, shrink=0.5, aspect=5)

    plt.show()
