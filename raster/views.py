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
import time

# Log
log = logging.getLogger('carinev3.raster.views')





@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')
def index(request):
	"""Index."""
	template = loader.get_template('raster/index.html')
	context = {'ctx' : Context.objects.get(active=True)}
	return HttpResponse(template.render(context, request))

@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')
def application_js(request):
	"""Application (Javascript)."""
	template = loader.get_template('raster/application.map.js')
	context = {}
	return HttpResponse(template.render(context, request))

@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')
def help(request):
	"""Index."""
	template = loader.get_template('help/help.html')
	context = {}
	return HttpResponse(template.render(context, request))
@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')
def help_js(request):
	"""Application (Javascript)."""
	template = loader.get_template('help/help.js')
	context = {}
	return HttpResponse(template.render(context, request))    
  
@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')
def get_init_info(request):
	ctx = Context.objects.get(active=True)
	polls=ctx.previ_mod.polls
	infos=dict(polls=polls,echs=ctx.previ_mod.echs_diff)
	ls={}
	d=libcarine3.timestamp.getTimestamp(0)
	p=Prev.objects.filter(date_prev=d)
	for i in p:
		ls[i.id]=[i.pol,i.ech]
	return JsonResponse(ls)
	
@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')
def check_statut(request):
	ls={}
	src0=Source.objects.filter(daterun=libcarine3.timestamp.getTimestamp(0),tsr__intrun=0)
	src1=Source.objects.filter(daterun=libcarine3.timestamp.getTimestamp(1),tsr__intrun=0)
	src2=Source.objects.filter(daterun=libcarine3.timestamp.getTimestamp(2),tsr__intrun=0)
	for s in src0:

		s.statut=s.checkStatut()
		s.save()
		ls[s.id]=s.json()
	for s in src1:
		s.statut=s.checkStatut()
		s.save()
		ls[s.id]=s.json()
	for s in src2:
		s.statut=s.checkStatut()
		s.save()
		ls[s.id]=s.json()
	return JsonResponse(ls)
	# else :
		# return HttpResponse("nb d'enregistrements dans Prev ne correspond ni a 0 ni a nb_polls*nb_ech")
@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')
def check_sources(request):
	p=Prev.objects.filter(date_prev=libcarine3.timestamp.getTimestamp(0))
	ls={}
	for i in p:
		if (i.src):
			ls[i.id]=i.src.id
		else :
			pass
	return JsonResponse(ls)
@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')
def source_url(request):
	tsr=TypeSourceRaster.objects.all()
	ls={}
	for t in tsr:
		ls[t.id]=t.json
	return  JsonResponse(ls)
@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')
def update_source(request):
	id_prev = request.GET.get('id_prev')
	id = request.GET.get('id')
	prev=Prev.objects.get(id=id_prev)
	source=Source.objects.get(id=id)
	prev.src=source
	prev.save()
	
	return HttpResponse(Prev.objects.get(id=id_prev).src.id)
@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')
def getMoreSources(request,id):
	ob=Source.objects.get(id=id)
	d=ob.daterun
	pol = ob.tsr.pol
	ech = ob.tsr.ech
	run = ob.tsr.intrun
	ts=TypeSourceRaster.objects.filter(pol=pol,ech=ech,intrun=run)
	sources={}
	for i in ts:
		other_src=i.source_set.get(daterun=d)
		sources[other_src.id]=other_src.json()
	#pas trouvé de moyen plus simple mais bon, ça fait le boulot:
	#on recup toutes les sources dispo pour le même pol/ech/run

	return JsonResponse(sources)
@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')
@never_cache
def img_raster(request):
	"""Raster as an image."""
	# TODO: ajouter transformation du raster en wgs84
	id=request.GET.get('id')
	ob=Source.objects.get(id=id)
	expertises = Expertise.objects.filter(target=ob)
	
	# Read raster
	fnrst =ob.url()   
	r = libcarine3.Raster(fnrst, pol=Polluant.objects.get(nom=ob.tsr.pol).val,source=ob)
	r.add_expertises(expertises)
	data=r.get_array()
	if (ob.tsr.pol!='MULTI'):
		data=libcarine3.merge_tools.sous_indice(data,Polluant.objects.get(nom=ob.tsr.pol).val)
	# Return image
	return HttpResponse(r.to_png(data,None,20), content_type="image/png")
def img_raster_url(request):
	id_source = request.GET.get('id_source')

	u=reverse('img_raster')+'?id='+str(id_source) + '&randomnocache='+str(random.random())
	return HttpResponse(u)
@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')
def info_raster(request,id):
	ob=Source.objects.get(id=id)
	url=ob.url()
	pol=Polluant.objects.get(nom=ob.tsr.pol).val
	ds=rio.open(url)
	arr=ds.read(1)
	ss_ind=''
	if (pol!=10):
		ss_ind=libcarine3.merge_tools.sous_indice(arr,pol)
	pr=ds.profile
	ds.close()
	return JsonResponse({'height':pr['height'],'width':pr['width'],'driver':pr['driver'],'transform':pr['transform']})
	
