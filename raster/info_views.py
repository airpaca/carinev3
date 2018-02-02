import os
from django.http import HttpResponse, JsonResponse,HttpResponseRedirect
from .models import *
import libcarine3
from libcarine3 import timestamp
import config,logins
def get_sources(request):
    type=request.GET.get('type')
    date=request.GET.get('date')
    tsp=libcarine3.timestamp.getTimestampFromDate(date)
    
    tsr=TypeSourceRaster.objects.filter(type=type)
    
    dct=dict()
    for i in tsr:
        src=Source.objects.get(tsr=i,daterun=tsp)
        dct[src.id] = {'source' : '','2154' : '','3857' : ''}
        if (os.path.exists(src.url())):
            dct[src.id]['source']=src.url()
        if (os.path.exists(src.url_2154())):
            dct[src.id]['2154']=src.url_2154()
        if (os.path.exists(src.url())):
            dct[src.id]['3857']=os.stat(src.url())
    return JsonResponse(dct)