Oscillator simulations
**********************

.. image:: output/pendulum@2x.gif
    :width: 450px

Tests
=====

Run tests with::

    poetry run pytest --doctest-modules

Video gifs
==========

The ``pendulum`` and ``escapement`` scripts can both produce animation
files with the ``-o`` switch. Convert to a relatively efficient animated
gif with ffmpeg like so:

.. code-block::

    filename="pendulum"
    poetry run pendulum -o $filename.avi
    ffmpeg  -i $filename.avi -filter_complex \
        "[0:v] split [a][b];[a] palettegen=max_colors=16 [p];[b][p] paletteuse" \
        $filename.gif
