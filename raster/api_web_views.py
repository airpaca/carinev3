# -*- coding: utf-8 -*-
from libcarine3 import timestamp,api_web_lib
import os
import config
from django.http import HttpResponse, JsonResponse
import logging
from raster.models import Source,Prev
import numpy as np
import json
from shapely.geometry import shape,MultiLineString
# Log
log = logging.getLogger('carinev3.raster.api_web_views')
def indice_request(request):
    x = request.GET.get('x')
    y = request.GET.get('y')
    log.debug(x)
    log.debug(y)
    tsp=timestamp.getTimestamp(0)
    url_basename='val/'+config.aasqa + "-multi-" + str(tsp) + '-1-ind.tiff'
    url = os.path.join(config.hd_path,url_basename)
    log.debug(url)
    if (os.path.exists(url)) != True:
        tsp=timestamp.getTimestamp(1)
        url_basename='val/'+config.raster_prefix.lower() + "-multi-" + str(tsp) + '-2-ind.tiff'
        url = os.path.join(config.hd_path,url_basename)
        log.debug(url)
        if (os.path.exists(url)) != True:
            return HttpResponse("Aucune des dates n'est disponible")
    
    xy_3857= api_web_lib.to_3857(x,y)
    val=api_web_lib.get_value(url,xy_3857[0],xy_3857[1])
    if val < 0 :
        return JsonResponse(dict())
    else : 
        return JsonResponse(dict(indice_multipolluant=dict(valeur=int(val))))
def indice_request_full(request):
    x = request.GET.get('x')
    y = request.GET.get('y')
    xy_3857= api_web_lib.to_3857(x,y)
    tsp=timestamp.getTimestamp(0)
    tsp_hier=timestamp.getTimestamp(1)
    polls={'multi':'indice_multipolluant','pm10':'sous_indice_pm10','no2':'sous_indice_no2','o3' : 'sous_indice_o3'}
    lib_ech=["indice_jm1","indice_j","indice_jp1"]
    dct=dict(
        indice_jm1=dict(
            indice_multipolluant=0,
            sous_indice_pm10=0,
            sous_indice_no2=0,
            sous_indice_o3=0
        ),
        indice_j=dict(
            indice_multipolluant=0,
            sous_indice_pm10=0,
            sous_indice_no2=0,
            sous_indice_o3=0
        ),
        indice_jp1=dict(
            indice_multipolluant=0,
            sous_indice_pm10=0,
            sous_indice_no2=0,
            sous_indice_o3=0
        )
    )
    for e in range(0,3):
        for p in polls:
            url=''
            url_basename='val/'+config.aasqa + "-" + p + "-" + str(tsp) + '-'+str(e) +"-"+'ind.tiff'
            url = os.path.join(config.hd_path,url_basename)     
            log.debug(url)
            if (os.path.exists(url) == False):
                url_basename='val/'+config.aasqa + "-" + p + "-" + str(tsp_hier) + '-'+str(e+1) +'-ind.tiff'
                url = os.path.join(config.hd_path,url_basename)
                log.debug(url)
            val=api_web_lib.get_value(url,xy_3857[0],xy_3857[1])
            if val < 0 :
                return JsonResponse(dict())
            else : 
                dct[lib_ech[e]][polls[p]]=int(val)
    return JsonResponse(dct)
    
def indice_request_unique(request):
    x = request.GET.get('x')
    y = request.GET.get('y')
    pol=request.GET.get('pol')
    ech=int(request.GET.get('ech'))
    tsp=int(request.GET.get('date'))
    log.debug(x)
    log.debug(y)
    prev=Prev.objects.get(pol=pol.upper(),ech=ech-1,date_prev=tsp)

    #devrait implémenté comme mé&thode de la classe prev
    url_basename='val/'+config.aasqa + "-"+ pol + "-" + str(tsp) + '-' + str(ech) + '-ind.tiff'
    url = os.path.join(config.hd_path,url_basename)
    if (os.path.exists(url)) != True:
        return HttpResponse(url + " non disponible")
    
    xy_3857= api_web_lib.to_3857(x,y)
    val=api_web_lib.get_value(url,xy_3857[0],xy_3857[1])
    if val < 0 :
        return JsonResponse(dict())
    else : 
        return JsonResponse(dict(pol=pol,valeur=int(val)))
    
