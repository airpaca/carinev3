from django.conf.urls import url,include
from . import api_rest_views
import django.contrib.auth 
from django.contrib.auth import views as auth_views
from rest_framework.schemas import get_schema_view

from rest_framework import routers


router = routers.DefaultRouter()

router.register(r'DomaineFine',api_rest_views.DomaineFineViewSet)
router.register(r'DatePrev',api_rest_views.DatePrevViewSet)


schema_view = get_schema_view(title='Pastebin API')

urlpatterns = [
    url(r'^', include(router.urls)),
	url(r'^schema/$', schema_view),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
	]