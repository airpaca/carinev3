# Carine

  
## Données d'entrées

Les rasters en entrée doivent, pour l'instant, être en projection WGS84 avec 
la valeur -999.
Un rééchantillonnage est aussi nécessaire.

Faire un prétraitement sur les rasters :

    gdalwarp -t_srs EPSG:4326 -ts 2500 0 -r bilinear raster_PACA_NO2_20_04_2017_jp0.tif wgs84_ld/raster_PACA_NO2_20_04_2017_jp0.tif

Traitement en série :

    for fn in $( ls raster_PACA_*_??_??_????_j??.tif ); do gdalwarp -t_srs EPSG:4326 -ts 2500 0 -r bilinear ${fn}  wgs84_ld/${fn}; done

Configuration de la localisation des rasters dans le fichier `config.py`


## Installation

Clonage du dépôt et installation des dépendances

    git clone airpaca@vmli-cal2:/home/airpaca/git/carinev3.git
    cd carinev3
    python3.6 -m venv .env
    source .env/bin/activate
    pip install -r requirements.txt

Création d'une base vierge

    echo "CREATE DATABASE carinev3" | psql -h<host> -U<user> -d<postgres>

Modification des paramètres de connexion à la base de données
    
    Dans settings.py

Migration dans la base de données

    python manage.py migrate
    
Lancement du serveur de développement

    python manage.py runserver

L'application est disponible à l'adresse [http://localhost:8100](http://localhost:8100).

Si on utilise un serveur distant le, rajouter dans allowed hosts de carinev3/settings.py

    python manage.py runserver host:port
    

## Urls

Index : `/raster/`

Raster sous la forme d'une image : `/raster/img/raster_<pol>_ech<ech>.png`
edit 20-07: nouvelle url : `/raster/img/raster_<id>.png`
=> on passe l'id de l'objet TypeSourceRaster qui contient les infos de polluant / ech / run / type 

Enveloppe du raster : `/raster/bbox/raster_<pol>_ech<ech>.json`
edit 20-07: nouvelle url : `/raster/bbox/raster_<id>.json`
=> pareil, on passe l'id

Liste des modifications : `/raster/modifications/<pol>/ech<ech>/list.json`
    
Enregistrement des modifications (requête `POST`) : `/raster/alter_raster/`

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
    
    