@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')
def img_multi_unique(request):
#implementé direct dans img_raster,
# sert a tester direct la fonction, a virer si vraiment on s'en sert jamais
	id_prev=request.GET.get('id_prev')
	prev=Prev.objects.get(id=id_prev)
	prevs=Prev.objects.filter(date_prev=prev.date_prev,ech=prev.ech)
	arr_list=[]
	tr = ''
	for i in prevs:    
		if (i.pol!='MULTI'):
			polnum=Polluant.objects.get(nom=i.pol).val
			log.debug("============================")
			log.debug(i.pol)
			log.debug(polnum)
			expertises = Expertise.objects.filter(target=i.src)
			r = libcarine3.Raster(i.src.url(), pol=polnum,source=i.src)
			tr=r.r.transform
			log.debug("============================ GET ARRAY ====================")
			r.add_expertises(expertises)
			data=r.get_array()
			
			log.debug(np.max(data))
			# if (i.pol=='O3'):
				# data=data-data
			data=libcarine3.merge_tools.sous_indice(data,polnum)
			log.debug(np.min(data))
			arr_list.append(data)
			
	new_arr=libcarine3.merge_tools.merge_method('max',arr_list)
	
	fn=prev.src.url()
	if (os.path.exists(fn)):
		os.remove(fn)
	src_crs = {'init': 'EPSG:3857'}
	with rio.Env(GDAL_CACHEMAX=512,NUM_THREADS=1) as env:
		with rio.open(fn,'w',count=1,dtype='float64',driver='GTiff',compress='DEFLATE',crs=src_crs, height=300,width=400,transform=tr,nodata=0) as dst:
			dst.write(new_arr,1)
			dst.close()
	#rajout dernière minute export 2154, a fusionner les deux dans une seule fct..  
	arr_list=[]
	tr=''
	for i in prevs:    
		if (i.pol!='MULTI'):
			polnum=Polluant.objects.get(nom=i.pol).val
			log.debug("============================")
			log.debug(i.pol)
			log.debug(polnum)
			expertises = Expertise.objects.filter(target=i.src)
			r = libcarine3.Raster(i.src.url_2154(), pol=polnum,source=i.src,epsg=2154)
			log.debug("============================ GET ARRAY ====================")
			tr=r.r.transform
			r.add_expertises(expertises)
			data=r.get_array()
			
			log.debug(np.max(data))
			# if (i.pol=='O3'):
				# data=data-data
			data=libcarine3.merge_tools.sous_indice(data,polnum)
			log.debug(np.min(data))
			arr_list.append(data)
			
	new_arr=libcarine3.merge_tools.merge_method('max',arr_list)
	
	fn=prev.src.url_2154()
	src_crs = {'init': 'EPSG:2154'}
	log.debug(tr)
	if (os.path.exists(fn)):
		os.remove(fn)
	with rio.Env(GDAL_CACHEMAX=512,NUM_THREADS=1) as env:
		with rio.open(fn,'w',count=1,dtype='float64',driver='GTiff',compress='DEFLATE',height=342,width=447,crs=src_crs,transform=tr,nodata=0) as dst:
			dst.write(new_arr,1)
			dst.close() 
	return HttpResponse(fn)
@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')
def img_multi(request):
#implementé direct dans img_raster,
# sert a tester direct la fonction, a virer si vraiment on s'en sert jamais
	ech=int(request.GET.get('ech'))-1
	prevs=Prev.objects.filter(ech=ech,date_prev=libcarine3.timestamp.getTimestamp(0))
	
	arr_list=[]
	tr = ''
	for i in prevs:    
		if (i.pol!='MULTI'):
			polnum=Polluant.objects.get(nom=i.pol).val
			log.debug("============================")
			log.debug(i.pol)
			log.debug(polnum)
			expertises = Expertise.objects.filter(target=i.src)
			r = libcarine3.Raster(i.src.url(), pol=polnum,source=i.src)
			tr=r.r.transform
			log.debug("============================ GET ARRAY ====================")
			r.add_expertises(expertises)
			data=r.get_array()
			
			log.debug(np.max(data))
			# if (i.pol=='O3'):
				# data=data-data
			data=libcarine3.merge_tools.sous_indice(data,polnum)
			log.debug(np.min(data))
			arr_list.append(data)
			
	new_arr=libcarine3.merge_tools.merge_method('max',arr_list)
	
	fn=Prev.objects.get(ech=ech,date_prev=libcarine3.timestamp.getTimestamp(0),pol='MULTI').src.url()
	if (os.path.exists(fn)):
		os.remove(fn)
	src_crs = {'init': 'EPSG:3857'}
	with rio.Env(GDAL_CACHEMAX=512,NUM_THREADS=1) as env:
		with rio.open(fn,'w',count=1,dtype='float64',driver='GTiff',compress='DEFLATE',crs=src_crs, height=300,width=400,transform=tr,nodata=0) as dst:
			dst.write(new_arr,1)
			dst.close()
	#rajout dernière minute export 2154, a fusionner les deux dans une seule fct..  
	arr_list=[]
	tr=''
	for i in prevs:    
		if (i.pol!='MULTI'):
			polnum=Polluant.objects.get(nom=i.pol).val
			log.debug("============================")
			log.debug(i.pol)
			log.debug(polnum)
			expertises = Expertise.objects.filter(target=i.src)
			r = libcarine3.Raster(i.src.url_2154(), pol=polnum,source=i.src,epsg=2154)
			log.debug("============================ GET ARRAY ====================")
			tr=r.r.transform
			r.add_expertises(expertises)
			data=r.get_array()
			
			log.debug(np.max(data))
			# if (i.pol=='O3'):
				# data=data-data
			data=libcarine3.merge_tools.sous_indice(data,polnum)
			log.debug(np.min(data))
			arr_list.append(data)
			
	new_arr=libcarine3.merge_tools.merge_method('max',arr_list)
	
	fn=Prev.objects.get(ech=ech,date_prev=libcarine3.timestamp.getTimestamp(0),pol='MULTI').src.url_2154()
	src_crs = {'init': 'EPSG:2154'}
	log.debug(tr)
	if (os.path.exists(fn)):
		os.remove(fn)
	with rio.Env(GDAL_CACHEMAX=512,NUM_THREADS=1) as env:
		with rio.open(fn,'w',count=1,dtype='float64',driver='GTiff',compress='DEFLATE',height=342,width=447,crs=src_crs,transform=tr,nodata=0) as dst:
			dst.write(new_arr,1)
			dst.close() 
	return HttpResponse(fn)
