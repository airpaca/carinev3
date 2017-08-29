import logging
import datetime
import json
import psycopg2
import rasterio as rio
import datetime
import fiona
from pyproj import Proj,transform
from django.views.decorators.http import require_POST
from django.template import loader
from django.http import HttpResponse, JsonResponse
from .models import Expertise,TypeSourceRaster,Source,Prev
import libcarine3
from libcarine3 import timestamp,merge_tools,api
import config,logins
import django.utils.timezone as tz
import os
import itertools
from django.views.decorators.cache import never_cache
import urllib.request

# Log
log = logging.getLogger('carinev3.raster.views')


# Pour le test
DATE_TEST = datetime.date(2017,6,7)


# Views
def index(request):
    """Index."""
    template = loader.get_template('raster/index.html')
    context = {}
    return HttpResponse(template.render(context, request))


def application_js(request):
    """Application (Javascript)."""
    template = loader.get_template('raster/application.map.js')
    context = {}
    return HttpResponse(template.render(context, request))
# def init_once(request):
    # ls={}
    # tsr=TypeSourceRaster.objects.all()
    # for i in tsr:
        # if (i.intrun==1):
            # s=Source(tsr=i)
            # s.daterun=libcarine3.timestamp.getTimestamp(1)
            # s.is_source=i.is_default_source
            # s.statut=s.checkStatut()
            # s.save()
            # ls[s.id]=s.json
    # return JsonResponse(ls)
def get_init_info(request):
    
    infos=dict(polls=config.polls,echs=config.echs_diff)
    ls={}
    d=libcarine3.timestamp.getTimestamp(0)
    p=Prev.objects.filter(date_prev=d)
    for i in p:
        ls[i.id]=[i.pol,i.ech]
    return JsonResponse(ls)
def init_today(request,run):
    x=int(run)
    d=libcarine3.timestamp.getTimestamp(x)
    p=Prev.objects.filter(date_prev=d)
    if (len(p)==0):
        for p in config.polls:
            for e in config.echs_diff:
                pr=Prev(date_prev=d,ech=e,pol=p)
                pr.save()

        ls={}
        tsr=TypeSourceRaster.objects.all()
        for i in tsr:
            if (i.intrun==x):
                s=Source(tsr=i,daterun=d)
                s.statut=s.checkStatut()
                s.save()
                if (i.is_default_source):
                    p=i.pol
                    e=i.ech
                    prev=Prev.objects.get(date_prev=d,pol=p,ech=e)
                    prev.src=s
                    prev.save()
                ls[s.id]=s.json()
    return HttpResponse('Nb dinstance de Prev : ' + str(len(p)))
    #a priori garde fou plus necessaire si tout est géré dynamiquement par rapport a config.polls/ech
    #elif (len(p)==(len(config.polls)*len(config.echs_diff))) :
def check_statut(request):
    ls={}
    src0=Source.objects.filter(daterun=libcarine3.timestamp.getTimestamp(0))
    src1=Source.objects.filter(daterun=libcarine3.timestamp.getTimestamp(1))
    src2=Source.objects.filter(daterun=libcarine3.timestamp.getTimestamp(2))
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
def check_sources(request):
    p=Prev.objects.filter(date_prev=libcarine3.timestamp.getTimestamp(0))
    ls={}
    for i in p:
        ls[i.id]=i.src.id
    return JsonResponse(ls)    
def source_url(request):
    tsr=TypeSourceRaster.objects.all()
    ls={}
    for t in tsr:
        ls[t.id]=t.json
    return  JsonResponse(ls)
