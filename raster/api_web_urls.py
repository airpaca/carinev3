from django.conf.urls import url
from . import views


urlpatterns = [
    ######## API SMILE ########
    url(r'^indice_com$',
    views.indice_com, name='indice_com'),
    url(r'^commentaire$',
    views.commentaire, name='commentaire'),
    url(r'^basse_def$',
    views.basse_def, name='basse_def'),

    ]