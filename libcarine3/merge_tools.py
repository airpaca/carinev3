import os
import numpy as np
import config
import rasterio as rio
import config
import logging
import raster
from rasterio import merge,windows
from rasterio.windows import from_bounds
import affine
from rasterio.io import MemoryFile
from raster.models import Prev,Polluant
log = logging.getLogger('libcarinev3.raster')

def merge_method(m,arrs):
    m_auth=['max']
    if (m not in m_auth):
        print('method inconnue, peut rien faire.... try again')
    else:
        new_arr=np.zeros(arrs[0].shape)
        for i in arrs:
            log.debug('---------- MERGE MAX ---------')
            log.debug(i.shape)
            log.debug(new_arr.shape)
            new_arr=np.maximum(new_arr,i)
        return new_arr
        
def sous_indice(arr,poll):
    ALE=config.ALE[poll]
    INFO=config.VLS[poll]
    log.debug (" ---------- MIN / MAX -------------")
    log.debug(np.min(arr))
    log.debug(np.max(arr))
    log.debug(arr.dtype)

    data=(((arr<0)*0)+((arr>=0)*(arr<(INFO/5)))*((arr*10)/(INFO/5))+((arr>=(INFO/5))*(arr<=INFO))*(((arr*100)/INFO)-10)+((arr>INFO)*(90+(arr-INFO)*10/(ALE-INFO)))+(((arr/ALE)>1)*100))
    log.debug(np.min(data))
    log.debug(np.max(data))
    log.debug(data.dtype)
    
    return data   
# Si [P]< INFOP/5 : Ip = 10*[P]/( INFOP/5) 
# •Si [P] ≤ INFOP : IP = ([P]*100/INFOP) -10
# •Si [P] ≤ INFOP : IP = ([P]*100/INFOP) -10
# •Si [P] > INFOP : IP = 90+([P]-INFOP)*10/(ALEP-INFOP) 
def rasterize(poly, rstshape, rstaff):

    shapes = ((g, 1) for g in [poly])
    rbuf = features.rasterize(shapes=shapes,
                              out_shape=rstshape,
                              transform=rstaff
                              )
    return rstshape
    
    
    

        
        
def warp(argz):
    """with a def you can easily change your subprocess call"""
    # command construction with binary and options
    options = ['gdalwarp']
    options.extend(argz)
    # call gdalwarp 
    subprocess.check_call(options)
def ic(x):
    return np.sum((x>90)*x)
    
def surf_exp(x):
    #0.01=km²
    
    return np.extract(x,x>0).shape
    
def pop_exp(x):
    return (np.extract)
def export_ratio(rast,ratio,prev):
    with rio.Env(GDAL_CACHEMAX=12000,NUM_THREADS='ALL_CPUS') as env:
        ech = prev.ech
        tsp=prev.date_prev
        pol=prev.pol
        
        pr = rast.r.profile

        new_file = '/var/www/html/hd/aura-' + pol.lower() + '-' + str(tsp) + '-' + str(ech+1) + '.tiff'        
        ar=rast.r.read(1)
        new_ar = rast.get_array()
        shp=new_ar.shape
        new_ar=new_ar.repeat(ratio,axis=0).repeat(ratio,axis=1)
        shp2=new_ar.shape
        pr.update(height = pr['height'] * ratio)
        pr.update(width = pr['width']  * ratio)
        aff=rast.r.transform
        new_aff = affine.Affine(aff.a / ratio, aff.b, aff.c,aff.d, aff.e / ratio, aff.f)  
        pr.update(transform=new_aff)
        prh=pr['height']
        prw=pr['width']
        with rio.open(new_file,'w',**pr) as dst:
            dst.write(new_ar,1)
            dst.close()

