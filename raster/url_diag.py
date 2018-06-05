from django.conf.urls import url
from . import views,diag_views
import django.contrib.auth 
from django.contrib.auth import views as auth_views


urlpatterns = [

    url(r'^check_mod', diag_views.check_mod, name='check_mod'),
    url(r'^check_outputs', diag_views.check_outputs, name='check_outputs'),
]