@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')
def sites_fixes(request):
	conn = psycopg2.connect("host="+logins.host+  " dbname="+logins.dbname +  " user="+logins.user+" password=" + logins.password )
	cur=conn.cursor()
	req = "select id_site,nom_site,st_X(st_transform(" + Context.objects.get(active=True).previ_mod.geom_field + ",4326))as x,st_Y(st_transform(" + Context.objects.get(active=True).previ_mod.geom_field + ",4326)) as y from sites_fixes"
	cur.execute(req)
	res=cur.fetchall();
	conn.close()
	liste_sites=[]
	for i in res:
		row={"type": "Feature","geometry": {"type": "Point","coordinates": [i[2],i[3]]},"properties": {"nom" : i[1]},"id_site": i[0]}
		liste_sites.append(row)
	str={"type": "FeatureCollection","features": liste_sites}   
	return JsonResponse(str)
@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')
def reg_aura(request):

	conn = psycopg2.connect("host="+logins.host+  " dbname="+logins.dbname +  " user="+logins.user+" password=" + logins.password )
	cur=conn.cursor()
	if config.aasqa == "aura":
		req = "select id_zone,lib_zone,st_asgeojson(st_transform(" + Context.objects.get(active=True).previ_mod.geom_field + ",4326)) as the_geom from zones where id_zone=2038 or id_zone=0"
	if config.aasqa == "aura_preprod":
		req = "select id_zone,lib_zone,st_asgeojson(st_transform(" + Context.objects.get(active=True).previ_mod.geom_field + ",4326)) as the_geom from zones where id_zone=2038 or id_zone=0"
	if config.aasqa == "aura_dev":
		req = "select id_zone,lib_zone,st_asgeojson(st_transform(" + Context.objects.get(active=True).previ_mod.geom_field + ",4326)) as the_geom from zones where id_zone=2038 or id_zone=0"
	elif config.aasqa == "airpaca":
		req = "select id_zone,lib_zone,st_asgeojson(st_transform(" + Context.objects.get(active=True).previ_mod.geom_field + ",4326)) as the_geom from zones where id_zone=0"
	cur.execute(req)
	res=cur.fetchall();
	conn.close()
	liste_sites=[]
	for i in res :
		row={"type": "Feature","geometry": {"type": "MultiPolygon","coordinates": json.loads(i[2])['coordinates']},"properties": {"nom" : i[1]},"id_reg": i[0]}
		liste_sites.append(row)

	return JsonResponse(liste_sites,safe=False)
# @login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')
# def disp_reg(request):
	# conn = psycopg2.connect("host="+logins.host+  " dbname="+logins.dbname +  " user="+logins.user+" password=" + logins.password )
	# cur=conn.cursor()
	# req = "select id_zone,lib_zone,st_asgeojson(" + Context.objects.get(active=True).previ_mod.geom_field + ") as " + Context.objects.get(active=True).previ_mod.geom_field + " from temp_epci_2017_aura_4326"
	# cur.execute(req)
	# res=cur.fetchall();
	# conn.close()
	# liste_sites=[]
	# for i in res :
		# row={"type": "Feature","geometry": {"type": "MultiPolygon","coordinates": json.loads(i[2])['coordinates']},"properties": {"nom" : i[1]},"id_epci": i[0]}
		# liste_sites.append(row)
	# return JsonResponse(liste_sites,safe=False)
@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')
def bbox_raster(request):
	"""Bounding box of the raster."""
	id = request.GET.get('id')
	#defaut_id == id d'une instance de Source a prendre pr MULTI
	ob=Source.objects.get(id=id)
	#a moins d'ecrire direct en dur chaque indice multi, on prend la default bbox pr multi)

	fnrst =ob.url()
	r = libcarine3.Raster(fnrst, pol=Polluant.objects.get(nom=ob.tsr.pol).val,source=ob)
	x1, y1, x2, y2 = r.bbox

	inProj = Proj(init='epsg:3857')
	outProj = Proj(init='epsg:4326')
	xmin,ymin = transform(inProj,outProj,x1,y1)
	xmax,ymax = transform(inProj,outProj,x2,y2)
	return JsonResponse(dict(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax))
@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')
def list_modifications(request,id):
	"""Liste des modifications."""

	daterun = datetime.date.today()
	daterun = DATE_TEST  # test
	source=TypeSourceRaster.objects.filter(id=id)
	objs = Expertise.objects.filter(id_source=source)
	data = dict(source, pol=pol, ech=int(ech),
				modifs=[e.json for e in objs])
	return JsonResponse(data)


# @require_POST
@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')
def test_ajax(request):
   
	b=request.body
	
	
	return HttpResponse(b)
@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')    
#TODO modif obj tsr
def alter_raster(request):
	"""Route to alter the raster."""
	import ast
	print("**************************************************************")
	print("ALTER RASTER")
	print("**************************************************************")
	
	def error(message):
		"""Return a error JSON response."""
		log.error(message)
		return JsonResponse({'status': 'error', 'message':request.body},
							status=400)

	log.debug('************************************************************')
	log.debug(request.body)
	user=request.user
	id_source =request.POST.get('source')
	val=request.POST.get('value')
	corr_min=request.POST.get('minimum')
	corr_max=request.POST.get('maximum')
	corr_ssup=request.POST.get('ssup')
	coords=request.POST.get('coords')
	coords=ast.literal_eval(coords)

		
	# Get data
	if not request.body:
		return error("Missing data from request.")

	# print(request.body)
	#data = json.loads(request.body)

	# id = data.get('id')
	# modifs = data.get('modifs')



	# # Insert data into database

	src=Source.objects.get(id=id_source)
	# # Check data TODO
	# for modif in modifs:

	# Insert data into database
	inProj = Proj(init='epsg:4326')
	outProj = Proj(init='epsg:3857')
	#geom_type = modifs['geom']['type']
	geom_type='POLYGON'
	print(coords)

	coords_3857=[]
	for i in coords:     
		x_dest,y_dest = transform(inProj,outProj,i[0],i[1])
		coords_3857+=[[x_dest,y_dest]]
	print(coords_3857)
	# coords_3857=[coords_3857]
	# print(coords_3857)
	# if geom_type == 'Point':
		# x, y = coords
		# geom = f'POINT({x} {y})'
   
	# elif geom_type == 'POLYGON':
	strcoord = ", ".join([f"{x} {y}" for (x, y) in coords_3857])
	geom = f'POLYGON(({strcoord}))'
	print(geom)

	# else:
		# return error('error in parameters')

	# Create objects
	
	e = Expertise(target=src, delta=val, geom=geom, mn=corr_min, mx=corr_max, ssup=corr_ssup,user=user)
	e.save()

	return JsonResponse(dict(one='uh'))
