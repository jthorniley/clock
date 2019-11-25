__version__ = '0.1.0'
__author__ = 'James Thorniley <james.thorniley@gmail.com'
__license__ = 'GPL 3'

import argparse
from typing import Optional, Sequence

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
    """Animation consisting of a trajectory and a pendulum drawing.

    Solve the model provided and use the results to animate a
    plot showing the pendulum trajectory in state space, and a
    representation of the pendulum swinging.

    The drawing will be added to two existing matplotlib.axes.Axes
    objects (``state`` and ``illustration``).

    Args:
        model: the model to generate data from
        init: starting values for the model variables
        t: length of time to simulate
        state: axes to draw the state space trajectory
        illustration: axes to draw the illustration of the pendulum
        color: color to use for this drawing
        zorder: use this for all objects created
    """
    def __init__(self, model: models.Pendulum, init: Sequence[float], t: float,
                 state: Axes, illustration: Axes, color: str, zorder: int):
        self.model = model
        self.sol = self.model.solve(init, t, 15)
        self.trajectory = drawing.Trajectory(state,
                                             self.sol,
                                             color=color,
                                             zorder=zorder,
                                             radius=0.05,
                                             n=self.sol.t.shape[0])
        self.pendulum = drawing.Pendulum(illustration, color, zorder)
        self.state_iterator = self.trajectory()

    def update(self):
        """Move the animation to the next frame.

        The next state is take from the IVP solution.
        """
        try:
            state = next(self.state_iterator)
        except StopIteration:
            # Retstart the animation when we get to the end
            self.state_iterator = self.trajectory()
            state = next(self.state_iterator)
        self.trajectory.set_marker(state)
        self.pendulum.angle = state[0]


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
        p = PendulumAnimation(model=models.Pendulum(drag),
                              init=[0.0, 1.0],
                              t=t,
                              color=color,
                              state=state,
                              illustration=illustration,
                              zorder=i)
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
                 fps=30,
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
    model = models.PendulumWithEscapement(0.1, 0.25)

    lim = 1.0

    # Plot the escapement force on the state axes, so that
    # it will be overlaid on the trajectory to show where the
    # escapement takes effect
    p = np.linspace(-lim, lim, 500)
    dotp = np.linspace(-lim, lim, 500)
    p, dotp = np.meshgrid(p, dotp)
    escapement = model.escapement(p, dotp)
    state.matshow(escapement,
                  origin='lower',
                  cmap=cm.bwr,
                  extent=(-lim, lim, -lim, lim),
                  alpha=0.8)

    configs = ((.4, '#f086dc'), (.8, '#5cad69'))
    for i, (init, color) in enumerate(configs):
        p = PendulumAnimation(model=model,
                              init=[init, 0.],
                              t=24 * np.pi,
                              state=state,
                              illustration=illustration,
                              color=color,
                              zorder=i + 10)
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
                 fps=30,
                 dpi=150,
                 savefig_kwargs=dict(facecolor=bgcolor))
    plt.show()


def escapement_surface():
    """Plot the escapement force.

    As a surface and as a heat map.
    """

    model = models.PendulumWithEscapement(0.1, 1)
    bgcolor = "white"
    fig = plt.figure()
    fig.set_size_inches(6, 4)
    fig.set_facecolor(bgcolor)
    fig.subplots_adjust(bottom=0.2)
    contour = fig.add_subplot(1, 2, 1)
    surface = fig.add_subplot(1, 2, 2, projection='3d')

    # Make data.
    lim = 1.0
    p = np.linspace(-lim, lim, 500)
    dotp = np.linspace(-lim, lim, 500)
    p, dotp = np.meshgrid(p, dotp)
    escapement = model.escapement(p, dotp)

    # Plot the surface.
    s = surface.plot_surface(p,
                             dotp,
                             escapement,
                             linewidth=1,
                             cmap=cm.bwr,
                             antialiased=True)
    surface.plot_wireframe(p,
                           dotp,
                           escapement,
                           rstride=25,
                           cstride=25,
                           linewidth=0.2,
                           cmap=cm.bwr,
                           antialiased=True)
    surface.grid(False)
    for axis in (surface.xaxis, surface.yaxis, surface.zaxis):
        axis.set_pane_color((1, 1, 1))

    surface.set_xlabel(r'$p$', fontsize='x-large')
    surface.set_ylabel(r'$\dot{p}$', fontsize='x-large')
    surface.set_zlabel(r'$e$', fontsize='x-large')
    surface.tick_params(labelsize='x-large')
    surface.set_xticks([-1, 1])
    surface.set_yticks([-1, 1])
    surface.set_zticks([-1, 1])

    # Plot 2d representation
    contour.matshow(escapement,
                    origin='lower',
                    cmap=cm.bwr,
                    extent=(-lim, lim, -lim, lim))

    contour.set_xlabel(r'$p$', fontsize='x-large')
    contour.set_ylabel(r'$\dot{p}$', fontsize='x-large')
    contour.tick_params(labeltop=False,
                        top=False,
                        labelbottom=True,
                        bottom=True,
                        labelsize='x-large')
    contour.set_xticks([-1, 1])
    contour.set_yticks([-1, 1])

    cbar = fig.colorbar(s,
                        label=r'$e$',
                        ax=(surface, contour),
                        anchor=(0.5, -0.5),
                        aspect=40,
                        ticks=np.linspace(escapement.min(), escapement.max(),
                                          5),
                        orientation='horizontal')
    cbar.ax.tick_params(labelsize='x-large')
    cbar.ax.set_xlabel(r'$e$', fontsize='x-large')

    save_file = save_to_file()
    if save_file:
        plt.savefig(save_file, dpi=150)
    plt.show()
