from django.conf.urls import url
from . import accueil_views
import django.contrib.auth 
from django.contrib.auth import views as auth_views


urlpatterns = [
	
	# accueil
	url(r'^$', accueil_views.accueil, name='accueil'),

	# Dynamic javascript application
	url(r'^accueil.js$', accueil_views.accueil_js, name='accueil_js'),
		#etat du jour
	url(r'^get_state$',	accueil_views.get_state, name='get_state'),
	url(r'^set_state$', accueil_views.set_state, name='set_state'),
]

