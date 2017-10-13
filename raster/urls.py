from django.conf.urls import url
from . import views
import django.contrib.auth 
from django.contrib.auth import views as auth_views


urlpatterns = [
    #default login
    url(r'accounts/login/$', auth_views.LoginView.as_view(),name='login'),
    # Index
    url(r'^$', views.index, name='index'),

    # Dynamic javascript application
    url(r'^application.map.js$', views.application_js, name='application_js'),
    
    # Url to check les sources a diffuser (Prev.source)
    url(r'^get_init_info$', views.get_init_info, name='get_init_info'),
    
    # Url to init appli (Previ(date)    
    url(r'^init_today_(?P<run>[0-2]+)$', views.init_today, name='init_today'),
    
    # Url to check les sources a diffuser (Prev.source)
    url(r'^check_sources$', views.check_sources, name='check_sources'),
    
    # Url to POST modification
    url(r'^alter_raster/$', views.alter_raster, name='alter_raster'),
    url(r'^test_ajax$', views.test_ajax, name='test_ajax'),
    # Url to GET a list of modifications
    # .. modifications/<pol>/ech<ech>/list.json
    #url(r'^modifications/(?P<id>[0-9]+)/list.json$',
    #    views.list_modifications, name='list_modifications'),

    
    # Raster info
    # .. info/raster_<pol>_ech<ech>.png
    url(r'^info/raster_(?P<id>[0-9]+).png$',
        views.info_raster, name='info_raster'),
    # Raster as an image (to Leaflet)
    # .. img/raster_<pol>_ech<ech>.png
    url(r'^img/raster_(?P<id>[0-9]+).png$',
        views.img_raster, name='img_raster'),

    # .. img/raster_ech<ech>.png => multi polluant
    url(r'^img/raster_multi_(?P<ech>[0-4]+).png$',
        views.img_multi, name='img_multi'),
    # Bounding box of the raster (JSON)
    # .. bbox/raster_<pol>_ech<ech>.json
    url(r'^bbox/raster_(?P<id>[0-9]+).json$',
        views.bbox_raster, name='bbox_raster'),
    
    #get_pixel(id,x,y)
    url(r'^api/pixel_(?P<id>[0-9]+)_(?P<x>[0-9]+)_(?P<y>[0-9]+)$',
        views.get_pixel, name='get_pixel'),   
    #sources
    url(r'^source/update$',
        views.update_source, name='update_source'),

    ###couches vecteurs    
    url(r'^sites_fixes.json$',
        views.sites_fixes, name='sites_fixes'),

    url(r'^reg_aura$',
        views.reg_aura, name='reg_aura'),
    url(r'^epci_aura$',
        views.epci_aura, name='epci_aura'),

    #appelé au chargement de l'appli pour initialiser les couches
    url(r'^source_url$',
        views.source_url, name='source_url'),

    url(r'^getMoreSources/(?P<id>[0-9]+).json$',
        views.getMoreSources, name='getMoreSources'),
        
    url(r'^check_statut$',
        views.check_statut, name='check_statut'),
        
    url(r'^img/stats_reg_(?P<id>[0-9]+)$',
        views.calcul_stats_reg, name='calcul_stats_reg'),
        
       # .. img/raster_ech<ech>.png => multi polluant
    url(r'^img/export_low$',
        views.export_low, name='export_low'), 
        
       # .. img/raster_ech<ech>.png => multi polluant
    url(r'^img/export_low_val$',
        views.export_low_val, name='export_low_val'), 
        
    url(r'^getTsp$',
        views.getTsp, name='getTsp'), 
        
    url(r'^save_commentaire/$',
        views.save_commentaire, name='save_commentaire'), 
    
    
    url(r'^export_hd/$',
        views.export_hd, name='export_hd'),    
    url(r'^merge_fine$',
        views.merge_fine, name='merge_fine'),  
    url(r'^merge_mi_fine$',
        views.merge_mi_fine, name='merge_mi_fine'),

    url (r'^mylogout/$',views.mylogout,name='mylogout'),
    url(r'^fake$',
        views.fake, name='fake'),   
    url(r'^get_expertises$',
        views.get_expertise, name='get_expertise'),

]
