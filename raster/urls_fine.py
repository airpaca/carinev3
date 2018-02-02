from django.conf.urls import url
from . import views,dashboardfine_views
import django.contrib.auth 
from django.contrib.auth import views as auth_views


urlpatterns = [
    url(r'^dashboard_fine$', dashboardfine_views.dashboard_fine, name='dashboard_fine'),
    url(r'^dashboard_fine_js$', dashboardfine_views.dashboard_fine_js, name='dashboard_fine_js'),
    url(r'^get_fine_url', dashboardfine_views.get_fine_url, name='get_fine_url'),
    url(r'^get_fine_url_by_id', dashboardfine_views.get_fine_url_by_id, name='get_fine_url_by_id'),
    url(r'^get_mi_fine_url', dashboardfine_views.get_mi_fine_url, name='get_mi_fine_url'),
    url(r'^init_dallefine', dashboardfine_views.init_dallefine, name='init_dallefine'),
    url(r'^get_poll_menu', dashboardfine_views.get_poll_menu, name='get_poll_menu'),    
    url(r'^get_fine_png', dashboardfine_views.get_fine_png, name='get_fine_png'),
    url(r'^get_table_fine', dashboardfine_views.get_table_fine, name='get_table_fine'),
    url(r'^check_fine_status', dashboardfine_views.check_fine_status, name='check_fine_status'),
    url(r'^set_fine_active', dashboardfine_views.set_fine_active, name='set_fine_active'),
    url(r'^get_fine_url_merge', dashboardfine_views.get_fine_url_merge, name='get_fine_url_merge'),
    
]