def merge_fine(rast,prev):
    with rio.Env(GDAL_CACHEMAX=16384,NUM_THREADS='ALL_CPUS') as env:
        log = logging.getLogger('carinev3.raster.views')
        ech = prev.ech
        tsp=prev.date_prev
        pol=prev.pol
        ratio=100
        urls=[]
        pol_int=config.from_name(pol)
        pr=rast.r.profile
        b1=rast.r.bounds
        aff=rast.r.transform
        new_file = config.hd_path + config.aasqa+ '_' + pol.lower() + '_' + str(tsp) + '_' + str(ech+1) + '.tiff' 
        
        ar=rast.get_array()
        if (pol.upper() != 'MULTI'):
            ar=sous_indice(ar,pol_int).astype('uint8')
        else:
            ar = ar.astype('uint8')
        s=ar.shape
        log.debug(s)
        new_ar=ar.repeat(ratio,axis=0).repeat(ratio,axis=1)
        new_ar=new_ar.astype('uint8')
        log.debug(new_ar.shape)
        ar=None
        
        pr.update(height = pr['height'] * ratio)
        pr.update(width = pr['width']  * ratio)

        new_aff = affine.Affine(aff.a / ratio, aff.b, aff.c,aff.d, aff.e / ratio, aff.f)
        pr.update(transform=new_aff)
        prh=pr['height']
        prw=pr['width']
        
        if (pol.upper() != 'MULTI'):

            lib_ech=config.libs_ech[ech]
            dir = '/home/previ/raster_source/domaines_fine/3857/'           
            for i in config.domaines_hd:
                url=dir+'AURA_'+pol.upper()+'_'+i+'_'+str(tsp)+'_'+lib_ech+'_3857.tif'
                if (os.path.exists(url)):
                    urls.append(url) 
                else : 
                    log.debug(url)
        
        res=14.25
        w1=rio.windows.from_bounds(b1[0],b1[1],b1[2],b1[3],pr['transform'],boundless=True)
        log.debug(w1)
        w4=None
        pr.update(dtype='uint8')
        log.debug('---min')
        log.debug(np.min(new_ar))
        with MemoryFile() as memfile:
            with memfile.open(**pr) as dataset:
                dataset.write(new_ar,1)
                new_ar=None
                mem_arr = dataset.read().astype('uint8')
                for f2 in urls:
                    ds2=rio.open(f2)
                    b2=ds2.bounds
                    log.debug(b2)
                    ox=abs((b2[0]-b1[0])/res)
                    oy=abs((b2[3]-b1[3])/res)
                    w2=rio.windows.from_bounds(b2[0],b2[1],b2[2],b2[3],ds2.transform,boundless=True)
                    log.debug("=== w2 ===")
                    print(w2)
                    w3=rio.windows.intersection(w1,w2)
                    log.debug("=== w3 ===")
                    log.debug(w3)
                    w4=((int(w3[0][0]+oy),int(w3[0][1]+oy)),(int(w3[1][0]+ox),int(w3[1][1]+ox)))
                    log.debug("=== w4 ===")
                    log.debug(w4)
                    warr=dataset.read(1,window=w4)
                    log.debug("=== warrshape ===")
                    log.debug(warr.shape)
                    ar2=sous_indice(ds2.read(),pol_int).astype('uint8')
                    warr=np.maximum(warr,ar2)
                    print("=== w4 ===")
                    print([w4[0][0],w4[0][1],w4[1][0],w4[1][1]])
                    mem_arr[0][w4[0][0]:w4[0][1],w4[1][0]:w4[1][1]]=warr
                    log.debug(warr.shape)
                    

                    print(mem_arr.shape)
                    log.debug(ds2.profile)
                    warr=None
                    ds2.close()

                with rio.Env(GDAL_CACHEMAX=16384,NUM_THREADS='ALL_CPUS') as env2:
                    with rio.open(new_file,'w',**pr) as dst:

                        # r=((mem_arr<=10)*0)+(((mem_arr>10)*(mem_arr<=20)) *92) +(((mem_arr>20)*(mem_arr<=30)) * 153)+(((mem_arr>30)*(mem_arr<=40)) * 195)+((mem_arr>40)*(mem_arr<=50)) * 255+((mem_arr>50)*(mem_arr<=60)) * 255+((mem_arr>60)*(mem_arr<=70)) * 255+((mem_arr>70)*(mem_arr<=80)) * 255+((mem_arr>80)*(mem_arr<=90)) * 255+((mem_arr>90)*(mem_arr<=100)) * 255+((mem_arr>100)*127)
                        # r=r.astype('uint8')
                        # g=((mem_arr<=10)*204)+((mem_arr>10)*(mem_arr<=20)) * 203+((mem_arr>20)*(mem_arr<=30)) * 230+((mem_arr>30)*(mem_arr<=40)) * 240+((mem_arr>40)*(mem_arr<=50)) * 255+((mem_arr>50)*(mem_arr<=60)) * 209+((mem_arr>60)*(mem_arr<=70)) * 170+((mem_arr>70)*(mem_arr<=80)) * 94+((mem_arr>80)*(mem_arr<=90)) * 0+((mem_arr>90)*(mem_arr<=100)) * 0+((mem_arr>100)*0)
                        # g=g.astype('uint8')
                        # b=((mem_arr<=10)*170)+((mem_arr>10)*(mem_arr<=20)) * 96+((mem_arr>20)*0)
                        # b=b.astype('uint8')
                        #for k, arr_rgb in [(1, b), (2, g), (3, r)]:
                        dst.write(mem_arr)
                        dst.close()
                
        mem_arr=None
        dataset.close()
        memfile=None
        return new_file
