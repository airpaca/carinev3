import logging
import datetime
import json
from django.views.decorators.http import require_POST
from django.template import loader
from django.http import HttpResponse, JsonResponse
from .models import Expertise
import libcarine3
import config


# Log
log = logging.getLogger('carinev3.raster.views')


# Pour le test
DATE_TEST = datetime.date(2017, 5, 15)


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


def img_raster(request, pol, ech):
    """Raster as an image."""
    # TODO: ajouter transformation du raster en wgs84

    daterun = datetime.date.today()
    daterun = DATE_TEST  # test

    # Read database and check for expertise
    expertises = Expertise.objects.filter(daterun=daterun, pol=pol, ech=ech)
    log.debug(expertises)

    # Read raster
    fnrst = config.get_raster_path(daterun, pol, int(ech))
    r = libcarine3.Raster(fnrst, pol=libcarine3.from_name(pol))

    # Apply expertise
    for expertise in expertises:
        r.alter(expertise.delta, expertise.geom)

    # Return image
    return HttpResponse(r.to_png(dpi=75), content_type="image/png")


def bbox_raster(request, pol, ech):
    """Bounding box of the raster."""

    daterun = datetime.date.today()
    daterun = DATE_TEST  # test

    fnrst = config.get_raster_path(daterun, pol, int(ech))
    r = libcarine3.Raster(fnrst, pol=libcarine3.from_name(pol))

    xmin, ymin, xmax, ymax = r.bbox
    return JsonResponse(dict(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax))


def list_modifications(request, pol, ech):
    """Liste des modifications."""
    daterun = datetime.date.today()
    objs = Expertise.objects.filter(daterun=daterun, pol=pol, ech=ech)
    data = dict(daterun=daterun, pol=pol, ech=int(ech),
                modifs=[e.json for e in objs])
    return JsonResponse(data)


@require_POST
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
    pol = data.get('pol')
    ech = data.get('ech')
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
