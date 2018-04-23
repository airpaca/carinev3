from pyproj import Proj,transform
import rasterio as rio
from rasterio import windows, features
import logging
import numpy as np
import math
import affine
import shapely.geometry as sgeo
from shapely.geometry import shape
from functools import partial
import pyproj
from shapely.ops import transform
from libcarine3 import write_log
# Log
log = logging.getLogger('carinev3.raster.api_web_views')
def to_3857(x,y):
    inProj = Proj(init='epsg:4326')
    outProj = Proj(init='epsg:3857')
    x_dest,y_dest = pyproj.transform(inProj,outProj,x,y)
    return [x_dest,y_dest]
def to_4326(x,y):
    inProj = Proj(init='epsg:3857')
    outProj = Proj(init='epsg:4326')
    x_dest,y_dest = pyproj.transform(inProj,outProj,x,y)
    return [x_dest,y_dest]
def intersect_bounds(x,y,bounds):
    is_within=False
    if (x > bounds[0]):#left
        if (x < bounds[2]):#right
            if (y > bounds[1]):#bottom
                if (y < bounds[3]):#top
                    is_within = True
    return is_within
             
def get_value(url,x,y):
    #rewrite de la source du meme nom de rio (rio.sample.sample_gen) 
    ds=rio.open(url)
    bounds = ds.bounds
    l=bounds[0]
    intersects=intersect_bounds(x,y,bounds)
    if intersects:
        x0=int((x-ds.transform.c)/14.25)
        y0=int((ds.transform.f-y)/14.25)

        w=rio.windows.Window(x0,y0,1,1)
        d=ds.read(1,window=w)
        
        if d.shape:
            val =d[0][0]
            log.debug(d.shape)
            return(val)
    else :
        return -1
def get_value_any(url,x,y):
    #rewrite de la source du meme nom de rio (rio.sample.sample_gen) 
    ds=rio.open(url)

    res=ds.transform.a

    x0=int((x-ds.transform.c)/res)
    y0=int((ds.transform.f-y)/res)
    log.debug(x0)
    log.debug(y0)
    w=rio.windows.Window(x0,y0,1,1)
    d=ds.read(1,window=w)
    log.debug(w)
    val =d[0][0]
    log.debug(d.shape)
    return(val)    
def get_square_buff(url,x,y,size):
    #rewrite de la source du meme nom de rio (rio.sample.sample_gen)

    ds=rio.open(url)
    x=float(x)
    y=float(y)
    co=to_3857(x,y)
    x,y=co[0],co[1]
    size=int(size)
    block_offset = int((size-1)/2)

    x0=int((x-ds.transform.c)/14.25) - block_offset
    y0=int((ds.transform.f-y)/14.25) - block_offset

    w=rio.windows.Window(x0,y0,size,size)

    block=ds.read(1,window=w)

    return(block)

    
def iter_increment(url,x,y):
    #rewrite de la source du meme nom de rio (rio.sample.sample_gen)

    ds=rio.open(url)

    # init value
    x0=int((x-ds.transform.c)/14.25)
    y0=int((ds.transform.f-y)/14.25)
    # log.debug(x0)
    # log.debug(y0)
    w=rio.windows.Window(x0,y0,1,1)
    d=ds.read(1,window=w)
    # log.debug(w)
    
    #init_val = valeur seuil (ex : pour 37: init_val = 30, pour 73: init_val = 70)
    init_val =int(((d[0][0])/10))*10
    if (init_val <= 10):
        #ben oui si on est déjà dans la classe minimum..
        return 0
    elif (init_val > 49):
        init_val = 49
    val=init_val
    size=3
    increment = 400
    rectifx0min=0
    rectify0min=0
    rectifx0max=0
    rectify0max=0
    while val >= init_val:
        block_offset = int((size-1)/2)
        xoff=int((x-ds.transform.c)/14.25) 
        x0 = xoff - block_offset
        yoff=int((ds.transform.f-y)/14.25) 
        y0 = yoff - block_offset
        #cas ou ca depasse de la carte:
        
        if (x0 < 0):
            rectifx0min=x0*-1
            x0=0
        
        if ((xoff + block_offset) > ds.width):
            rectifx0max=(xoff + block_offset)-ds.width
            
        
        if (y0 < 0):
            rectify0min=y0*-1
            y0=0
        if ((yoff + block_offset) > ds.height):
            rectify0max=(yoff + block_offset)-ds.height
            
        w=rio.windows.Window(x0,y0,size-rectifx0max,size - rectify0max)
        block=ds.read(1,window=w)
        block = (block > 0)*block + ((block <=0 )*1000)
        val = np.min(block)
        if (size > 10000):
            return 0
        else :
            size+=increment
    size = size -  (increment * 2)
    val=init_val
    
    b=np.lib.pad(block,((rectify0min,rectify0max),(rectifx0min,rectifx0max)),'constant')
 
    # if (init_val>49) :
        # init_val=49
    block_co = get_closest(b,init_val)
    
    offset_x = block_co[1] - (b.shape[1]-1)/2
    # log.debug(offset_x)
    offset_y = block_co[0] - (b.shape[1]-1)/2
    # log.debug(offset_y)
    world_co = to_4326(x+(offset_x*14.25),y-(offset_y*14.25))
    
    return(world_co)