@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')
def get_pixel(request):
	id = request.GET.get('id')
	x = request.GET.get('x')
	y = request.GET.get('y')
	ob=Source.objects.get(id=id)
	expertises = Expertise.objects.filter(target=ob)
	# Read raster
	fnrst =ob.url()

	r = libcarine3.Raster(fnrst, pol=Polluant.objects.get(nom=ob.tsr.pol).val,source=ob)
	r.add_expertises(expertises)
	x=int(x)/1000000.0
	y=int(y)/1000000.0
	inProj = Proj(init='epsg:4326')
	outProj = Proj(init='epsg:3857')
	x_dest,y_dest = transform(inProj,outProj,x,y)
	v=r.sample_gen(x_dest,y_dest)
	v[0]=round(float(v[0]),2)
	v[1]=round(float(v[1]),2)
	return JsonResponse(dict(val=v))
	

def mylogout(request):
	logout(request)
	return redirect('%s?next=%s' % (settings.LOGIN_URL, '/carinev3/raster/'))


def calcul_stats_reg(request):
	id_prev = request.GET.get('id_prev')
	prev=Prev.objects.get(id=id_prev)
	id=prev.src.id
	"""Raster as an image."""
	# TODO: ajouter transformation du raster en wgs84
	log.debug(id)
	ob=Source.objects.get(id=id)

	expertises = Expertise.objects.filter(target=ob)
	log.debug(expertises)
	
	# Read raster
	fnrst =ob.url_2154()
	log.debug(fnrst)
	r = libcarine3.Raster(fnrst, pol=Polluant.objects.get(nom=ob.tsr.pol).val,source=ob,epsg=2154)
	r.add_expertises(expertises)
	log.debug(r.expertises)
	data=r.get_array()
	if (ob.tsr.pol!='MULTI'):
		data=libcarine3.merge_tools.sous_indice(data,Polluant.objects.get(nom=ob.tsr.pol).val)
	data=data.repeat(10,axis=0).repeat(10,axis=1)
	
	fpop=r'/home/previ/raster_source/pop/pop100m_2154.tif'
	ds= rio.open(fpop)
	pop =ds.read(1)

	aff=r.r.transform
	newaff = affine.Affine(aff.a / 10, aff.b, aff.c,aff.d, aff.e / 10, aff.f)

	disp=r'/home/previ/vector_source/disp_reg_aura.shp'
	pixel_3857=0.01
	data2 = (data>90)
	data3 = data2 * pixel_3857
	
	zs_surf_info = zonal_stats(disp, data3,stats=['sum','count'], affine=newaff,geojson_out=True)
	log.debug("================ data shape ===============")
	log.debug(data.shape)
	log.debug(data2.shape)
	log.debug("================ ZS SURF ===============")

	log.debug("================ ZS POP ===============")
	log.debug(pop.shape)
	data4=data2*pop
	
	zs_pop_info= zonal_stats(disp, data4,stats=['sum'], affine=newaff,geojson_out=True)
	#zs = zonal_stats(disp, data, affine=newaff,stats=['max'],add_stats={'myfunc':merge_tools.myfunc})
	# log.debug("================ data shape ===============")
	# log.debug(r.fn)
	# log.debug(data2.shape)
	# log.debug(np.max(data))
	# log.debug(np.max(data2))
	
	#la meme chose pr le seuil Alerte :
	data2 = (data>=100)
	data3 = data2 * pixel_3857
	data4=data2*pop
	zs_surf_alerte = zonal_stats(disp, data3,stats=['sum','count'], affine=newaff,geojson_out=True) 
	zs_pop_alerte = zonal_stats(disp, data4,stats=['sum'], affine=newaff,geojson_out=True)
	
	dct=dict()
	for i in zs_pop_info :  
		pop=i['properties']['pop_tr_sum']
		pop_exp_info = round(i["properties"]['sum'],2)
		pop_exp_perc_info = round((pop_exp_info/pop)*100,2)
		depassement_pop_info=False
		if (pop > 500000):
			if (pop_exp_perc_info > 10):
				depassement_pop_info=True
		elif (pop <= 500000) :
			if (pop_exp_info > 50000):
				depassement_pop_info=True
		dct[i["properties"]["id_zone"]]={'lib' :i["properties"]['lib_court_'] ,'pop_exp_info': pop_exp_info,'pop_exp_perc_info':pop_exp_perc_info,'depassement_pop_info' : depassement_pop_info}
	for j in zs_surf_info:
		surf_exp_info = round(j["properties"]['sum'],2)
		surf=round(j["properties"]['count'],2)
		depassement_surf_info=False
		if (surf_exp_info > 25):
			depassement_surf_info = True
		dct[j["properties"]["id_zone"]]['surf_exp_info']=surf_exp_info
		dct[j["properties"]["id_zone"]]['surf_exp_perc_info']=round((surf_exp_info/(surf*0.01))*100,2)
		dct[j["properties"]["id_zone"]]['depassement_surf_info']=depassement_surf_info
	for k in zs_surf_alerte:
		surf_exp_alerte = round(k["properties"]['sum'],2)
		surf=round(k["properties"]['count'],2)
		depassement_surf_alerte=False
		if (surf_exp_alerte > 25):
			depassement_surf_alerte = True
		dct[k["properties"]["id_zone"]]['surf_exp_alerte']=surf_exp_alerte
		dct[k["properties"]["id_zone"]]['surf_exp_perc_alerte']=round((surf_exp_alerte/(surf*0.01))*100,2)
		dct[k["properties"]["id_zone"]]['depassement_surf_alerte']=depassement_surf_alerte
	for l in zs_pop_alerte :  
		pop=l['properties']['pop_tr_sum']
		pop_exp_alerte = round(l["properties"]['sum'],2)
		pop_exp_perc_alerte = round((pop_exp_alerte/pop)*100,2)
		depassement_pop_alerte=False
		if (pop > 500000):
			if (pop_exp_perc_alerte > 10):
				depassement_pop_alerte=True
		elif (pop <= 500000) :
			if (pop_exp_alerte > 50000):
				depassement_pop_alerte=True
		dct[l["properties"]["id_zone"]]['pop_exp_alerte'] = pop_exp_alerte
		dct[l["properties"]["id_zone"]]['pop_exp_perc_alerte'] = pop_exp_perc_alerte
		dct[l["properties"]["id_zone"]]['depassement_pop_alerte'] = depassement_pop_alerte
	for i in dct:
		obj = dct[i]
		log.debug(i)
		log.debug(obj)
		log.debug("  ***********************  ")
		id_zone = i
		lib = obj['lib']
		log.debug(lib)
		pop_exp_info = obj['pop_exp_info']
		pop_exp_perc_info = obj['pop_exp_perc_info']
		surf_exp_info = obj['surf_exp_info']
		surf_exp_perc_info = obj['surf_exp_perc_info']
		depassement_pop_info = obj['depassement_pop_info']
		depassement_surf_info = obj['depassement_surf_info']
		pop_exp_alerte = obj['pop_exp_alerte']
		pop_exp_perc_alerte = obj['pop_exp_perc_alerte']
		surf_exp_alerte = obj['surf_exp_alerte']
		surf_exp_perc_alerte = obj['surf_exp_perc_alerte']
		depassement_pop_alerte = obj['depassement_pop_alerte']
		depassement_surf_alerte = obj['depassement_surf_alerte']
		qs=DepassementReg.objects.filter(zone=id_zone,prev=prev)
		if (len(qs)==0):
			dp=DepassementReg(
				zone = i,
				prev=prev,
				lib = lib,
				pop_exp_info = pop_exp_info,
				pop_exp_perc_info = pop_exp_perc_info,
				surf_exp_info = surf_exp_info,
				surf_exp_perc_info = surf_exp_perc_info,
				depassement_pop_info = depassement_pop_info,
				depassement_surf_info = depassement_surf_info,
				pop_exp_alerte = pop_exp_alerte,
				pop_exp_perc_alerte = pop_exp_perc_alerte,
				surf_exp_alerte = surf_exp_alerte,
				surf_exp_perc_alerte = surf_exp_perc_alerte,
				depassement_pop_alerte = depassement_pop_alerte,
				depassement_surf_alerte = depassement_surf_alerte
			)
			dp.save()
		elif (len(qs)==1):
			dp=qs[0]
			dp.pop_exp_info = pop_exp_info
			dp.pop_exp_perc_info = pop_exp_perc_info
			dp.surf_exp_info = surf_exp_info
			dp.surf_exp_perc_info = surf_exp_perc_info
			dp.depassement_surf_info = depassement_surf_info
			dp.depassement_pop_info = depassement_pop_info
			dp.pop_exp_alerte = pop_exp_alerte
			dp.pop_exp_perc_alerte = pop_exp_perc_alerte
			dp.surf_exp_alerte = surf_exp_alerte
			dp.surf_exp_perc_alerte = surf_exp_perc_alerte
			dp.depassement_pop_alerte = depassement_pop_alerte
			dp.depassement_surf_alerte = depassement_surf_alerte
			dp.save()
		else : 
			log.debug(" === trop d'enregistrements pour <qs=DepassementReg.objects.filter(id_zone=id_zone,prev=prev> ===")        
	return JsonResponse(dct)
