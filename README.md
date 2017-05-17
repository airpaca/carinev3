# Carine

  
## Données d'entrées

Les rasters en entrée doivent, pour l'instant, être en projection WGS84 avec 
la valeur -999.
Un rééchantillonnage est aussi nécessaire.

Faire un prétraitement sur les rasters :

    gdalwarp -t_srs EPSG:4326 -ts 2500 0 -r bilinear raster_PACA_NO2_20_04_2017_jp0.tif wgs84_ld/raster_PACA_NO2_20_04_2017_jp0.tif

Traitement en série :

    for fn in $( ls raster_PACA_*_??_??_????_j??.tif ); do gdalwarp -t_srs EPSG:4326 -ts 2500 0 -r bilinear ${fn}  wgs84_ld/${fn}; done


## Communication

Transmission des modifications client -> serveur sous la forme d'une requête 
POST :

    {"pol": "NO2", 
     "ech": 0, 
     "modifs": [
        {"delta": 5, 
         "geom": {
            "type": "Point", 
            "coordinates": [5, 45]
        }},
        {"delta": -10, 
         "geom": {
            "type": "Polygon", 
            "coordinates": [[[6, 46], [7, 48], [8, 42], [6, 46]]]
        }}
     ]
    }
    
    