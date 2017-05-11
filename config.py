#!/usr/bin/env python3.6
# coding: utf-8

"""Configuration."""


import os


DIR_RASTERS = '/home/jv/azur_data/wgs84_ldv2'


def get_raster_path(daterun, pol, ech):
    """Get path of a specific raster."""
    prefx = 'm' if ech < 0 else 'p'
    absech = abs(ech)
    path = os.path.join(
        DIR_RASTERS,
        f'raster_PACA_{pol}_{daterun:%d_%m_%Y}_j{prefx}{absech}.tif')
    return path
