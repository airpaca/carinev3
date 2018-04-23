from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .models import Prev
from django.http import HttpResponse, JsonResponse,HttpResponseRedirect
from libcarine3 import timestamp,bqa_lib

@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')
@never_cache
def launch_BQA(request):
    bqa_lib.clean_bqa()
    prevs=Prev.objects.filter(date_prev=timestamp.getTimestamp(0),pol='MULTI')
    for p in prevs:
        bqa_lib.calc_BQA(p.id)
    return HttpResponse('Insert Transalpair terminé')
def launch_BQA_unique(request):
    #bqa_lib.clean_bqa()
    id_prev = request.GET.get('id_prev')
    res = bqa_lib.calc_BQA(id_prev)
    return JsonResponse(res)