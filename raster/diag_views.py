import os
from django.http import HttpResponse, JsonResponse,HttpResponseRedirect
from .models import *
import libcarine3

def check_mod(request):
    # verifie les arrivées de mod et renvoie un json avec tous les fichiers et un msg conseil
    # msg = json : {nomfichier / heure création / taille / status} - conseil
    t=libcarine3.timestamp.getTimestamp(0)
    s=Source.objects.filter(daterun = t)
    dct={}
    for i in s:
        url=i.url()
        url_2154 =i.url_2154()
        url_src = i.url_source()
        if i.tsr.pol.lower() != 'multi':
            if i.tsr.type.lower() == 'ada':
                if os.path.exists(url_src):
                    stat=os.stat(url_src)
                    if (stat[6] < 50000):
                        status="WARNING"
                        msg="Taille trop basse, erreur probable,essayer de voir avec mod si il y a des problèmes sur la chaîne de prévi"
                    else :
                        status = "OK"
                        msg="RAS"
                    dct[i.id] = dict({'3857' : dict(url=url_src, size = stat[6], modif= stat[8], status = status, msg = msg)})
                    print(dct)
                else :
                    msg = "Pas de fichier sur le serveur, vérifier si il reste de la place sur la machine puis contacter mod"
                    dct[i.id]=dict({'3857' : dict(url=url_src, size =0, modif= 0, status = "ERROR", msg = msg)})
                if os.path.exists(url_2154):                      
                    stat=os.stat(url_2154)
                    if (stat[6] < 50000):
                        status="WARNING"
                        msg="Taille trop basse, erreur probable, essayez de regénérer les sources ou de voir avec mod si il y a des problèmes sur la chaîne de prévi"
                    else :
                        status = "OK"
                        msg="RAS"
                    dct[i.id] = dict({'2154' : dict(url=url_2154, size = stat[6], modif= stat[8], status = status, msg = msg)})
                    print(dct)
                else :
                    msg = "Pas de fichier sur le serveur, vérifier si il 1) la source correspondante est dispo, si oui vérifier la place et regénérer les sources, sinon vérifiez d'abord la place dispo sur la machine puis contactez mod,"
                    dct[i.id] = dict({'2154' : dict(url=url_2154, size =0, modif= 0, status = "ERROR", msg = msg)})
                if os.path.exists(url):
                    stat=os.stat(url)
                    if (stat[6] < 50000):
                        status="WARNING"
                        msg="Taille trop basse, erreur probable, essayez de regénérer les sources ou de voir avec mod si il y a des problèmes sur la chaîne de prévi"
                    else :
                        status = "OK"
                        msg="RAS"
                    dct[i.id] = dict({'3857' : dict(url=url, size = stat[6], modif= stat[8], status = status, msg = msg)})
                    print(dct)
                else :
                    msg = "Pas de fichier sur le serveur, vérifier si il 1) la source correspondante est dispo, si oui vérifier la place et regénérer les sources, sinon vérifiez d'abord la place dispo sur la machine puis contactez mod,"
                    dct[i.id]=dict({'3857' : dict(url=url, size =0, modif= 0, status = "ERROR", msg = msg)})
        # else :
                # print(i.url_2154() + ' => INACCESSIBLE')

    return JsonResponse(dct)

# def check_multi(request):
    # return JsonResponse()
# def check_dalles_fines(request):
    # return JsonResponse()
def check_outputs(request):
    t=libcarine3.timestamp.getTimestamp(0)
    prevs = Prev.objects.filter(date_prev = t)
    dct={}
    for i in prevs:
        dct[i.id] = i.get_urls()
        for k,v in dct.items():
            print(k)

            if os.path.exists(v['url']):
                dct[i.id]['exists']=True
            else :
                dct[i.id]['exists']=False
    return JsonResponse(dct)
# def check_low_rgb(request):
    # return JsonResponse()
# def check_hd(request):
    # return JsonResponse()
# def check_ibg(request):
    # return JsonResponse()