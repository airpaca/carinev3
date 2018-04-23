import os
import numpy as np
import config
import rasterio as rio
import config
import logging
import libcarine3
from libcarine3 import colors
import raster
from rasterio import merge,windows
from rasterio.windows import from_bounds
import affine
from raster import dashboardfine_views
from rasterio.io import MemoryFile
from raster.models import Prev,Polluant,Expertise,Source,DalleFine,Echeance
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
    np.ma.set_fill_value(arr,0)
    ALE=config.ALE[poll]
    INFO=config.VLS[poll]
    log.debug (" ---------- MIN / MAX -------------")
    data=np.round_(arr,2)
    log.debug(np.min(arr))
    log.debug(np.max(arr))
    log.debug(arr.dtype)

    data=np.round((
        ((arr<0)*255)+
        ((arr>=0)*(arr<(INFO/5)))*((arr*10)/(INFO/5))+
        ((arr>=(INFO/5))*(arr<=INFO))*(((arr*100)/INFO)-10)+
        (((arr>INFO)*((arr/ALE)<1))*(90+(arr-INFO)*10/(ALE-INFO)))+
        (((arr/ALE)>1)*100)
        ),2).astype('float32')
    log.debug(np.min(data))
    log.debug(np.max(data))
    log.debug(data.dtype)
    return data
def arr_to_tif(arr):
    shape=arr.shape
    # r = np.zeros(shape=shape,dtype='uint8')
    # g = np.zeros(shape=shape,dtype='uint8')
    mx=np.max(arr)
    mn=np.min(arr)
    r=((arr>0)*255).astype(rio.uint8)
    g=((arr>0)*255).astype(rio.uint8)
    b=((arr>0)*0).astype(rio.uint8)
    return [r,g,b]

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

def ibg_25(arr):
    z=np.ma.getdata(arr)
    tri=np.sort(z.flat)
    x=tri[-2500]
    return x
def ibg_10(arr):
    z=np.ma.getdata(arr)
    tri=np.sort(z.flat)
    
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

