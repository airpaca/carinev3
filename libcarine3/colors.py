#!/usr/bin/env python3.6
# coding: utf-8

"""Colors / Scales to plot air quality data."""


from matplotlib.colors import LinearSegmentedColormap


# Echelle de couleur pour matplotlib
aqvl_rgb = {
    'red': (
        (0.000, 0.00, 0.00),
        (0.100, 0.00, 0.00),
        (0.200, 0.60, 0.60),
        (0.300, 1.00, 1.00),
        (0.400, 1.00, 1.00),
        (0.500, 1.00, 1.00),
        (1.000, 0.50, 0.50),
    ),
    'green': (
        (0.000, 0.80, 0.80),
        (0.100, 0.80, 0.80),
        (0.200, 0.90, 0.90),
        (0.300, 1.00, 1.00),
        (0.400, 0.66, 0.66),
        (0.500, 0.00, 0.00),
        (1.000, 0.00, 0.00),
    ),
    'blue': (
        (0.000, 0.66, 0.66),
        (0.100, 0.66, 0.66),
        (0.200, 0.00, 0.00),
        (0.300, 0.00, 0.00),
        (0.400, 0.00, 0.00),
        (0.500, 0.00, 0.00),
        (1.000, 0.00, 0.00),
    )
}
aqvl = LinearSegmentedColormap('pollution', aqvl_rgb)