def calcul_indice_com(request):
	id_prev = request.GET.get('id_prev')
	prev=Prev.objects.get(id=id_prev)
	id=prev.src.id
	"""Raster as an image."""
	# TODO: ajouter transformation du raster en wgs84
	log.debug(id)
	ob=Source.objects.get(id=id)

	expertises = Expertise.objects.filter(target=ob)
	log.debug(expertises)
	
	# Read raster
	fnrst =ob.url_2154()
	log.debug(fnrst)
	
	r = libcarine3.Raster(fnrst, pol=Polluant.objects.get(nom=ob.tsr.pol).val,source=ob,epsg=2154)
	r.add_expertises(expertises)
	log.debug(r.expertises)
	data=r.get_array()

	data=data.repeat(10,axis=0).repeat(10,axis=1)
	
	fpop=r'/home/previ/raster_source/pop/pop100m_2154.tif'
	fpop_com=r'/home/previ/raster_source/pop/pop_com_lyonok.tif'
	ds= rio.open(fpop)
	pop =ds.read(1)
	ds2=rio.open(fpop_com)
	pop_com=ds2.read(1)
	log.debug(" ======== r.r.transform =============== ")
	log.debug(" ======== r.r.transform =============== ")
	aff=r.r.transform
	log.debug(aff)    
	newaff = affine.Affine(aff.a / 10, aff.b, aff.c,aff.d, aff.e / 10, aff.f)
	log.debug(aff)
	disp=r'/home/previ/vector_source/communes_geofla_light.shp'
	lyon_arr = r'/home/previ/vector_source/lyon_geofla_arr.shp'
	data2 = pop*data
	log.debug(data2.shape)

	log.debug("================ data shape ===============")
	log.debug(data.shape)
   
	log.debug(pop.shape)
	log.debug("================ ZS IC ===============")


	zs_ic = zonal_stats(disp, data2,stats=['sum'], affine=newaff,geojson_out=True)
	zs_lyon=zonal_stats(lyon_arr, data2,stats=['sum'], affine=newaff,geojson_out=True)

	dct=dict()

	for j in zs_ic:
		popcom=j["properties"]['pop_tr_sum']
		s=(round(j["properties"]['sum'])/popcom)
		lib=j["properties"]['NOM_COM']
		code_insee=j["properties"]["INSEE_COM"]
		dct[code_insee]={'lib' :lib ,'total' :s}
		#save BD
		qs=IndiceCom.objects.filter(code_insee=code_insee,prev=prev)
		if (len(qs)==0):            
			ic=IndiceCom(code_insee=code_insee, lib=lib, indice=s, prev=prev)
			ic.save()
		else :
			qs[0].indice=s
			qs[0].save()
	for l in zs_lyon:
		popcom=l["properties"]['pop_tr_sum']
		s=(round(l["properties"]['sum'])/popcom)
		lib=l["properties"]['NOM_COM']
		code_insee=l["properties"]["INSEE_COM"]
		dct[code_insee]={'lib' :lib ,'total' :s}
		#save BD
		qs=IndiceCom.objects.filter(code_insee=code_insee,prev=prev)
		if (len(qs)==0):            
			ic=IndiceCom(code_insee=code_insee, lib=lib, indice=s, prev=prev)
			ic.save()
		else :
			qs[0].indice=s
			qs[0].save()        
	return JsonResponse(dct)
