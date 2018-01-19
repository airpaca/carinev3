#!/usr/bin/env python3.6
# coding: utf-8

"""Configuration."""

import os

# Déclaration de l'aasqa [airpaca, atmoaura]
aasqa = "aura" 
polls=[]
echs_diff=[]
DIR_RASTERS=''
basse_def_url=""
hd_dest=""
# Création automatique des variables selon l'aasqa
if aasqa == "airpaca":
#TODO : a changer
    #profile={'height':299,'width':400,'driver':'GTiff','transform':[1425.6362032714426, 0.0, 229638.54496787317, 0.0, -1427.6076271328982, 5910187.041501439, 0.0, 0.0, 1.0]}
    geom_field = "geom"
    DIR_RASTERS = '/home/airpaca/azur_data_test_carine'
    raster_prefix = 'PACA'
    polls=['NO2','PM10','O3','MULTI']
    echs_diff=[-1,0,1,2]
elif aasqa == "aura":
    profile={'count':1,'height':300,'width':400,'driver':'GTiff','transform':[1425, 0.0, 229638.54496787317, 0.0, -1425, 5910187.041501439]}
    geom_field = "the_geom"
    DIR_RASTERS = '/home/previ/raster_source'
    DIR_RASTERS_GLOB = '/home/previ/raster_source'
    raster_prefix = 'AURA'
    polls=['NO2','PM10','O3','MULTI']
    hd_dest="previ@dmz-previ:/home/previ/geotiff"
    hd_path="/var/www/html/hd/" 
    basse_def_path="/var/www/html/basse_def/" 
    basse_def_val_path="/var/www/html/basse_def/val/" 
    basse_def_url='http://carine3-prod.atmo-aura.fr:8080/basse_def/'
    basse_def_url_val_path='http://carine3-prod.atmo-aura.fr:8080/basse_def/val/'
    echs_diff=[-1,0,1,2]
    launch_smile_prod="http://www.atmo-auvergnerhonealpes.fr/ws/launch_carine_get_data"
    launch_smile_preprod="http://preprod.air-rhonealpes.fr/ws/launch_carine_get_data"
    mylogs="/var/www/html/mylogs.txt"
elif aasqa == "aura_dev":
    profile={'count':1,'height':300,'width':400,'driver':'GTiff','transform':[1425, 0.0, 229638.54496787317, 0.0, -1425, 5910187.041501439]}
    geom_field = "the_geom"
    DIR_RASTERS = '/home/previ/raster_source_dev'
    DIR_RASTERS_GLOB = '/home/previ/raster_source'
    raster_prefix = 'AURA'
    polls=['NO2','PM10','O3','MULTI']
    hd_dest="previ@dmz-previ:/home/previ/geotiff"
    hd_path="/var/www/html/hddev/" 
    basse_def_path="/var/www/html/basse_def_dev/" 
    basse_def_val_path="/var/www/html/basse_def_dev/val/" 
    basse_def_url='http://carine3-preprod.atmo-aura.fr:8080/basse_def_dev/'
    basse_def_url_val_path='http://carine3-preprod.atmo-aura.fr:8080/basse_def_dev/val/'
    echs_diff=[-1,0,1,2]
    launch_smile="http://preprod.air-rhonealpes.fr/ws/launch_carine_get_data"
    mylogs="/var/www/html/mylogs_dev.txt"
NO2 = 1
O3 = 2
PM10 = 3
PM25 = 4
MULTI = 10

POLLUTANTS = [NO2, O3, PM10, PM25, MULTI]
VLS = {NO2: 200, O3: 180, PM10: 50, PM25: 50, MULTI : 90}

ALE= {NO2: 400, PM10: 80, O3: 240, MULTI : 100}
libs_ech=['jm1','jp0','jp1','jp2']
domaines_hd=[
    'CUGdLyon',
    'LaMetro',
    'Montlucon',
    'SEM',
    'Annecy2',
    'Clermont',
    'Moulins',
    'Vichy',
    'Aurillac',
    'LePuy',
]
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
