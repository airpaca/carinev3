from django.conf.urls import url
from . import views,info_views


urlpatterns = [

    url(r'^get_sources$',
    info_views.get_sources, name='get_sources'),
 
    ]