@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')
def export_low(request):
	ctx=Context.objects.get(active=True)
	"""Raster as an image."""
	# TODO: ajouter transformation du raster en wgs84
	id=request.GET.get('id_source')
	id_prev=request.GET.get('id_prev')
	prev=Prev.objects.get(id=id_prev)
	log.debug(id)
	ob=Source.objects.get(id=id)

	expertises = Expertise.objects.filter(target=ob)
	log.debug(expertises)
	
	# Read raster
	fnrst =ob.url()
	log.debug(fnrst)
	
	r = libcarine3.Raster(fnrst, pol=Polluant.objects.get(nom=ob.tsr.pol).val,source=ob)
	r.add_expertises(expertises)
	log.debug(r.expertises)
	data=r.get_array()
	log.debug(" ================== ================== ================== ")
	log.debug(np.max(data))
	if (ob.tsr.pol!='MULTI'):
		data=libcarine3.merge_tools.sous_indice(data,Polluant.objects.get(nom=ob.tsr.pol).val)
	log.debug(np.max(data))
	# Return image
	
	dp=DicoPath.objects.get(nom='bd rgba')
	output_data=OutputData.objects.get(type=dp)
	u=dp.get_file_url(ctx.previ_mod.raster_prefix,prev.pol.lower(),prev.date_prev,prev.ech+1)
	u_full=os.path.join(ctx.previ_mod.output_dir,os.path.join(output_data.dir,u))
	name=config.basse_def_path+config.aasqa+'-'+prev.pol.lower()+'-'+str(prev.date_prev)+'-'+str(prev.ech+1)+ '.png'
	r.to_png(data,name,10)
	
	#libcarine3.subprocess_wrapper.scp_classic(name,'192.168.37.158','airtogo','/home/aura_datas/carine_data/basse_def/')
	return HttpResponse(name)
@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')
def export_low_val(request):
	ctx=Context.objects.get(active=True)
	"""Raster as an image."""
	# TODO: ajouter transformation du raster en wgs84
	id=request.GET.get('id_source')
	log.debug(id)
	id_prev=request.GET.get('id_prev')
	prev=Prev.objects.get(id=id_prev)
	log.debug(id)
	ob=Source.objects.get(id=id)

	expertises = Expertise.objects.filter(target=ob)
	log.debug(expertises)
	
	# Read raster
	fnrst =ob.url()
	log.debug("________ -- FILENAME -- __________")
	log.debug(fnrst)
	
	r = libcarine3.Raster(fnrst, pol=Polluant.objects.get(nom=ob.tsr.pol).val,source=ob)
	r.add_expertises(expertises)
	log.debug(r.expertises)
	

	dp=DicoPath.objects.get(nom='bd concentration')
	output_data=OutputData.objects.get(type=dp)
	u=dp.get_file_url(ctx.previ_mod.raster_prefix,prev.pol.lower(),prev.date_prev,prev.ech+1)
	u_full=os.path.join(ctx.previ_mod.output_dir,os.path.join(output_data.dir,u))
	
	#fullPath=dict(img=os.path.join(ctx.previ_mod.basse_def_val_path,ctx.previ_mod.raster_prefix+'-'+pol.lower()+'-'+str(tsp)+'-'+ech+'.tiff'))
	#name=config.basse_def_val_path+config.aasqa+'-'+prev.pol.lower()+'-'+str(prev.date_prev)+'-'+str(prev.ech+1)+ '.tiff'
	msg=r.export_low_val(u_full)
	log.debug(msg)
	#libcarine3.subprocess_wrapper.scp_classic(name,'192.168.37.158','airtogo','/home/aura_datas/carine_data/basse_def/val')
	return HttpResponse(msg)
@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')
def getTsp(request):
	tsp0=libcarine3.timestamp.getTimestamp(0)
	tsp1=libcarine3.timestamp.getTimestamp(1)
	tsp2=libcarine3.timestamp.getTimestamp(2)
	return JsonResponse(dict(t=tsp0,y=tsp1,yy=tsp2))
@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')
def save_commentaire(request):
	comm=request.POST.get('commentaire')
	tsp=request.POST.get('date_prev')
	p=DatePrev.objects.get(date_prev=tsp)
	p.commentaire=comm
	p.save()
	p=DatePrev.objects.get(date_prev=tsp)
	return HttpResponse(p.commentaire)