def update_source(request,id_prev,id):
    prev=Prev.objects.get(id=id_prev)
    source=Source.objects.get(id=id)
    prev.src=source
    prev.save()
    
    return HttpResponse(Prev.objects.get(id=id_prev).src.id)

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
@never_cache
def img_raster(request,id):
    """Raster as an image."""
    # TODO: ajouter transformation du raster en wgs84
    log.debug(id)
    ob=Source.objects.get(id=id)
    # if (ob.tsr.pol=='MULTI'):
        # ech=ob.tsr.ech
        # srcs=Prev.objects.filter(ech=ech,date_prev=libcarine3.timestamp.getTimestamp(0))
        # arr_list=[]
        # for i in srcs:
            # log.debug(i)
            # if (i.pol!='MULTI'):
                # r = libcarine3.Raster(i.src.url(), pol=config.from_name(i.pol))
                # data=r.get_array()
                # data=libcarine3.merge_tools.sous_indice(data,config.from_name(i.pol))
                # arr_list.append(data)           
        # new_arr=libcarine3.merge_tools.merge_method('max',arr_list)
        # return HttpResponse(libcarine3.raster.to_png(new_arr,None,75), content_type="image/png")
    # else :
        # Read database and check for expertise

    expertises = Expertise.objects.filter(target=ob)
    log.debug(expertises)
    
    # Read raster
    fnrst =ob.url()
    log.debug(fnrst)
    
    r = libcarine3.Raster(fnrst, pol=config.from_name(ob.tsr.pol))
    r.add_expertises(expertises)
    log.debug(r.expertises)
    data=r.get_array()
    log.debug(data)
    # Return image
    return HttpResponse(r.to_png(data,None,100), content_type="image/png")
def info_raster(request,id):
    ob=Source.objects.get(id=id)
    url=ob.url()
    pol=config.from_name(ob.tsr.pol)
    ds=rio.open(url)
    arr=ds.read(1)
    ss_ind=''
    if (pol!=10):
        ss_ind=libcarine3.merge_tools.sous_indice(arr,pol)
    pr=ds.profile
    ds.close()
    return JsonResponse({'height':pr['height'],'width':pr['width'],'driver':pr['driver'],'transform':pr['transform']})

def img_multi(request,ech):
#implementé direct dans img_raster,
# sert a tester direct la fonction, a virer si vraiment on s'en sert jamais
    ech=int(ech)-1
    srcs=Prev.objects.filter(ech=ech,date_prev=libcarine3.timestamp.getTimestamp(0))
    arr_list=[]
    for i in srcs:    
        if (i.pol!='MULTI'):
            log.debug(i.pol)
            r = libcarine3.Raster(i.src.url(), pol=config.from_name(i.pol))
            data=r.get_array()
            #data=libcarine3.merge_tools.sous_indice(data,config.from_name(i.pol))
            arr_list.append(data)
            
    new_arr=libcarine3.merge_tools.merge_method('max',arr_list)
    fn=Prev.objects.get(ech=ech,date_prev=libcarine3.timestamp.getTimestamp(0),pol='MULTI').src.url()
    src_crs = {'init': 'EPSG:3857'}
    with rio.open(fn,'w',count=1,dtype='float64',driver='GTiff',crs=src_crs, height=config.profile['height'],width=config.profile['width'],transform=config.profile['transform']) as dst:
        dst.write(new_arr,1)
        dst.close()
    return HttpResponse(libcarine3.raster.to_png(new_arr,None,300), content_type="image/png")
def sites_fixes(request):
    conn = psycopg2.connect("host="+logins.host+  " dbname="+logins.dbname +  " user="+logins.user+" password=" + logins.password )
    cur=conn.cursor()
    req = "select id_site,nom_site,st_X(st_transform(" + config.geom_field + ",4326))as x,st_Y(st_transform(" + config.geom_field + ",4326)) as y from sites_fixes"
    cur.execute(req)
    res=cur.fetchall();
    conn.close()
    liste_sites=[]
    for i in res:
    
        #liste_site.append(str)
        row={"type": "Feature","geometry": {"type": "Point","coordinates": [i[2],i[3]]},"properties": {"nom" : i[1]},"id_site": i[0]}
        liste_sites.append(row)
        

    str={"type": "FeatureCollection","features": liste_sites}   
    return JsonResponse(str)
