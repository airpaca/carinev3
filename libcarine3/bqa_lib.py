import logins
import config
import MySQLdb as msql
from raster.models import Source,Prev,Expertise
from libcarine3 import *
import libcarine3
import logging
import rasterio as rio
import numpy as np
import rasterstats
import affine
from rasterstats import zonal_stats
log = logging.getLogger('carinev3.libcarine3.bqa_lib')

def insert_BQA(dct):
    #bqa_log=logins.db_BQA_dev
    k=list(dct.keys())
    zone_id = k[0]
    echeance = list(dct[zone_id].keys())[0]
    o3=dct[zone_id][echeance]['indice_o3']
    no2=dct[zone_id][echeance]['indice_no2']
    pm10=dct[zone_id][echeance]['indice_pm10']
    multi=dct[zone_id][echeance]['indice_multipolluant']
    poll_id=dct[zone_id][echeance]['polluant_id']
    bd='transalpair.eu'
    #conn = msql.connect("host="+bqa_log['host']+ " port=3306" + " db="+bqa_log['dbname'] +  " user="+bqa_log['user']+" passwd=" + bqa_log['password'] )
    # conn = msql.connect(host=bd, port=3306 ,db="BQA" , user="BQA", passwd="BQA" )
    # cur=conn.cursor()
    # req = "INSERT INTO indices (zone_id,date,echeance,indice_o3,indice_no2,indice_pm10,indice_total,indice_dispositif,polluant_id) VALUES(" + str(zone_id) + ",CURDATE(),'"+echeance+"',"+str(o3) + ","+ str(no2) + "," + str(pm10) + ",0,"+ str(multi) + "," + str(poll_id)+");"
    # cur.execute(req)
    # res=cur.fetchall();
    # conn.close()
    if (echeance == 'J_moins_1'):
        conn = msql.connect(host=bd, port=3306 ,db="BQA" , user="BQA", passwd="BQA" )
        cur=conn.cursor()
        req = "INSERT INTO indices (zone_id,date,echeance,indice_o3,indice_no2,indice_pm10,indice_total,indice_dispositif,polluant_id) VALUES(" + str(zone_id) + ",DATE_ADD(CURDATE(), INTERVAL -1 DAY),'current',"+str(o3) + ","+ str(no2) + "," + str(pm10) + ",0,"+ str(multi) + "," + str(poll_id)+");"
        cur.execute(req)
        res=cur.fetchall();
        conn.close()
    if (echeance == 'J'):
        conn = msql.connect(host=bd, port=3306 ,db="BQA" , user="BQA", passwd="BQA" )
        cur=conn.cursor()
        req = "INSERT INTO indices (zone_id,date,echeance,indice_o3,indice_no2,indice_pm10,indice_total,indice_dispositif,polluant_id) VALUES(" + str(zone_id) + ",CURDATE(),'current',"+str(o3) + ","+ str(no2) + "," + str(pm10) + ",0,"+ str(multi) + "," + str(poll_id)+");"
        cur.execute(req)
        res=cur.fetchall();
        conn.close()
    if (echeance == 'J_plus_1'):
        conn = msql.connect(host=bd, port=3306 ,db="BQA" , user="BQA", passwd="BQA" )
        cur=conn.cursor()
        req = "INSERT INTO indices (zone_id,date,echeance,indice_o3,indice_no2,indice_pm10,indice_total,indice_dispositif,polluant_id) VALUES(" + str(zone_id) + ",DATE_ADD(CURDATE(), INTERVAL 1 DAY),'current',"+str(o3) + ","+ str(no2) + "," + str(pm10) + ",0,"+ str(multi) + "," + str(poll_id)+");"
        cur.execute(req)
        res=cur.fetchall();
        conn.close()
    #return res
def clean_bqa():
    bd='transalpair.eu'
    conn = msql.connect(host=bd, port=3306 ,db="BQA" , user="BQA", passwd="BQA" )
    cur=conn.cursor()
    req = "DELETE FROM indices WHERE date=CURDATE() OR date=DATE_ADD(CURDATE(), INTERVAL -1 DAY)  OR date=DATE_ADD(CURDATE(), INTERVAL +1 DAY)"
    cur.execute(req)
    
    conn.close()
def get_BQA(sql_req):
    bqa_log=logins.db_BQA_dev
    #conn = msql.connect("host="+bqa_log['host']+ " port=3306" + " db="+bqa_log['dbname'] +  " user="+bqa_log['user']+" passwd=" + bqa_log['password'] )
    conn = msql.connect(host="transalpair.eu", port=3306 ,db="BQA" , user="BQA", passwd="BQA" )
    cur=conn.cursor()
    cur.execute(sql_req)
    res=cur.fetchall();
    conn.close()
    return res
    