@never_cache  
def indice_com(request):
	if ((request.GET.get('date') != None ) &(request.GET.get('ech') != None )):
		date_prev=request.GET['date']
		tsp=libcarine3.timestamp.getTimestampFromDate(date_prev)
		log.debug(tsp)
		ech=int(request.GET['ech'])
		if ( 0 <= ech <= 3 ):
			p = Prev.objects.get(date_prev=tsp,ech=ech-1,pol='MULTI')
			qs = IndiceCom.objects.filter(prev=p)
			l=[]
			for i in qs:
				l.append(i.json_less())
			return HttpResponse(json.dumps(l))
		else :
			return HttpResponse("Valeur incorrecte pour l'échéance : ech= "+str(ech) )
	else : 
		return HttpResponse('Paramètres du GET invalides')
	#return HttpResponse(json.dumps(l))

@never_cache    
def basse_def (request):
	ctx=Context.objects.get(active=True)
	date_prev=request.GET.get('date')
	tsp=libcarine3.timestamp.getTimestampFromDate(date_prev)
	pol=request.GET.get('pollutant')
	ech=request.GET.get('term')
	path=ctx.previ_mod.public_adresse

	dp=DicoPath.objects.get(nom='bd rgba')
	output_data=OutputData.objects.get(type=dp)
	u=dp.get_file_url(ctx.previ_mod.raster_prefix,pol.lower(),tsp,ech)
	u_full=os.path.join(path,os.path.join(output_data.dir,u))
	return JsonResponse(dict(img=u_full))
@never_cache    
def basse_def_val (request):
	ctx=Context.objects.get(active=True)
	date_prev=request.GET.get('date')
	tsp=libcarine3.timestamp.getTimestampFromDate(date_prev)
	pol=request.GET.get('pollutant')
	ech=request.GET.get('term')
	path=ctx.previ_mod.public_adresse
	dp=DicoPath.objects.get(nom='bd concentration')
	output_data=OutputData.objects.get(type=dp)
	u=dp.get_file_url(ctx.previ_mod.raster_prefix,pol.lower(),tsp,ech)
	u_full=os.path.join(path,os.path.join(output_data.dir,u))
	return JsonResponse(dict(img=u_full))
	
@never_cache
def commentaire(request):
	comm=""
	if (request.GET.get('date') != None ):
		date_prev=request.GET.get('date')
		tsp=libcarine3.timestamp.getTimestampFromDate(date_prev)
		p=DatePrev.objects.get(date_prev=tsp)
		comm=p.commentaire
	return JsonResponse(dict(comment=comm))

@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')    
def export_hd(request):
	id_source=request.GET.get('id_source')
	id_prev=request.GET.get('id_prev')
	ratio=request.GET.get('ratio')
	src=Source.objects.get(id=id_source)
	prev=Prev.objects.get(id=id_prev)
	urls=[]
	pol=prev.pol
	ech=prev.ech
	lib_ech=config.libs_ech[ech]
	tsp=prev.date_prev
	for i in config.domaines_hd:
		url='AURA_'+pol.upper()+'_'+i+'_'+str(tsp)+'_'+lib_ech+'_3857.tif'   
	r = libcarine3.Raster(src.url(), pol=config.from_name(src.tsr.pol),source=src)
	r.export_ratio(100)
	return HttpResponse(r.fn)
@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')    
def merge_fine(request):
	ctx=Context.objects.get(active=True)
	id_source=request.GET.get('id_source')
	id_prev=request.GET.get('id_prev')
	ratio=request.GET.get('ratio')
	prev=Prev.objects.get(id=id_prev)
	src=Source.objects.get(id=id_source)
	expertises = Expertise.objects.filter(target=src)
	#with rio.Env(GDAL_CACHEMAX=16384,NUM_THREADS='ALL_CPUS') as env:
	r = libcarine3.Raster(src.url(), pol=config.from_name(src.tsr.pol),source=src)
	r.add_expertises(expertises)
	dp_val=DicoPath.objects.get(nom='hd sous_indice')
	dp_img=DicoPath.objects.get(nom='hd rgba')
	u=dp_val.get_file_url(ctx.previ_mod.raster_prefix,str.lower(prev.pol),prev.date_prev,prev.ech+1)
	full_u = os.path.join(ctx.previ_mod.output_dir,os.path.join(ctx.previ_mod.hd_val_path,u))
	u2=dp_img.get_file_url(ctx.previ_mod.raster_prefix,str.lower(prev.pol),prev.date_prev,prev.ech+1)
	utemp=u2.replace('-','_')
	full_u2 = os.path.join(ctx.previ_mod.output_dir,os.path.join(ctx.previ_mod.hd_path,u2))   
	full_utemp=os.path.join(ctx.previ_mod.output_dir,os.path.join(ctx.previ_mod.hd_path,utemp))   
	f=libcarine3.merge_tools.merge_fine(r,prev,full_u)
	#libcarine3.subprocess_wrapper.scp_classic(f,'192.168.37.158','airtogo','/home/aura_datas/carine_data/hd/val')
	#write_log.append_log(f)
	if (os.path.exists(full_utemp)):
		os.remove(full_utemp)
	
	f2=libcarine3.subprocess_wrapper.gdaldem(full_u,full_utemp)
	# libcarine3.merge_tools.merge_mask(f2)
	# f3=f2.replace('__','-')
	if (os.path.exists(full_u2)):
		os.remove(full_u2)
	# if (os.path.exists(f3)):
		# os.remove(f3)
	#msg=libcarine3.subprocess_wrapper.warp([full_utemp,full_u2,'-co','COMPRESS=DEFLATE','--config','GDAL_CACHEMAX','2048','-cutline','/home/previ/vector_source/aura_reg_3857.shp','-crop_to_cutline','-dstnodata','-9999'])
	msg=libcarine3.subprocess_wrapper.warp([full_utemp,full_u2,'-co','COMPRESS=DEFLATE','--config','GDAL_CACHEMAX','2048','-dstnodata','-9999'])
	#os.remove(f2)
	#libcarine3.subprocess_wrapper.scp_classic(full_u2,'dmz-previ','previ','/home/previ/geotiff')
	return HttpResponse(src.url())