def merge_fine(rast,prev,new_file):
    with rio.Env(GDAL_CACHEMAX=16384,NUM_THREADS='ALL_CPUS') as env:
        log = logging.getLogger('carinev3.raster.views')
        ech = prev.ech
        tsp=prev.date_prev
        pol=prev.pol
        ratio=100
        urls=[]
        pol_int=config.from_name(pol)
        pr=rast.r.profile
        meta=rast.r.meta
        b1=rast.r.bounds
        aff=rast.r.transform
        #new_file = config.hd_path + config.aasqa+ '_' + pol.lower() + '_' + str(tsp) + '_' + str(ech+1) + '.tiff'

        ar2=rast.get_array()
        print(np.min(ar2))
        # ar2 = (ar2 > 0)*ar2 + (ar2<0)*255
        # print(np.min(ar2))
        ar=ar2



        print(np.min(ar))
        log.debug(np.min(ar))
        if (pol.upper() != 'MULTI'):
            ar=sous_indice(ar,pol_int).astype('uint8')
        else:
            ar = ar.astype('uint8')
        print(np.min(ar))
        s=ar.shape
        log.debug(s)
        new_ar=ar.repeat(ratio,axis=0).repeat(ratio,axis=1)
        new_ar=new_ar.astype('uint8')
        print(np.min(ar))
        log.debug(new_ar.shape)
        ar=None

        pr.update(height = pr['height'] * ratio)
        pr.update(width = pr['width']  * ratio)
        meta.update(height = meta['height'] * ratio)
        meta.update(width = meta['width']  * ratio)
        new_aff = affine.Affine(aff.a / ratio, aff.b, aff.c,aff.d, aff.e / ratio, aff.f)
        meta.update(transform=new_aff)
        pr.update(transform=new_aff)
        prh=pr['height']
        prw=pr['width']
        eObj = Echeance.objects.filter(libInt=str(ech))
        pObj = Polluant.objects.filter(nom=pol.upper())
        

        urls = dashboardfine_views.get_fine_url_merge(prev.id)


        res=14.25
        w1=rio.windows.from_bounds(b1[0],b1[1],b1[2],b1[3],pr['transform'],boundless=True)
        log.debug(w1)
        w4=None
        pr.update(dtype='uint8')
        pr.update(nodata=0)
        meta.update(dtype='uint8')
        meta.update(nodata=0)
        log.debug('---min')
        log.debug(np.min(new_ar))
        new_ar=new_ar.reshape(1,new_ar.shape[0],new_ar.shape[1])
        for f2 in urls:

            if (os.path.exists(f2)):
                log.debug("------------------ PROCESSING LOW-DEF  : "+ f2 + "  ------------")
                lib_pol = os.path.basename(f2).split('_')[1].upper()
                log.debug(lib_pol)
                pol_low=config.from_name(lib_pol)
                log.debug(pol_low)
                date_prev = prev.date_prev

                f2_prev=Prev.objects.get(date_prev=date_prev,pol=lib_pol,ech=prev.ech)
                src=f2_prev.src
                log.debug(src.url())
                exp=Expertise.objects.filter(target=src)
                log.debug(exp)
                ds2=rio.open(f2)
                print(ds2.profile)
                #a refactorer quand tout tournera bien, là on a 1 dataset + 1 raster .. (qui contient un dataset redondant)
                r2=libcarine3.Raster(f2,config.from_name(lib_pol.upper()))
                r2.add_expertises(exp)
                get_ar=r2.get_array()

                b2=ds2.bounds
                log.debug(b2)
                ox=abs((b2[0]-b1[0])/res)
                oy=abs((b2[3]-b1[3])/res)
                w2=rio.windows.from_bounds(b2[0],b2[1],b2[2],b2[3],ds2.transform,boundless=True)

                w3=rio.windows.intersection(w1,w2)

                w4=((int(w3[0][0]+oy),int(w3[0][1]+oy)),(int(w3[1][0]+ox),int(w3[1][1]+ox)))
                sh=new_ar.shape
                warr=new_ar[0][w4[0][0]:w4[0][1],w4[1][0]:w4[1][1]]




                ar2=sous_indice(get_ar,pol_low).astype('uint8')
                ar2=(ar2 <255)*ar2
                warr=np.maximum(warr,ar2)
                print("=== w4 ===")
                print([w4[0][0],w4[0][1],w4[1][0],w4[1][1]])
                
                new_ar[0][w4[0][0]:w4[0][1],w4[1][0]:w4[1][1]]=warr
                log.debug(warr.shape)
                print(new_ar.shape)
                log.debug(ds2.profile)
                warr=None
                ds2.close()
        pr.update(dtype='uint8')
        pr.update(nodata=255)
        with rio.open(new_file,'w',**pr) as dst:
            log.debug(' ---- dst write --- ' )
            dst.write(new_ar)
            dst.close()
        # mx=np.max(new_ar)
        # mn=np.min(new_ar)
        # pr['count']=3
        # rgb=arr_to_tif(new_ar)
        # with rio.open(new_file[0], 'w', **pr) as dst:
            # log.debug(new_ar.astype(rio.uint8).shape)
            # dst.write(rgb[0].astype(rio.uint8),indexes=1)
            # dst.write(rgb[0].astype(rio.uint8),indexes=2)
            # dst.write(rgb[0].astype(rio.uint8),indexes=3)
        # rast.to_png(new_ar[0],new_file,dpi=100)
        ar2=None

        return new_file
def merge_mask(f):
    ds = rio.open(f)
    r=ds.read(1)
    pr=ds.profile
    print(pr)
    m=u'/var/www/html/hd/mask_reg_10m_def.tif'
    ds_mask = rio.open(m)
    new_file = '/var/www/html/hd/test.tif'
    
    with rio.open(new_file,'w',**pr) as dst:
        log.debug(' ---- dst write --- ' )
        r=ds.read(1)
        dst.write(r,1)
        r=None
        g=ds.read(2)
        dst.write(g,2)
        g=None
        b=ds.read(3)
        dst.write(b,3)
        b=None
        # m_ar=ds_mask.read(1)
        # dst.write(m_ar,4)
        dst.close()
