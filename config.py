#!/usr/bin/env python3.6
# coding: utf-8

"""Configuration."""

import os

# Déclaration de l'aasqa [airpaca, atmoaura]
aasqa = "airpaca" 

# Création automatique des variables selon l'aasqa
if aasqa == "airpaca":
    geom_field = "geom"
    DIR_RASTERS = '/home/airpaca/azur_data_test_carine'
    raster_prefix = 'PACA'
elif aasqa == "atmoaura":
    geom_field = "the_geom"
    DIR_RASTERS = '/home/vjulier/raster_source'
    raster_prefix = 'AURA'
    
NO2 = 1
O3 = 2
PM10 = 3
PM25 = 4
IQA = 10

POLLUTANTS = [NO2, O3, PM10, PM25, IQA]

VLS = {NO2: 200, O3: 180, PM10: 50, PM25: 50}

def from_name(name):
    """Constante from pollutant name."""
    if name == 'NO2':
        return NO2
    elif name == 'O3':
        return O3
    elif name == 'PM10':
        return PM10
    elif name == 'PM25' or name == 'PM2.5':
        return PM25
    elif name == 'IQA':
        return IQA
    return None

# def get_raster_path(daterun, pol, ech, type):
	# """Get path of a specific raster."""

	# prefx = 'm' if ech < 0 else 'p'
	# absech = abs(ech)
	# path = os.path.join(
		# DIR_RASTERS,
		# f'%s' % files_raster)
	# return path
