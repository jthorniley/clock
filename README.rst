Oscillator simulations
**********************

.. image:: output/pendulum@2x.gif
    :width: 450px

Blog post explanation
=====================

`Here <https://medium.com/swlh/clocks-and-oscillators-a401dabb08c2?source=friends_link&sk=b1777334c6e1aeb9303fb9ce3a6c7442>`_

Running the code
================

Set up a virtual environment using
`Poetry <https://github.com/sdispater/poetry>`_. If you have not already
installed Poetry, the quick installation is::

    curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python

Tested with Poetry 0.12.17.

To install the virtual environment do::

    poetry install

Run the code with one of the following scripts::

    poetry run pendulum
    poetry run escapement
    poetry run escapement_surface

This are mapped to functions in `<clock/__init__.py>`_.

pendulum
    Displays an animation of a pendulum with and without drag
escapement
    Displays an animation of a pendulum with an escapement, starting
    from two different initial conditions.
escapement_surface
    Displays the function used to model the escapement.

Tests
=====

Run tests with::

    poetry run pytest --doctest-modules

Video gifs
==========

The ``pendulum`` and ``escapement`` scripts can both produce animation
files with the ``-o`` switch. You may need to install ffmpeg to do this.
For example, on Ubuntu, use::

    sudo apt-get install ffmpeg

Convert to a relatively efficient animated gif with this incantation::

    command="pendulum"
    poetry run pendulum -o $command.avi
    ffmpeg  -i $command.avi -filter_complex \
        "[0:v] split [a][b];[a] palettegen=max_colors=16 [p];[b][p] paletteuse" \
        $command.gif