def calc_BQA(id_prev):
    prev=Prev.objects.get(id=id_prev)
    other_prevs=Prev.objects.filter(date_prev=prev.date_prev,ech=prev.ech)
    dct=dict()
    ids=[]
    vals={'indice_pm10':0,'indice_no2':0,'indice_o3' : 0 ,'indice_multipolluant':0, 'polluant_id' : 0}
    mx_ind=0
    for pr in other_prevs:
        ids.append(pr.id)
        id=pr.src.id
        """Raster as an image."""
        # TODO: ajouter transformation du raster en wgs84
        log.debug(id)
        ob=Source.objects.get(id=id)

        expertises = Expertise.objects.filter(target=ob)
        log.debug(expertises)
        
        # Read raster
        fnrst =ob.url_2154()
        log.debug(fnrst)
        r = libcarine3.Raster(fnrst, pol=config.from_name(ob.tsr.pol),source=ob,epsg=2154)
        b1=r.r.bounds
        res=100
        r.add_expertises(expertises)
        log.debug(r.expertises)
        data=r.get_array()
        if (ob.tsr.pol!='MULTI'):
            data=libcarine3.merge_tools.sous_indice(data,config.from_name(ob.tsr.pol))
        data=data.repeat(10,axis=0).repeat(10,axis=1)
        
        fpop=r'/home/previ/raster_source/pop/pop100m_2154.tif'
        ds= rio.open(fpop)

        aff=r.r.transform
        newaff = affine.Affine(aff.a / 10, aff.b, aff.c,aff.d, aff.e / 10, aff.f)
        disp=r'/home/previ/vector_source/disp_reg_aura.shp'
        zs_25 = zonal_stats(disp, data,raster_out=True,add_stats={'ibg_25':libcarine3.merge_tools.ibg_25},nodata=-999, affine=newaff,geojson_out=True)   
        zs_pop = zonal_stats(disp, ds.read(1),raster_out=True, affine=newaff,geojson_out=True, nodata=-999) 
        dct=dict()
        poll_ids={'indice_o3':  8 , 'indice_no2' : 3 , 'indice_pm10': 24}
        lib_ech=['J_moins_1','J','J_plus_1','J_plus_2']
        lib_zone=""
        for i in zs_25 :
            #pour ne travailler que sur grenoble
            if (i["properties"]["id_zone"])==2000:
                pop=i['properties']['pop_tr_sum']
                val=i['properties']['ibg_25']
                mini_aff=i['properties']['mini_raster_affine']
                mini_arr=i['properties']['mini_raster_array']
                mini_nodata=i['properties']['mini_raster_nodata']
                pp=mini_arr.shape
                for k in zs_pop:
                    id_zone=k['properties']['id_zone']
                    if (k['properties']['id_zone']==i['properties']['id_zone']):
                        pop_array = k['properties']['mini_raster_array']
                log.debug(np.max(pop_array))
                log.debug(pop)
                log.debug(np.sum(pop_array))
                log.debug(" ******** STATS ************" )
                log.debug(mini_arr.shape)
                log.debug(mini_aff)
                fl=np.ma.getdata(mini_arr).flat
                fl_sort=np.sort(fl)
                fl_argsort=np.argsort(fl)

                popsort=np.round(pop_array).flat[fl_argsort][::-1]
                log.debug(np.max(popsort))
                log.debug(np.max(pop))
                popw=popsort*100/pop
                log.debug(" ******** SUM popw ************" )
                cumul=0
                ib_10=0
                c=0
                for j in popw:
                    if (j > 0):
                        cumul+=j
                        if (cumul > 10 ):
                            ib_10=fl_sort[::-1][c]
                            break
                    c+=1  
                log.debug(" ******** boucle done ************" )                    
                # h=fl.shape[0]
                # w=fl.shape[1]
                # x1,y1 =int((mini_aff.c-newaff.c)/100),int((mini_aff.f-newaff.f)/100)
                # x2,y2 = int((mini_aff.c-newaff.c)/100)+w,int((mini_aff.f-newaff.f)/100)+h
                # win=windows.Window(x1,y1*-1,w,h)
                # warr=ds.read(1,window=win)
                # s=warr.shape
                # sum=np.sum((warr & mini_nodata))
                # fl=warr.flat  
                # srt=np.sort(fl)

                ind=max(val,ib_10)
                lib=""
                if (pr.pol.lower() =='multi') :
                    lib="indice_multipolluant"
                else :
                    lib = 'indice_'+pr.pol.lower()
                    if (ind > mx_ind):
                        mx_ind=ind
                        vals['polluant_id'] = poll_ids[lib]
                log.debug(" ******** vals done ************" )
                vals[lib]=ind
                lib_zone=i['properties']['lib_court_']
                log.debug(val)
                log.debug(ib_10)
    dct['2000']={lib_ech[pr.ech+1] : vals}
    insert_BQA(dct)
    return dct