def best_prox_qa(request):
    x = request.GET.get('x')
    y = request.GET.get('y')
    tsp=timestamp.getTimestamp(0)
    url_basename='val/'+config.aasqa + "-multi-" + str(tsp) + '-1-ind.tiff'
    url = os.path.join(config.hd_path,url_basename)
    log.debug(url)
    if (os.path.exists(url)) != True:
        tsp=timestamp.getTimestamp(1)
        url_basename='val/'+config.raster_prefix.lower() + "-multi-" + str(tsp) + '-2-ind.tiff'
        url = os.path.join(config.hd_path,url_basename)
        log.debug(url)
        if (os.path.exists(url)) != True:
            return HttpResponse("Aucune des dates n'est disponible")
    
    co = api_web_lib.to_3857(x,y)
    val=api_web_lib.get_value(url,co[0],co[1])
    if val < 20 :
        return JsonResponse(dict())
    else : 
        vals=api_web_lib.iter_increment(url,co[0],co[1])
        if (vals==0):
            return JsonResponse(dict())
        else :
            bestCoords=api_web_lib.to_3857(vals[0],vals[1])
            bestQA=api_web_lib.get_value(url,bestCoords[0],bestCoords[1])
        return JsonResponse(dict(position = dict(latitude = vals[1], longitude = vals[0]),indice_j = dict(valeur = int(bestQA))))
    
def get_square_buff(request):
    x = request.GET.get('x')
    y = request.GET.get('y')
    url = request.GET.get('url')
    size = request.GET.get('size')
    b=api_web_lib.get_square_buff(url,x,y,size)
    return HttpResponse(np.max(b))
    
def get_pixel_any(request):
    x = request.GET.get('x')
    y = request.GET.get('y')
    pol=request.GET.get('pol')
    ech=int(request.GET.get('ech'))
    tsp=int(request.GET.get('date'))
    log.debug(x)
    log.debug(y)
    prev=Prev.objects.get(pol=pol.upper(),ech=ech-1,date_prev=tsp)

    #devrait implémenté comme mé&thode de la classe prev
    url_basename='val/'+config.aasqa + "-"+ pol + "-" + str(tsp) + '-' + str(ech) + '.tiff'
    url = os.path.join(config.basse_def_val_path,url_basename)
    if (os.path.exists(url)) != True:
        return HttpResponse(url + " non disponible")
    
    xy_3857= api_web_lib.to_3857(x,y)
    val=api_web_lib.get_value_any(url,xy_3857[0],xy_3857[1])
    return JsonResponse(dict(pol=pol,valeur=int(val)))
def trajet_request(request):

    tsp=timestamp.getTimestamp(0)
    tsp_hier=timestamp.getTimestamp(1)
    r = request.method
    rb=request.body
    a=request.body.decode('utf8')
    mls=json.loads(a)['features'][0]['geometry']
    polls={'multi':'indice_multipolluant','pm10':'sous_indice_pm10','no2':'sous_indice_no2','o3' : 'sous_indice_o3'}
    lib_ech=["indice_jm1","indice_j","indice_jp1"]
    lib_moy=['moyenne_jm1','moyenne_j','moyenne_jp1']
    dct=dict(segments = [])
    for e in range(0,3):
        lib_e=lib_ech[e]

        url=''
        url_basename='val/'+config.aasqa + "-multi-" + str(tsp) + '-'+str(e) +'-ind.tiff'
        url = os.path.join(config.hd_path,url_basename)     
        log.debug(url)
        if (os.path.exists(url) == False):
            url_basename='val/'+config.aasqa + "-multi-" + str(tsp_hier) + '-'+str(e+1) +'-ind.tiff'
            url = os.path.join(config.hd_path,url_basename)
            log.debug(url)
        all= api_web_lib.rast_mls(url,mls)
        segments=all["segments"]
        for k in range(0,len(segments)):
            if len(dct["segments"])<= k :
                dct["segments"].append(dict(
                        indice_jm1=dict(
                            indice_multipolluant=0,
                            sous_indice_pm10=0,
                            sous_indice_no2=0,
                            sous_indice_o3=0
                        ),
                        indice_j=dict(
                            indice_multipolluant=0,
                            sous_indice_pm10=0,
                            sous_indice_no2=0,
                            sous_indice_o3=0
                        ),
                        indice_jp1=dict(
                            indice_multipolluant=0,
                            sous_indice_pm10=0,
                            sous_indice_no2=0,
                            sous_indice_o3=0
                        )
                    )
                )
            dct['segments'][k][lib_e]["indice_multipolluant"]=float(segments[k])
            dct[lib_moy[e]] = float(all["moyenne"])
                
        
        #dct[lib_ech[ech]]=mean
    return JsonResponse(dct)