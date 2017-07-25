import logging
import datetime
import json
import psycopg2
import rasterio

from django.views.decorators.http import require_POST
from django.template import loader
from django.http import HttpResponse, JsonResponse
from .models import Expertise,TypeSourceRaster
import libcarine3
import config,logins

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

def source_url(request):
    tsr=TypeSourceRaster.objects.all()
    ls={}
    for t in tsr:
        t.statut=t.checkStatut()
        ls[t.id]=t.json
    return  JsonResponse(ls)
def check_statut(request,id):
    ob=TypeSourceRaster.objects.filter(id=id)[0]
    statut = ob.checkStatut()
    return HttpResponse(statut)
def getMoreSources(request,id):
	ob=TypeSourceRaster.objects.filter(id=id)[0]
	samepoll=TypeSourceRaster.objects.filter(pol=ob.pol)
	sameech=TypeSourceRaster.objects.filter(ech=ob.ech)
	samerun=TypeSourceRaster.objects.filter(intrun=ob.intrun)
	#pas trouvé de moyen plus simple mais bon, ça fait le boulot:
	#on recup toutes les sources dispo pour le même pol/ech/run
	obs={}
	for i in samepoll:
		if i in sameech:
			if i in samerun:
				i.statut=i.checkStatut()
				obs[i.id]=i.json
	return JsonResponse(obs)
def img_raster(request,id):
    """Raster as an image."""
    # TODO: ajouter transformation du raster en wgs84
    log.debug(id)
    ob=TypeSourceRaster.objects.filter(id=id)[0]
    
    # Read database and check for expertise
    expertises = Expertise.objects.filter(id_source=ob)
    log.debug(expertises)

    # Read raster
    fnrst =ob.url()
    log.debug(fnrst)
    r = libcarine3.Raster(fnrst, pol=config.from_name(ob.pol))
    r.add_expertises(expertises)
    
    # Return image
    return HttpResponse(r.to_png(None,300), content_type="image/png")
def sites_fixes(request):
    conn = psycopg2.connect("host="+logins.host+  " dbname="+logins.dbname +  " user="+logins.user+" password=" + logins.password )
    cur=conn.cursor()
    req = "select id_site,nom_site,st_X(st_transform(the_geom,4326))as x,st_Y(st_transform(the_geom,4326)) as y from sites_fixes"
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
    req = "select id_zone,lib_zone,st_asgeojson(st_transform(the_geom,4326)) as the_geom from zones where id_zone=2038 or id_zone=0"
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
    req = "select id_zone,lib_zone,st_asgeojson(the_geom) as the_geom from temp_epci_2017_aura_4326"
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
    ob=TypeSourceRaster.objects.filter(id=id)[0]

    fnrst =ob.url()
    r = libcarine3.Raster(fnrst, pol=config.from_name(ob.pol))


    xmin, ymin, xmax, ymax = r.bbox
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


@require_POST
#TODO modif obj tsr
def alter_raster(request):
    """Route to alter the raster."""

    def error(message):
        """Return a error JSON response."""
        log.error(message)
        return JsonResponse({'status': 'error', 'message': message},
                            status=400)

    dr = datetime.date.today()

    # Get data
    if not request.body:
        return error("Missing data from request.")

    print(request.body)
    data = json.loads(request.body)
    id = data.get('id')
    modifs = data.get('modifs')

    # Check data
    if pol is None or ech is None or modifs is None:
        return error('missing parameters')

    # Insert data into database
    for modif in modifs:
        geom_type = modif['geom']['type']
        coords = modif['geom']['coordinates']

        if geom_type == 'Point':
            x, y = coords
            geom = f'POINT({x} {y})'

        elif geom_type == 'Polygon':
            strcoord = ", ".join([f"{x} {y}" for (x, y) in coords[0]])
            geom = f'POLYGON(({strcoord}))'

        else:
            return error('error in parameters')

        # Create objects
        e = Expertise(daterun=dr, pol=pol, ech=ech, delta=modif['delta'],
                      geom=geom)
        e.save()

    return JsonResponse({'status': 'ok'})
