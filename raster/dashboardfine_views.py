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
from libcarine3 import *
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
from django.views.decorators.cache import never_cache

@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')    
def dashboard_fine(request):
	"""Index."""
	template = loader.get_template('dashboard_fine/dashboard_fine.html')
	context = {}
	return HttpResponse(template.render(context, request))
@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')
def dashboard_fine_js(request):
	"""Application (Javascript)."""
	template = loader.get_template('dashboard_fine/dashboard_fine.js')
	context = {}
	return HttpResponse(template.render(context, request))

def init_dallefine(request):
	tsp=libcarine3.timestamp.getTimestamp(0)
	dateObj = DatePrev.objects.get(date_prev = tsp)
	polls=Polluant.objects.all()
	ech = Echeance.objects.all()
	nom = DomaineFine.objects.all()
	for p in polls:
		if (p.nom != 'MULTI'):
			for e in ech:
				for n in nom:
					if (len(DalleFine.objects.filter(date_prev = dateObj, nom = n,ech = e, poll=p))==0):
						d=DalleFine(date_prev = dateObj, nom = n,ech = e, poll=p)
						d.save()
	return HttpResponse('ok')
						
def get_dalle_obj(dateprev,nom,poll,ech):
	dObj= DatePrev.objects.get(date_prev=dateprev)
	nObj= DomaineFine.objects.get(nom=nom)
	pObj= Polluant.objects.get(nom=poll)
	eObj= Echeance.objects.get(libInt=ech)
	dalle = DalleFine.objects.get(date_prev=dObj,nom=nObj,poll=pObj,ech=eObj)
	return dalle
def get_fine_url(request):
	dateprev= request.GET.get('date')
	nom= request.GET.get('nom')
	poll=request.GET.get('poll')
	ech= request.GET.get('ech')
	dalle=get_dalle_obj(dateprev,nom,poll,ech)
	url = dalle.get_url_fine()
	return HttpResponse(url)
def get_fine_url_by_id(request):
	id= request.GET.get('id')
	dalle=DalleFine.objects.get(id=id)
	url = dalle.get_url_fine()
	return HttpResponse(url) 
def get_mi_fine_url(request):
	return HttpResponse('en construction')
def get_fine_png(request):
	id=request.GET.get('id')
	dalle=DalleFine.objects.get(id=id)
	poll = dalle.poll.nom
	url = dalle.get_url_fine()

	
	if os.path.exists(url):
		r = libcarine3.Raster(url, pol=config.from_name(poll))
		data=r.get_array()

		data=libcarine3.merge_tools.sous_indice(data,config.from_name(poll))
		# Return image
		return HttpResponse(r.to_png(data,None,2000), content_type="image/png")
	else :
		return HttpResponse('pas de carte')

def get_poll_menu(request):
	polls=Polluant.objects.all().order_by('id')
	ex=request.GET.get('ex')
	d= ''
	for p in polls:
		if (p.nom != ex):
			d+='<li style="width : 24%;"><a  class="btn btn-default" onclick="switch_poll(\''+p.nom+'\')">'+p.nom+' </a></li>'

	return HttpResponse(d)
	
@never_cache
def get_table_fine(request):
	poll=request.GET.get('poll')
	pol=Polluant.objects.filter(nom=poll)
	tsp=timestamp.getTimestamp(0)
	domaines = DomaineFine.objects.all()
	ech = Echeance.objects.all()

	tbl = '<table id="fine-table" class="table-fine table table-bordered table-inverse"><thead><tr><th></th>'
	for e in ech:
		tbl += '<th style="text-align : center;">'+e.libChar+'</th>'
	tbl += '</tr></thead>'
	tbl += '<tbody>'
	for d in domaines:
		tbl+='<tr><th>'+d.nom+'</th>'
		for i in ech:
			#prev.ech<-1;2>
			prev = DatePrev.objects.get(date_prev=tsp)
			df = DalleFine.objects.filter(poll=pol,ech=i,date_prev=prev,nom=d)
			if (len(df)>0):
				df = df[0]
			url=reverse('get_fine_png')+'?id='+str(df.id)
			cls='red-fine-status'
			status = df.get_status()
			active = df.is_valid
			if (active == True):
				chk='checked'
			elif (active == False):
				chk = ''
			if (status == True):
				cls='green-fine-status'    
			cbx_id='td'+ str(df.id)
			td='<td  data-toggle="tooltip" title="'+i.libChar+'" class="img-container '+cls+'"><img src="'+url+'"></img><ul class="img-ul"><li><input class="form-check-input" onchange="toggle_active('+str(df.id)+')" type="checkbox" value="" id="'+cbx_id+'" ' + chk +'  ><label for="'+cbx_id+'">Activer / désactiver la dalle</label></li></ul></td>'
			#<img src='http://inf-carine3/carinev3/raster/get_fine_png?date=1516316400&nom=Lyon&ech=0&poll=PM10'></img>
			tbl+=td
		tbl+="</tr>"
	tbl+="</tbody></table>"
	return HttpResponse(tbl)
def set_fine_active(request):
	id=request.GET.get('id')
	df=DalleFine.objects.get(id=id)
	df.is_valid=not df.is_valid
	df.save()
	return HttpResponse(df.is_valid)
def check_fine_status(request):
	return HttpResponse('uh')
def get_fine_url_merge(id_prev):
	#renvoie la liste des domaines pour un poll une ech et une date
	prev=Prev.objects.get(id=id_prev)
	dateprev=DatePrev.objects.filter(date_prev=prev.date_prev)[0]
	ech = Echeance.objects.filter(delta=prev.ech)[0]
	if (prev.pol != 'MULTI'):
		poll=Polluant.objects.filter(nom=prev.pol)[0]
		dfs=DalleFine.objects.filter(date_prev=dateprev,poll=poll,ech=ech)
	elif (prev.pol == 'MULTI'):
		dfs=DalleFine.objects.filter(date_prev=dateprev,ech=ech)
	urls=[]
   
	for i in dfs:
		if (i.is_valid==True):
			urls.append(i.get_url_fine())
   
	return urls
	# return []