@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')    
def merge_mi_fine(request):
	id_source=request.GET.get('id_source')
	id_prev=request.GET.get('id_prev')
	ratio=request.GET.get('ratio')
	src=Source.objects.get(id=id_source)
	prev=Prev.objects.get(id=id_prev)
	expertises = Expertise.objects.filter(target=src)
	r = libcarine3.Raster(src.url(), pol=config.from_name(src.tsr.pol),source=src)
	r.add_expertises(expertises)
	arr=libcarine3.merge_tools.merge_mi_fine(r,prev)
	arr=arr[0]
	mn=np.min(arr)
	mx=np.max(arr)
	shp=arr.shape
	return HttpResponse(r.to_png(arr,fn=None,dpi=100),content_type="image/png")
def mi_fine_url(request):
	id_source = request.GET.get('id_source')
	id_prev = request.GET.get('id_prev')
	u=reverse('merge_mi_fine')+'?id_source='+str(id_source) + '&id_prev='+str(id_prev) + '&randomnocache='+str(random.random())
	return HttpResponse(u)

def fake(request):
	a=subprocess_wrapper.fake('/var/www/html/hd/aura-no2-1508882400-0.tiff')
	return HttpResponse(a)

def preprocess_files(request):
	list_files=[]
	tsr=TypeSourceRaster.objects.filter(type='ada',intrun=0)
	tsp=timestamp.getTimestamp(0)
	for i in tsr :
		s=i.source_set.filter(daterun=tsp)
		for f in s:
			url=f.url_source()
			log.debug(url)
			msg=libcarine3.preprocessing.projcrop_ada(url)
   
	return HttpResponse(msg)
def ws_smile(request):
	ctx=Context.objects.get(active=True)
	if (ctx.previ_mod.launch_smile_prod != "''"):
		f= urllib.request.urlopen(ctx.previ_mod.launch_smile_prod)
	if (ctx.previ_mod.launch_smile_prod != "''"):
		f2= urllib.request.urlopen(ctx.previ_mod.launch_smile_preprod)
	return HttpResponse(ctx.previ_mod.launch_smile_prod)
	
def get_expertises(request):
	log.debug("  xxxxxxxxxxxxxxxxxxxx xxxxxxxxxxxxxxxxxxxx ")
	id_source=request.GET.get('id_source')
	log.debug(id_source)
	src=Source.objects.get(id=id_source)
	log.debug(src)
	exps=Expertise.objects.filter(target=src)
	ls={}
	for i in exps:
		ls[i.id]=dict(id=i.id,min=i.mn,max=i.mx,delta=i.delta,active=i.active)
	return JsonResponse(ls)
def set_expertises(request):
	id_exp=request.GET.get('id_exp')
	js_active = request.GET.get('active')
	active=''
	if (js_active=='true'):
		active=True
	else :
		active=False
	exp=Expertise.objects.get(id=id_exp)
	exp.active=active
	exp.save()
	exp=Expertise.objects.get(id=id_exp)
	return JsonResponse({id_exp : exp.active})
	
def get_legend(request):
	pol=request.GET.get('pol')

	html_lib='<tr>'
	html_c='<tr>'
	n=0
	vals=libcarine3.colors.get_vals(pol)
	for c in libcarine3.colors.colors[1:]:      
		html_lib+='<td class="td-legend-lib">'+str(vals[n])+'</td>'
		html_c+='<td data-toggle="tooltip" title="'+str(vals[n])+'" class="td-legend" style="background-color : '+c+';">'+'    '+'</td>'
		n+=1
	html_c+='</tr>'
	html_lib+='</tr>'
	return HttpResponse(html_lib+html_c)
def callback_merge(request):
	return HttpResponse('callback_merge')
def export_scp(request):
	ctx=Context.objects.get(active=True)
	polls=Polluant.objects.all()
	ech = Echeance.objects.all()
	tsp = timestamp.getTimestamp(0)
	out_type=DicoPath.objects.all()
	errors='fichier(s) inexistants : '
	urlss=[]
	for i in out_type:
		print(i.nom)
		remote_machine = RemoteMachine.objects.filter(type=i,active=True)
		output_data = OutputData.objects.get(type=i)
		urls = []
		for p in polls:
			print(p.nom)
			for e in ech:
				# print(e.delta)
				u=i.get_file_url(ctx.previ_mod.raster_prefix,str.lower(p.nom),tsp,e.delta+1)
				print(u)
				u_full=os.path.join(ctx.previ_mod.output_dir,os.path.join(output_data.dir,u))
				urls.append(u_full)
				# print('ctx.previ_mod.output_dir : '+ ctx.previ_mod.output_dir)
				# print('output_data.dir : ' + output_data.dir)
				print(u_full)
		for m in remote_machine:
			for u in urls:
				if os.path.exists(u):
					libcarine3.subprocess_wrapper.scp_classic(u,m.domaine,m.user,m.dir)
					time.sleep(1)
				else : 
					errors += u  + ' '
	
	if errors == 'fichier(s) inexistants : ':   
		return HttpResponse('export vers serveur de tuiles et api terminé')
	else :
		return HttpResponse('export vers serveur de tuiles et api terminé</br>' + errors)
		
def get_note(request):
	id = int(request.GET.get('id'))
	s=Source.objects.get(id=id)
	note = s.commentaire
	return HttpResponse(note)
def save_note(request):
	id=int(request.GET.get('id'))
	note = request.GET.get('commentaire')
	s=Source.objects.get(id=id)
	s.commentaire = note
	s.save()
	return HttpResponse('save  '  +note)