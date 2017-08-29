#!/usr/bin/env python3.6
# coding: utf-8

"""Configuration."""

import os

# Déclaration de l'aasqa [airpaca, atmoaura]
aasqa = "atmoaura" 
polls=[]
echs_diff=[]
DIR_RASTERS=''
# Création automatique des variables selon l'aasqa
if aasqa == "airpaca":
#TODO : a changer
    profile={'height':299,'width':400,'driver':'GTiff','transform':[1425.6362032714426, 0.0, 229638.54496787317, 0.0, -1427.6076271328982, 5910187.041501439, 0.0, 0.0, 1.0]}
    geom_field = "geom"
    DIR_RASTERS = '/home/airpaca/azur_data_test_carine'
    raster_prefix = 'PACA'
    polls=['NO2','PM10','O3']
    echs_diff=[-1,0,1,2]
elif aasqa == "atmoaura":
    profile={'count':1,'height':299,'width':400,'driver':'GTiff','transform':[1425.6362032714426, 0.0, 229638.54496787317, 0.0, -1427.6076271328982, 5910187.041501439]}
    geom_field = "the_geom"
    DIR_RASTERS = '/home/previ/raster_source'
    raster_prefix = 'AURA'
    polls=['NO2','PM10','O3','MULTI']
    echs_diff=[-1,0,1]
NO2 = 1
O3 = 2
PM10 = 3
PM25 = 4
MULTI = 10

POLLUTANTS = [NO2, O3, PM10, PM25, MULTI]
VLS = {NO2: 200, O3: 180, PM10: 50, PM25: 50}

ALE= {NO2: 400, PM10: 80, O3: 240}

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
    elif name == 'MULTI':
        return MULTI
    return None

# def get_raster_path(daterun, pol, ech, type):
	# """Get path of a specific raster."""

	# prefx = 'm' if ech < 0 else 'p'
	# absech = abs(ech)
	# path = os.path.join(
		# DIR_RASTERS,
		# f'%s' % files_raster)
	# return path
