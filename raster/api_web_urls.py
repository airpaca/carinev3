from django.conf.urls import url
from . import views,api_web_views


urlpatterns = [
    ######## API SMILE ########
    url(r'^indice_com$',
    views.indice_com, name='indice_com'),
    url(r'^commentaire$',
    views.commentaire, name='commentaire'),
    url(r'^basse_def$',
    views.basse_def, name='basse_def'),
    url(r'^basse_def_val$',
    views.basse_def_val, name='basse_def_val'),
    url(r'^indice_request$',
    api_web_views.indice_request, name='indice_request'),
    url(r'^indice_request_unique$',
    api_web_views.indice_request_unique, name='indice_request_unique'),
    url(r'^indice_request_full$',
    api_web_views.indice_request_full, name='indice_request_full'),
    url(r'^get_square_buff$',
    api_web_views.get_square_buff, name='get_square_buff'),
    url(r'^best_prox_qa$',
    api_web_views.best_prox_qa, name='best_prox_qa'),
    url(r'^get_pixel_any$',
    api_web_views.get_pixel_any, name='get_pixel_any'),
    url(r'^trajet_request$',
    api_web_views.trajet_request, name='trajet_request'),  
    ]