def reg_aura(request):
    conn = psycopg2.connect("host="+logins.host+  " dbname="+logins.dbname +  " user="+logins.user+" password=" + logins.password )
    cur=conn.cursor()
    if config.aasqa == "atmoaura":
        req = "select id_zone,lib_zone,st_asgeojson(st_transform(" + config.geom_field + ",4326)) as the_geom from zones where id_zone=2038 or id_zone=0"
    elif config.aasqa == "airpaca":
        req = "select id_zone,lib_zone,st_asgeojson(st_transform(" + config.geom_field + ",4326)) as the_geom from zones where id_zone=0"
    cur.execute(req)
    res=cur.fetchall();
    conn.close()
    liste_sites=[]
    for i in res :
        row={"type": "Feature","geometry": {"type": "MultiPolygon","coordinates": json.loads(i[2])['coordinates']},"properties": {"nom" : i[1]},"id_reg": i[0]}
        liste_sites.append(row)

    return JsonResponse(liste_sites,safe=False)
def epci_aura(request):
    conn = psycopg2.connect("host="+logins.host+  " dbname="+logins.dbname +  " user="+logins.user+" password=" + logins.password )
    cur=conn.cursor()
    req = "select id_zone,lib_zone,st_asgeojson(" + config.geom_field + ") as " + config.geom_field + " from temp_epci_2017_aura_4326"
    cur.execute(req)
    res=cur.fetchall();
    conn.close()
    liste_sites=[]
    for i in res :
        row={"type": "Feature","geometry": {"type": "MultiPolygon","coordinates": json.loads(i[2])['coordinates']},"properties": {"nom" : i[1]},"id_epci": i[0]}
        liste_sites.append(row)
    return JsonResponse(liste_sites,safe=False)

def bbox_raster(request, id):
    """Bounding box of the raster."""

    #defaut_id == id d'une instance de Source a prendre pr MULTI
    ob=Source.objects.get(id=id)
    #a moins d'ecrire direct en dur chaque indice multi, on prend la default bbox pr multi)

    fnrst =ob.url()
    r = libcarine3.Raster(fnrst, pol=config.from_name(ob.tsr.pol))
    x1, y1, x2, y2 = r.bbox

    inProj = Proj(init='epsg:3857')
    outProj = Proj(init='epsg:4326')
    xmin,ymin = transform(inProj,outProj,x1,y1)
    xmax,ymax = transform(inProj,outProj,x2,y2)
    return JsonResponse(dict(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax))

#TODO modif avec obj tsr
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
def test_ajax(request):
   
    b=request.body
    
    
    return HttpResponse(b) 
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
    coords=coords+[coords[0]]

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
    
    e = Expertise(target=src, delta=val, geom=geom, mn=corr_min, mx=corr_max, ssup=corr_ssup)
    e.save()

    return JsonResponse(dict(one='uh'))
def get_pixel(request,id,x,y):

    ob=Source.objects.get(id=id)
    expertises = Expertise.objects.filter(target=ob)
    # Read raster
    fnrst =ob.url()

    r = libcarine3.Raster(fnrst, pol=config.from_name(ob.tsr.pol))
    r.add_expertises(expertises)
    x=int(x)/1000000.0
    y=int(y)/1000000.0
    inProj = Proj(init='epsg:4326')
    outProj = Proj(init='epsg:3857')
    x_dest,y_dest = transform(inProj,outProj,x,y)

    v=r.sample_gen(x_dest,y_dest)
    
    return JsonResponse(dict(val=v))
def get_indice_com(request):
    url="http://carine.air-rhonealpes.fr/index.php/rasterize/getMunicipalValues?date=2016-04-13&ech=0"
    response = urllib.request.urlopen(url)
    html = response.read().decode('utf-8')
    json_obj = json.loads(html)
    ls=[]
    c=0
    for i in json_obj:
        ls.append(dict(code_commune=i['code_commune'],indice=i['indice']))
        c+=1
    return HttpResponse(ls)
def get_commentaire(request):
    return Json
