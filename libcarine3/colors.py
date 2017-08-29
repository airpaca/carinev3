#!/usr/bin/env python3.6
# coding: utf-8

"""Colors / Scales to plot air quality data."""


from matplotlib.colors import LinearSegmentedColormap
import matplotlib.colors as col
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
colors=[
    '#32B8A3',#0<10
    '#32B8A3',#10<20
    '#5CCB60',#20<30
    '#99E600',#30<40
    '#C3F000',#40<50
    '#FFFF00',#50<60
    '#FFD100',
    '#FFAA00',
    '#FF5E00',
    '#FF0000',
    '#800000'
    ]
#utilitaire pr convertir la le hex en rgb
def to_rgb(ls):
    rgb=[]
    for c in ls:
        r=round(int(('0x'+c[1:3]),16)/255,2)
        g=round(int(('0x'+c[3:5]),16)/255,2)
        b=round(int(('0x'+c[5:7]),16)/255,2)
        rgb.append((r,g,b))
    return rgb

    
def discrete_cmap(cols):
    N=len(cols)
    """create a colormap with N (N<15) discrete colors and register it"""
    # define individual colors as hex values
    cmap3=LinearSegmentedColormap('generic',aqvl_rgb)
    #cmap3 = col.ListedColormap(cols[0:N])
    
    return cmap3
# Echelle de couleur pour matplotlib
aqvl_rgb = {
    'red': (
        (0.000, 0.2, 0.2),
        (0.100, 0.2, 0.2),
        (0.200, 0.36,0.36),
        (0.300, 0.6, 0.6),
        (0.400, 0.76, 0.76),
        (0.500, 1.00, 1.00),
        (0.60 , 1.00, 1.00),
        (0.70 , 1.00,1.00),
        (0.80 , 1.00, 1.00),
        (0.90 , 1.00, 1.00),
        (1.000, 0.50, 0.50),
    ),
    'green': (
        (0.000, 0.72, 0.72),
        (0.100, 0.72, 0.72),
        (0.200, 0.8, 0.8),
        (0.300, 0.9, 0.9),
        (0.400, 0.940, 0.94),
        (0.500, 1.0, 1.00),
        (0.60 , 0.82, 0.820),
        (0.70 , 0.67, 0.670),
        (0.80 , 0.37, 0.370),
        (0.90 , 0.00, 0.00),
        (1.000, 0.00,0.0),
    ),
    'blue': (
        (0.000, 0.64, 0.64),
        (0.100, 0.64, 0.64),
        (0.200, 0.38, 0.38),
        (0.300, 0.00, 0.00),
        (0.400, 0.00, 0.00),
        (0.500, 0.00, 0.00),
        (0.60 , 0.00, 0.00),
        (0.70 , 0.00, 0.00),
        (0.80 , 0.00, 0.00),
        (0.90 , 0.00, 0.00),
        (1.000, 0.00, 0.0),
    )
}
