import os
from raster.models import *

def clear_date_prev():
    query_set=DatePrev.objects.all()
    for i in query_set:
        i.delete()
    print(len(DatePrev.objects.all()))
    return len(DatePrev.objects.all())
def clear_prev():
    query_set=Prev.objects.all()
    for i in query_set:
        i.delete()
    print(len(Prev.objects.all()))
    return len(Prev.objects.all())
def clear_source():
    query_set=Source.objects.all()
    for i in query_set:
        i.delete()
    print(len(Source.objects.all()))
    return len(Source.objects.all())
def clear_tsr():
    query_set=TypeSourceRaster.objects.all()
    for i in query_set:
        i.delete()
    print(len(TypeSourceRaster.objects.all()))
    return len(TypeSourceRaster.objects.all())
def clear_expertise():
    query_set=Expertise.objects.all()
    for i in query_set:
        i.delete()
    print(len(Expertise.objects.all()))
    return len(Expertise.objects.all())
def clear_indice_com():
    query_set=IndiceCom.objects.all()
    for i in query_set:
        i.delete()
    print(len(IndiceCom.objects.all()))
    return len(IndiceCom.objects.all())
def clear_depassement_reg():
    query_set=DepassementReg.objects.all()
    for i in query_set:
        i.delete()
    print(len(DepassementReg.objects.all()))
    return len(DepassementReg.objects.all())    
def clear_all():
    clear_depassement_reg()
    clear_indice_com()
    clear_expertise()
    clear_prev()
    clear_date_prev()
    clear_source()
    clear_tsr()
    