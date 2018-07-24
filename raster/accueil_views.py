# -*- coding: utf-8 -*-
import logging
import datetime
import json
import psycopg2
import MySQLdb as msql
import rasterio as rio
import datetime
import fiona
import numpy as np
import random
import rasterstats
from django.core import serializers
from pyproj import Proj,transform
from django.views.decorators.http import require_POST
from django.template import loader
from django.http import HttpResponse, JsonResponse,HttpResponseRedirect
from .models import *
import libcarine3
from libcarine3 import timestamp,merge_tools,api,subprocess_wrapper,preprocessing,bqa_lib,write_log
import config,logins
import django.utils.timezone as tz
import os
import itertools
from django.views.decorators.cache import never_cache
import urllib.request
from rasterio import merge,windows
from rasterio.windows import from_bounds
import affine
from rasterstats import zonal_stats
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import urllib.request
from datetime import date,datetime
import pytz
# Log
log = logging.getLogger('carinev3.raster.views')

@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/accueil')
def accueil(request):
	"""Index."""
	if len(TodayState.objects.filter(date=date.today())) == 0:
		TodayState().save()
		
	template = loader.get_template('accueil/accueil.html')
	context = {'ctx' : Context.objects.get(active=True),'init' : TodayState.objects.get(date=date.today()).get_state( Context.objects.get(active=True))}
	return HttpResponse(template.render(context, request))

@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/accueil')
def accueil_js(request):
	"""Application (Javascript)."""
	template = loader.get_template('accueil/accueil.js')
	context = {'init' : TodayState.objects.get(date=date.today()).get_state(Context.objects.get(active=True))}
	return HttpResponse(template.render(context, request))
def set_state(request):
	state= request.GET.get('state')
	print(state)
	if (TodayState.objects.get(date=date.today())):
		t=TodayState.objects.get(date=date.today())
		t.file_ok = state
		t.date_preprocess=datetime.now(pytz.timezone("Europe/Paris"))
		t.save()
		return HttpResponse('set_state ok')
	else :
		return HttpResponse("problème d'initialisation de l'appli pour aujourd'hui") 
def get_state(request):
	ctx=Context.objects.get(active=True)
	if (TodayState.objects.get(date=date.today())):	
		t=TodayState.objects.get(date=date.today())
		stat=os.stat(ctx.previ_mod.DIR_RASTERS+'/ada')
		print(t.file_ok)
		print(t.date_preprocess)
		print(datetime.fromtimestamp(stat.st_mtime))
		if (datetime.fromtimestamp(stat.st_mtime) > t.date_preprocess):
			t.file_ok = False
			t.save()
		return HttpResponse(t.file_ok) 
	else :
		return HttpResponse("problème d'initialisation de l'appli pour aujourd'hui") 