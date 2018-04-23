from django.conf.urls import url
from . import bqa_views
import django.contrib.auth 
from django.contrib.auth import views as auth_views
urlpatterns = [
    url(r'^launch_BQA$',
        bqa_views.launch_BQA, name='launch_BQA'),
    url(r'^launch_BQA_unique$',
        bqa_views.launch_BQA_unique, name='launch_BQA_unique')
        ]