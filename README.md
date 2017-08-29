# Carine

  
## Données d'entrées

Les rasters en entrée doivent, pour l'instant, être en projection 3857
Un rééchantillonnage est aussi nécessaire pour l'affichage dans carine(chez AURA : taille de pixel temporairement fixée à 71.25 en 3857 en attendant de gérer le bug (memory leak de mpl, j'ai perdu la ref du tcket) ).

Faire un prétraitement sur les rasters (à modif pour le 3857) :
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

Création d'un fichier logins.py à la racine avec les paramètres de connexion à la base de données

    host = "..."
    dbname = "..."
    user = "..."
    password = "..."
     
  
Modification des paramètres utilisateur 
    
    Dans settings.py

Migration dans la base de données

    python manage.py migrate
    
Lancement du serveur de développement

    python manage.py runserver

L'application est disponible à l'adresse [http://localhost:8100](http://localhost:8100).

Si on utilise un serveur distant le, rajouter dans allowed hosts de carinev3/settings.py

    python manage.py runserver host:port
    
# uPDATE EN PHASE DE DEV:
    - a chaque acces a /raster :
        - carine initialise les instances de prev pour la journée aucune n'existe
    - DONC : si carine n'a pas été lancé certains jours (we par exemeple), besoin de lancer ça manuellement :
        => /raster/init_today_<id_des_jours_a_initialiser>
        avec :
            - hier = 1
            - avant-hier = 2
            - ...
        #check TODO list

    
## Urls

Index : `/raster/`

Raster sous la forme d'une image : `url : `/raster/img/raster_<id>.png`
=> on passe l'id de l'objet TypeSourceRaster qui contient les infos de polluant / ech / run / type 

Enveloppe du raster : `nouvelle url : `/raster/bbox/raster_<id>.json`
=> pareil, on passe l'id

#TODO => url modifiée
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
    
    