def get_closest(block,val):
    block = (block<=0)*1000+(block > 0)*block
    mask=np.where(block < val)
    x=mask[0]
    y=mask[1]
    # log.debug(x)
    # log.debug(y)
    o=(block.shape[1]-1)/2
    #log.debug(xo)
    dist=(x-o)*(x-o) + (y-o)*(y-o)
    i=np.argsort(dist)[0]
    ind=[x[i],y[i]]
    return ind
    
def interp_ls(ls,interval,url):
    a=to_3857(ls[0][0],ls[0][1])
    b=to_3857(ls[1][0],ls[1][1])
    v=[b[0]-a[0],b[1]-a[1]]
    d = math.sqrt(v[0]*v[0] + v[1]*v[1])
    ratio = interval/d
    n=int(d/interval)
    vals=[get_value(url,a[0],a[1])]
    log.debug(d)
    for i in range(1,n):
        log.debug(i)
        px=a[0]+v[0]*(ratio*i)
        py=a[1]+v[1]*(ratio*i)
        vals.append(get_value(url,px,py))
    vals.append(get_value(url,px,py))
    return vals

def rast_mls(url,mls):
    project = partial(
        pyproj.transform,
        pyproj.Proj(init='epsg:4326'), # source coordinate system
        pyproj.Proj(init='epsg:3857'))

    ds =rio.open(url)
    aff=ds.transform
    shp=shape(mls)
    geom = transform(project,shp)
    l_tot = geom.length
    if (l_tot > 0 ):
        dct=dict(segments=[],moyenne=0)
        vals=0
        for ls in geom : 
            l=ls.length
            if ( l < 21.375):
                mean=get_value(url,ls.bounds[0],ls.bounds[1])
                vals+=round((mean * round((l/l_tot),2)),1)
                log.debug(vals)
                dct["segments"].append(mean)
                write_log.append_log(" ___________________________ ")
            else :
                write_log.append_log(" ___________________________ ")
                bounds=ls.bounds # left bot right top
                x=bounds
                x0=int((bounds[0]-ds.transform.c)/14.25)
                y0=int((ds.transform.f-bounds[3])/14.25)
                new_w = int((bounds[2] - bounds[0])/14.25) + 1
                new_h = int((bounds[3] - bounds[1])/14.25) + 1
                new_aff = affine.Affine(aff.a,aff.b,aff.c + x0*14.25,aff.d,aff.e,aff.f-y0*14.25)
                w=rio.windows.Window(x0,y0,new_w,new_h)
                rast = features.rasterize(shapes=[ls],
                                          out_shape=(new_h,new_w),
                                          transform=new_aff,default_value=1,
                                          all_touched=False)
                arr=ds.read(1,window = w)
                sel=rast * arr
                mean = round((np.sum(sel)/np.sum(rast > 0 )),1)

                vals+=round((mean * round((l/l_tot),2)),1)
                log.debug(vals)
                dct["segments"].append(mean)
    else :
        vals=0
        dct=dict(segments=[],moyenne=0)
        dct["segments"].append(0)
    dct['moyenne']=vals
    return dct

