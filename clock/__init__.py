__version__ = '0.1.0'
__author__ = 'James Thorniley <james.thorniley@gmail.com'
__license__ = 'GPL 3'

import argparse
from typing import Optional

from matplotlib import animation, cm, pyplot as plt
from matplotlib.axes import Axes
# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
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
    def __init__(self,
                 t: float,
                 color: str,
                 state: Axes,
                 illustration: Axes,
                 zorder: int,
                 model: models.Pendulum,
                 init=[1., 0.]):
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

    configs = ((0.1, 12 * np.pi, '#f086dc'), (0.0, 2 * np.pi, '#5cad69'))
    for i, (drag, t, color) in enumerate(configs):
        p = PendulumAnimation(t,
                              color,
                              state,
                              illustration,
                              i,
                              model=models.Pendulum(drag))
        animations.append(p)

    def update(t: float):
        for a in animations:
            a.update()

    ani = animation.FuncAnimation(fig,
                                  update,
                                  animations[0].sol.t,
                                  interval=20,
                                  blit=False)

    save_file = save_to_file()
    if save_file:
        ani.save_count = (animations[0].sol.t.shape[0])
        ani.save(save_file,
                 codec='rawvideo',
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
        p = PendulumAnimation(24 * np.pi,
                              color,
                              state,
                              illustration,
                              i,
                              model=models.PendulumWithEscapement(0.1, 0.3),
                              init=[init, 0.])
        animations.append(p)

    def update(t: float):
        for a in animations:
            a.update()

    ani = animation.FuncAnimation(fig,
                                  update,
                                  animations[0].sol.t,
                                  interval=20,
                                  blit=False)

    save_file = save_to_file()
    if save_file:
        ani.save_count = (animations[0].sol.t.shape[0])
        ani.save(save_file,
                 codec='rawvideo',
                 fps=50,
                 dpi=150,
                 savefig_kwargs=dict(facecolor=bgcolor))
    plt.show()


def escapement_surface():
    model = models.PendulumWithEscapement(0.1, 0.3)
    bgcolor = "white"
    fig = plt.figure()
    fig.set_size_inches(6, 4)
    fig.set_facecolor(bgcolor)
    fig.subplots_adjust(bottom=0.2)
    contour = fig.add_subplot(1, 2, 1)
    surface = fig.add_subplot(1, 2, 2, projection='3d')

    # Make data.
    Q = 1.0
    sigma = np.linspace(-Q, Q, 500)
    dsigma = np.linspace(-Q, Q, 500)
    sigma, dsigma = np.meshgrid(sigma, dsigma)
    R = model.escapement(sigma, dsigma)

    # Plot the surface.
    s = surface.plot_surface(sigma,
                             dsigma,
                             R,
                             linewidth=0,
                             cmap=cm.viridis,
                             antialiased=False)
    surface.grid(False)
    for axis in (surface.xaxis, surface.yaxis, surface.zaxis):
        axis.set_pane_color((1, 1, 1))
    contour.contourf(sigma,
                     dsigma,
                     R,
                     levels=np.linspace(R.min(), R.max(), 200))

    surface.set_xlabel(r'$\sigma$')
    surface.set_ylabel(r'$\dot{\sigma}$')
    surface.set_zlabel(r'$e$')
    contour.set_xlabel(r'$\sigma$')
    contour.set_ylabel(r'$\dot{\sigma}$')

    surface.set_xticks(np.linspace(-Q, Q, 3))
    surface.set_yticks(np.linspace(-Q, Q, 3))

    fig.colorbar(
        s,
        label=r'$e$',
        ax=(surface, contour),
        anchor=(0.5, -0.5),
        aspect=40,
        ticks=np.linspace(R.min(), R.max(), 7),
        orientation='horizontal',
    )

    save_file = save_to_file()
    if save_file:
        plt.savefig(save_file, dpi=150)
    plt.show()