def merge_mi_fine(rast,prev):
    log = logging.getLogger('carinev3.raster.views')
    ech = prev.ech
    tsp=prev.date_prev
    pol=prev.pol
    ratio=50
    urls=[]

    pr=rast.r.profile
    b1=rast.r.bounds
    aff=rast.r.transform
    new_file = config.hd_path + config.aasqa+ '_' + pol.lower() + '_' + str(tsp) + '_' + str(ech+1) + '.tiff'
    pol_int=config.from_name(pol)
    ar=rast.get_array()
    if (pol.upper() != 'MULTI'):
        ar=sous_indice(ar,pol_int).astype('uint8')
    else:
        ar = ar.astype('uint8')
    s=ar.shape
    log.debug(s)
    new_ar=ar.repeat(ratio,axis=0).repeat(ratio,axis=1)
    log.debug(new_ar.shape)
    ar=None
    
    pr.update(height = pr['height'] * ratio)
    pr.update(width = pr['width']  * ratio)

    new_aff = affine.Affine(aff.a / ratio, aff.b, aff.c,aff.d, aff.e / ratio, aff.f)  
    pr.update(transform=new_aff)
    prh=pr['height']
    prw=pr['width']
    
    if (pol.upper() != 'MULTI'):

        lib_ech=config.libs_ech[ech]
        dir = '/home/previ/raster_source/domaines_fine/3857/'           
        for i in config.domaines_hd:
            url=dir+'AURA_'+pol.upper()+'_'+i+'_'+str(tsp)+'_'+lib_ech+'_3857.tif'
            urls.append(url)            
    
    res=28.5
    w1=rio.windows.from_bounds(b1[0],b1[1],b1[2],b1[3],pr['transform'],boundless=True)
    log.debug(w1)
    w4=None
    log.debug(pr)
    pr.update(dtype='uint8')
    with MemoryFile() as memfile:
        with memfile.open(**pr) as dataset:
            dataset.write(new_ar,1)
            new_ar=None
            mem_arr = dataset.read()
            for f2 in urls:
                if (os.path.exists(f2)):
                    ds2=rio.open(f2)
                    b2=ds2.bounds
                    log.debug(b2)
                    ox=abs((b2[0]-b1[0])/res)
                    oy=abs((b2[3]-b1[3])/res)
                    w2=rio.windows.from_bounds(b2[0],b2[1],b2[2],b2[3],ds2.transform,boundless=True)
                    log.debug("=== w2 ===")
                    print(w2)
                    w3=rio.windows.intersection(w1,w2)
                    log.debug("=== w3 ===")
                    log.debug(w3)
                    w4=((int(w3[0][0]+oy),int(w3[0][1]+oy)),(int(w3[1][0]+ox),int(w3[1][1]+ox)))
                    log.debug("=== w4 ===")
                    log.debug(w4)
                    warr=dataset.read(1,window=w4)
                    log.debug("=== warrshape ===")
                    log.debug(warr.shape)
                    ar2=sous_indice(ds2.read(),pol_int).astype('uint8')
                    warr=np.maximum(warr,ar2)
                    print("=== w4 ===")
                    print([w4[0][0],w4[0][1],w4[1][0],w4[1][1]])
                    mem_arr[0][w4[0][0]:w4[0][1],w4[1][0]:w4[1][1]]=warr
                    log.debug(warr.shape)
                    

                    print(mem_arr.shape)
                    log.debug(ds2.profile)
                    warr=None
                    ds2.close()
            with rio.open(new_file,'w',**pr) as dst:
                dst.write(mem_arr)
                dst.close()
    mem_arr=None
    dataset.close()
    memfile=None
    return new_file