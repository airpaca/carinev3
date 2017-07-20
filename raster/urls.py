from django.conf.urls import url
from . import views


urlpatterns = [

    # Index
    url(r'^$', views.index, name='index'),

    # Dynamic javascript application
    url(r'^application.map.js$', views.application_js, name='application_js'),

    # Url to POST modification
    url(r'^alter_raster/$', views.alter_raster, name='alter_raster'),

    # Url to GET a list of modifications
    # .. modifications/<pol>/ech<ech>/list.json
    url(r'^modifications/(?P<pol>[a-zA-Z0-9]+)/ech(?P<ech>-?[0-9]+)/list.json$',
        views.list_modifications, name='list_modifications'),

    # Raster as an image (to Leaflet)
    # .. img/raster_<pol>_ech<ech>.png
    url(r'^img/raster_(?P<id>[0-9]+).png$',
        views.img_raster, name='img_raster'),

    # Bounding box of the raster (JSON)
    # .. bbox/raster_<pol>_ech<ech>.json
    url(r'^bbox/raster_(?P<id>[0-9]+).json$',
        views.bbox_raster, name='bbox_raster'),
    
    
    #couches vecteurs
       
    url(r'^sites_fixes.json$',
        views.sites_fixes, name='sites_fixes'),

    url(r'^reg_aura$',
        views.reg_aura, name='reg_aura'),
    url(r'^epci_aura$',
        views.epci_aura, name='epci_aura'),

    #appelé au chargement de l'appli pour initialiser les couches
    url(r'^source_url$',
        views.source_url, name='source_url'),

    url(r'^check_statut$',
        views.check_statut, name='check_statut'),

]
