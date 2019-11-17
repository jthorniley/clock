__version__ = '0.1.0'
__author__ = 'James Thorniley <james.thorniley@gmail.com'
__license__ = 'GPL 3'

import argparse
from typing import Sequence, Optional

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
    def __init__(self, drag: float, t: float, color: str,
                 state: Axes, illustration: Axes, zorder: int):
        self.model = models.Pendulum(drag)
        self.sol = self.model.solve([1., 0.], t, 20)
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
    bgcolor = "#e9f2cb"
    fig, (state, illustration) = plt.subplots(ncols=2)
    fig.tight_layout(pad=0)
    fig.set_size_inches(6, 3)
    fig.set_facecolor(bgcolor)

    animations = []

    configs = ((0.1, 12*np.pi, '#f086dc'), (0.0, 2*np.pi, 'black'))
    for i, (drag, t, color) in enumerate(configs):
        p = PendulumAnimation(drag, t, color, state, illustration, i)
        animations.append(p)

    def update(t: float):
        for a in animations:
            a.update()

    ani = animation.FuncAnimation(fig, update, animations[0].sol.t, interval=20, blit=False)

    save_file = save_to_file()
    if save_file:
        ani.save_count = (animations[0].sol.t.shape[0])
        ani.save(save_file,
                 writer='imagemagick',
                 fps=50,
                 dpi=150,
                 savefig_kwargs=dict(facecolor=bgcolor))
    plt.show()