def merge_mi_fine(rast,prev):
    with rio.Env(GDAL_CACHEMAX=16384,NUM_THREADS='ALL_CPUS') as env:
        log = logging.getLogger('carinev3.raster.views')
        ech = prev.ech
        tsp=prev.date_prev
        pol=prev.pol
        ratio=20
        urls=[]
        pol_int=config.from_name(pol)
        pr=rast.r.profile
        b1=rast.r.bounds
        aff=rast.r.transform
        new_file = config.hd_path + config.aasqa+ '_' + pol.lower() + '_' + str(tsp) + '_' + str(ech+1) + '.tiff'

        ar=rast.get_array()
        log.debug(np.min(ar))
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

            lib_ech=config.libs_ech[ech+1]
            dir = '/home/previ/raster_source/domaines_fine/3857/custom/'
            for i in config.domaines_hd:
                url=dir+'AURA_'+pol.upper()+'_'+i+'_'+str(tsp)+'_'+lib_ech+'_3857_custom.tif'
                if (os.path.exists(url)):
                    urls.append(url)
                else :
                    log.debug(url)
        else :
            lib_ech=config.libs_ech[ech+1]
            dir = '/home/previ/raster_source/domaines_fine/3857/custom/'
            for i in config.domaines_hd:
                for p in Polluant.objects.all():
                    url=dir+'AURA_'+p.nom.upper()+'_'+i+'_'+str(tsp)+'_'+lib_ech+'_3857_custom.tif'
                    if (os.path.exists(url)):
                        urls.append(url)
                    else :
                        log.debug(url)

        res=71.25
        w1=rio.windows.from_bounds(b1[0],b1[1],b1[2],b1[3],pr['transform'],boundless=True)
        log.debug(w1)

        pr.update(dtype='uint8')
        pr.update(nodata=0)
        log.debug('---min')
        log.debug(np.min(new_ar))

        with MemoryFile() as memfile:
            with memfile.open(**pr) as dataset:
                dataset.write(new_ar,1)
                new_ar=None
                mem_arr = dataset.read()
                for f2 in urls:
                    log.debug("------------------ PROCESSING LOW-DEF  : "+ f2 + "  ------------")
                    lib_pol = os.path.basename(f2).split('_')[1].upper()
                    log.debug(lib_pol)
                    pol_low=config.from_name(lib_pol)
                    log.debug(pol_low)
                    date_prev = prev.date_prev

                    f2_prev=Prev.objects.get(date_prev=date_prev,pol=lib_pol,ech=prev.ech)
                    src=f2_prev.src
                    log.debug(src.url())
                    exp=Expertise.objects.filter(target=src)
                    log.debug(exp)
                    ds2=rio.open(f2)
                    #a refactorer quand tout tournera bien, là on a 1 dataset + 1 raster .. (qui contient un dataset redondant)
                    r2=libcarine3.Raster(f2,config.from_name(lib_pol.upper()))
                    r2.add_expertises(exp)
                    get_ar=r2.get_array()

                    b2=ds2.bounds
                    log.debug(b2)
                    ox=abs((b2[0]-b1[0])/res)
                    oy=abs((b2[3]-b1[3])/res)
                    w2=rio.windows.from_bounds(b2[0],b2[1],b2[2],b2[3],ds2.transform,boundless=True)

                    w3=rio.windows.intersection(w1,w2)

                    w4=((int(w3[0][0]+oy),int(w3[0][1]+oy)),(int(w3[1][0]+ox),int(w3[1][1]+ox)))
                    log.debug(w4)
                    log.debug(mem_arr.shape)
                    warr=mem_arr[0][w4[0][0]:w4[0][1],w4[1][0]:w4[1][1]]
                    log.debug(warr.shape)


                    ar2=sous_indice(get_ar,pol_low).astype('uint8')
                    ar_sh=ar2.shape
                    warr=np.maximum(warr,ar2)
                    print("=== w4 ===")
                    print([w4[0][0],w4[0][1],w4[1][0],w4[1][1]])
                    mem_arr[0][w4[0][0]:w4[0][1],w4[1][0]:w4[1][1]]=warr
                    log.debug(warr.shape)


                    print(mem_arr.shape)
                    log.debug(ds2.profile)
                    warr=None
                    ds2.close()

                return mem_arr