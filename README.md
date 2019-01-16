# Contenu

Clônage / paramétrage de l'appli :
- 1 : création de l'environnement et clônage du dépôt
- 2 : création de la base Postgres/Postgis
- 3 : initialisation des paramètres
- 4 : gérer les clés ssh pour l'export des fichiers
- 5 : test du serveur de dev python

Déploiement :
- 6 : configuration apache / mod-wsgi
- 7 : collecte des fichiers statiques

Mise en place des flux de données quotidiens en entrée
- 8 : incron sur les fichier récpetionnés de mod
- 9 : cron pour archivage et purge automatique

Validation (en plus des tests de fonctionnements évidents):
- 10 : disponiblité des images sur le serveur de tuiles
- 11 : disponibilité des données SMILE (endpoints : commentaire / indices_com / basse_def)

Erreurs déjà rencontrées

## Installation

1- création de l'environnement et clônage du dépôt


    git clone https://github.com/airpaca/carinev3
    cd carinev3
    python3.6 -m venv .env
    source .env/bin/activate
    pip3.6 install -r requirements.txt


  remarque : c'est une bonne pratique d'utiliser un venv pour éviter les conflits avec d'autres lib de l'install système, mais on ne l'a pas testé chez Aura, ça tourne chez nous sur l'install système. La config apache / wsgi pour le déploiement sera je crois légèrement différente.
  
2- création de la base Postgres/Postgis

Création d'une base vierge

    CREATE USER xxx WITH PASSWORD 'xxx';
    CREATE DATABASE carinev3;
    GRANT ALL PRIVILEGES ON DATABASE carinev3 TO xxx;

Création d'un fichier logins.py à la racine avec les paramètres de connexion à la base de données

    #!/usr/bin/env python3
    # coding: utf-8
    db_prod={
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': 'xxx',
            'USER': 'xxx',
            'PASSWORD': 'xxx',
            'HOST': 'localhost', #possibilité d'utiliser une base distante
        }
    }


Editer postgresql.conf : 

    Listen_adresses = ‘*’ au lieu de ‘localhost’ 

Editer pg_hba.conf (/var/lib/pgsql/) 

    => ajouter les réseaux internes et changer la méthode d’identification ident => password 

Migration dans la base de données
 => makemigrations lit le model.py et crée les commandes sql qui utilisées pour générer la structure de la base (accessibles dans /raster/migrations)
 => migrate execute ces commandes et crée la base
 
    python3.6 manage.py makemigrations
    python3.6 manage.py migrate


3 - initialisation des paramètres : 
    - python3.6 manage.py shell et import add_sources.py pour l'initialisation générique
    - /admin pour la partie spécifique à chaque install (=création de contextes : répertoires de données, machines distantes, etc..)

4 - Lancement du serveur de développement

    python3.6 manage.py runserver nom_domaine_ou_ip:numport

L'application est disponible à l'adresse http://nom_domaine_ou_ip:numport.

Si on utilise un serveur distant le, rajouter dans allowed hosts de carinev3/settings.py

    python manage.py runserver host:port
    
    
Erreurs déjà rencontrées :

    - 1  : Si carine renvoie une erreur lors de l’édition des géométries : vérifier que postgis est bien installé.. 
    - 2  : En passant de la version 3.5 à la version 3.6.2 de geos, une erreur est apparue : la regex de django qui détecte la version de geos ne fonctionne plus, il faut l’éditer dans le fichier ou repasser à la version antérieure (qui fonctionne bien). Extrait de stackoverflow : 
    "
    The error says: 
    GEOSException: Could not parse version info string "3.4.2-CAPI-1.8.2 r3921" 
    And the geos_version_info warns: 
    Regular expression should be able to parse version strings such as '3.0.0rc4-CAPI-1.3.3', '3.0.0-CAPI-1.4.1' or '3.4.0dev-CAPI-1.8.0' 
    Edit this file: site-packages/django/contrib/gis/geos/libgeos.py 
    Look for the function: geos_version_info 
    And change this line: 
    ver = geos_version().decode() 
    With this line: 
    ver = geos_version().decode().split(' ')[0] 
    "
    - 3 : sur centos : 
    Disable SElinux (sinon il n’arrive pas à charger certaines libs comme geos ou gdal) 
    Disable firewalld 

    - 4 : attention aux versions de Matplotlib, la (les) version 2 renvoie parfois des erreurs sur l'import de tkinter.
    => le passage en version règle semble-t-il le problème 




