from django.conf.urls import url
from . import config_views
import django.contrib.auth 
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^config_html$', config_views.config_html, name='config_html'),
    url(r'^config_js$', config_views.config_js, name='config_js'),
    url(r'^set_ctx$', config_views.set_ctx, name='set_ctx'),
    ]