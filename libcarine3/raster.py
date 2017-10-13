#!/usr/bin/env python3
# coding: utf-8

"""Carine v3 :: raster"""


import io
import logging
import rasterio as rio
from rasterio import features
import numpy as np
import matplotlib.pyplot as plt
import libcarine3
from libcarine3 import colors
import config
import os
from raster import models
import affine
from rasterio.io import MemoryFile
log = logging.getLogger('libcarinev3.raster')


def rasterize_zt(poly, rstshape, rstaff):
    """Création d'un raster d'une zone tampon autour d'un polygone.
    
    :param poly: Polygon.
    :param distance: distance.
    :param rstshape: shape of output.
    :param rstaff: transformation of raster.
    :return: np.array.
    """
    pbuf = poly
    log.debug(poly)
   
    shapes = ((g, 255) for g in [pbuf])
    # log.debug("------------------------------------------------------------------")
    # log.debug(next(shapes))
    rbuf = features.rasterize(shapes=shapes,
                              out_shape=rstshape,
                              transform=rstaff,default_value=1,
                              all_touched=True)

    return rbuf
# def rasterize(poly, rstshape, rstaff):

    # shapes = ((g, 1) for g in [poly])
    # rbuf = features.rasterize(shapes=shapes,
                              # out_shape=rstshape,
                              # transform=rstaff,
                              # all_touched=True)
    # return rbuf
def to_png(data, fn=None, dpi=10):
    """Convert raster into png format.
    
    :param fn: path and filename of output png file or None
    :param dpi:
    :return: None or Pillow.Image if fn is None.
    """


    # Limits
    #data[(data > -999) & (data < 0)] = 0

    # Create figure
    log.debug("ljhf")
    figsize = (data.shape[1] /dpi, data.shape[0]/dpi)
    log.debug(figsize)
    fig = plt.figure(frameon=False, figsize=figsize,dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')

    # Echelle de couleurs
    cmap = libcarine3.colors.discrete_cmap(libcarine3.colors.colors)
    vmin = 0
    vmax = np.max(data)


    plt.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax,clim=(0.0,10.0))
    log.debug("creating plot done!")

    # Export sous forme d'image
    f = open(fn, 'wb') if fn else io.BytesIO()

    fig.canvas.print_png(f)

    fig.clf()

    plt.close()
    if fn:
        f.close()
        log.debug(f"save image to {fn}")
    else:
        log.debug("return image data...")
        return f.getvalue()

class Raster:
    """Raster."""

    def __init__(self, fn, pol,source):
        """Raster.
        
        :param fn: path and filename of a raster.
        :param pol: pollutant id.
        """
        
        self.fn = fn

        self.r = rio.open(self.fn, 'r')
        
        if pol not in config.POLLUTANTS:
            log.error("cannot reconize pollutant! " + pol)
            raise libcarine3.Carinev3Error("cannot reconize pollutant! " + pol)
        self.pol = pol
        self.expertises = list()
        self.source=source

    def __del__(self):
        """Close raster."""
        self.r.close()

    @property
    def xs(self):
        x0 = self.r.affine.c
        nx = self.r.width
        dx = self.r.affine.a
        return np.arange(x0, x0 + nx * dx, dx)

    @property
    def ys(self):
        y0 = self.r.affine.f
        ny = self.r.height
        dy = self.r.affine.e
        return np.arange(y0, y0 + ny * dy , dy)

    @property
    def x(self):
        x, _ = np.meshgrid(self.xs, self.ys)
        return x

    @property
    def y(self):
        _, y = np.meshgrid(self.xs, self.ys)
        return y
        
    def get_array(self):
        data = self.r.read(1)
        mask = (data == self.r.nodata)
        shape=self.r.shape
        aff=self.r.affine
        self.r.close()
        data = np.ma.array(data, mask=mask)
        del mask
        log.debug(f"read data from raster {self.fn}")

        # Apply modifications
        for expertise in self.expertises:
            log.debug("**************** EXPERTISE *********************")
            log.debug(expertise)
            modif = np.zeros(data.shape)
            if expertise.ssup:
                mk_ssup = (modif+expertise.delta) <= expertise.ssup
            else:
                mk_ssup = (data > 0)
            # Use mask if mn or mx
            # FIXME: comment faire le traitement avec les bornes min et max
            if expertise.smin:
                mk_smin = (data + expertise.delta > expertise.mn)
            else : 
                mk_smin = (data > 0)
                
            if expertise.mn:
                mk_mn = (data >= expertise.mn)
            else:
                mk_mn = (data > 0)
               
            if expertise.mx:
                mk_mx = (data <= expertise.mx)
            else:
                mk_mx = (data > 0)
                
            if expertise.geom.geom_type == 'Point':
                g = libcarine3.Point(*expertise.geom.coords, epsg=4326)

            elif expertise.geom.geom_type == 'Polygon':
                g = libcarine3.Polygon(expertise.geom.coords[0], epsg=3857)

            else:
                raise NotImplementedError()

            # Définition des zones tampons pour la décroissance
            # ztlims, ztxs, ztys = libcarine3.zt_sigmoide(d=10000, n=30)

            # ztlims = list(ztlims[1:][::-1]) + [0]
            # ztys = list(ztys[::-1]) + [1]
            #for d, pc in zip(ztlims, ztys):
            rbuf = rasterize_zt(g,  shape, aff)
            log.debug("--------------------------------------------------------------------------------rbuf.shape--------------------------------------------------------------")
            log.debug(rbuf.shape)
            log.debug(np.max(rbuf))
            
            
            modif[(rbuf == 255) & mk_mn & mk_mx & mk_ssup & mk_smin] = expertise.delta
            data += modif


        #data=libcarine3.sous_indice(data,self.pol)
        #log.debug(f"apply modification {expertise.delta:+} in {g.wkt}")

        # if (self.pol!=10):
            # data=libcarine3.merge_tools.sous_indice(data,self.pol)
        return data
    def sample_gen(self, x,y, indexes=None):
        #rewrite de la source du meme nom de rio (rio.sample.sample_gen) 
        index = self.r.index
        d = self.get_array()
        
        if isinstance(indexes, int):
            indexes = [indexes]
        r, c = index(x, y)
        window = ((r, r+1), (c, c+1))
        data = d[r][c]

        if (self.pol!=10):
            d=libcarine3.merge_tools.sous_indice(d,self.pol)
        
        data2=d[r][c]
        return([data,data2])
    def to_png(self,data, fn=None, dpi=10):
        """Convert raster into png format.
        
        :param fn: path and filename of output png file or None
        :param dpi:
        :return: None or Pillow.Image if fn is None.
        """
    

        # Limits
        #data[(data > -999) & (data < 0)] = 0

        # Create figure
        log.debug("oiyouyiuy")
        #size en pouces
        figsize = (data.shape[1]/dpi, data.shape[0]/dpi)
        log.debug(figsize)
        fig = plt.figure(frameon=False, figsize=figsize)
        ax = fig.add_axes([0, 0, 1,1])
        ax.axis('off')

        # Echelle de couleurs
        cmap = libcarine3.colors.discrete_cmap(libcarine3.colors.colors)
        vmin = 0
        vmax = 100
        log.debug(vmax)
        plt.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
        log.debug("creating plot done cool !")

        # Export sous forme d'image
        f = open(fn, 'wb') if fn else io.BytesIO()

        fig.canvas.print_png(f)
        log.debug("print ok")
        fig.clf()
    
        plt.close()
        if fn:
            f.close()
            log.debug(f"save image to {fn}")
        else:
            log.debug("return image data...")
            return f.getvalue()
        # width,height = data.shape[1] , data.shape[0]
        # width_byte_4 = width 
        
        # buf = data.tobytes()
        # raw_data = b''.join(b'\x00' + buf[span:span + width_byte_4] for span in range((height - 1) * width_byte_4, -1, - width_byte_4))
        # return b''.join([
            # b'\x89PNG\r\n\x1a\n',
            # self.png_pack(b'IHDR', struct.pack("!2I5B", width, height, 8, 6, 0, 0, 0)),
            # self.png_pack(b'IDAT', zlib.compress(raw_data, 9)),
            # self.png_pack(b'IEND', b'')])


    # def png_pack(self,png_tag, data):
        # chunk_head = png_tag + data
        # return (struct.pack("!I", len(data)) + chunk_head + struct.pack("!I", 0xFFFFFFFF & zlib.crc32(chunk_head)))
    def to_tif(self,data, fn=None, dpi=10):
        """Convert raster into png format.
        
        :param fn: path and filename of output png file or None
        :param dpi:
        :return: None or Pillow.Image if fn is None.
        """
    

        # Limits
        #data[(data > -999) & (data < 0)] = 0

        # Create figure
        log.debug("oiyouyiuy")
        #size en pouces
        log.debug(data.shape)
        data=data.reshape(data.shape[2],data.shape[1])
        figsize = (data.shape[1]/dpi, data.shape[0]/dpi)
        log.debug(figsize)
        fig = plt.figure(frameon=False, figsize=figsize)
        ax = fig.add_axes([0, 0, 1,1])
        ax.axis('off')

        # Echelle de couleurs
        cmap = libcarine3.colors.discrete_cmap(libcarine3.colors.colors)
        vmin = 0
        vmax = 100
        log.debug(vmax)
        # if (self.pol!=10):
            # data=libcarine3.merge_tools.sous_indice(data,self.pol)
        plt.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
        log.debug("creating plot done cool !")

        # Export sous forme d'image
        a=fig.savefig(fn)
        log.debug("print ok")
        
    
        plt.close()
        return a
    @property
    def bbox(self):
        """Bounding box of raster.
        
        :return: (xmin, ymin, xmax, ymax).
        """
        return list(self.r.bounds)

    def add_expertises(self, expertises):
        """Add expertises.
        
        :param expertises: list of Expertises object.
        """
        self.expertises += expertises
        
    def export_low_val(self):
        with rio.Env(GDAL_CACHEMAX=512,NUM_THREADS='ALL_CPUS') as env:

            pr = self.r.profile
            pol=self.source.tsr.pol
            ech=self.source.tsr.ech
            tsp=self.source.daterun
            
            new_file = config.basse_def_val_path + config.aasqa +'-'+ pol.lower() + '-' + str(tsp) + '-' + str(ech+1) + '.tiff' 
            log.debug(" --- new file --- ")
            log.debug(new_file)
            ar=self.r.read(1)
            new_ar = self.get_array()
            shp=new_ar.shape

            shp2=new_ar.shape
            aff=self.r.transform
            log.debug(pr)
            with rio.open(new_file,'w',**pr) as dst:
                dst.write(new_ar,1)
                dst.close()
            return 'toto'
    
    # def merge_fine(self):
        # with rio.Env(GDAL_CACHEMAX=8192,NUM_THREADS='ALL_CPUS') as env:
            # ratio=100
            # urls=[]
            # pol=self.source.tsr.pol
            # ech=self.source.tsr.ech
            # tsp=self.source.daterun
            # pr=self.r.profile
            # b1=self.r.bounds
            # aff=self.r.transform

            # new_file = '/var/www/html/hd/val/aura_' + pol.lower() + '_' + str(tsp) + '_' + str(ech+1) + '.tiff' 
            # ar=self.get_array()
            
            # s=ar.shape
            # log.debug(s)
            # new_ar=ar.repeat(ratio,axis=0).repeat(ratio,axis=1)
            # log.debug(new_ar.shape)
            # ar=None
            
            # pr.update(height = pr['height'] * ratio)
            # pr.update(width = pr['width']  * ratio)

            # new_aff = affine.Affine(aff.a / ratio, aff.b, aff.c,aff.d, aff.e / ratio, aff.f)  
            # pr.update(transform=new_aff)
            # prh=pr['height']
            # prw=pr['width']
            
            # if (pol.upper() != 'MULTI'):

                # lib_ech=config.libs_ech[ech]
                # dir = '/home/previ/raster_source/domaines_fine/3857/'           
                # for i in config.domaines_hd:
                    # url=dir+'AURA_'+pol.upper()+'_'+i+'_'+str(tsp)+'_'+lib_ech+'_3857.tif'
                    # urls.append(url)            
            
            # res=14.25
            # w1=rio.windows.from_bounds(b1[0],b1[1],b1[2],b1[3],pr['transform'],boundless=True)
            # log.debug(w1)
            # w4=None
            # with MemoryFile() as memfile:
                # with memfile.open(**pr) as dataset:
                    # dataset.write(new_ar,1)
                    # new_ar=None
                    # mem_arr = dataset.read()
                    # for f2 in urls:
                        # ds2=rio.open(f2)
                        # b2=ds2.bounds
                        # log.debug(b2)
                        # ox=abs((b2[0]-b1[0])/res)
                        # oy=abs((b2[3]-b1[3])/res)
                        # w2=rio.windows.from_bounds(b2[0],b2[1],b2[2],b2[3],ds2.transform,boundless=True)
                        # log.debug("=== w2 ===")
                        # print(w2)
                        # w3=rio.windows.intersection(w1,w2)
                        # log.debug("=== w3 ===")
                        # log.debug(w3)
                        # w4=((int(w3[0][0]+oy),int(w3[0][1]+oy)),(int(w3[1][0]+ox),int(w3[1][1]+ox)))
                        # log.debug("=== w4 ===")
                        # log.debug(w4)
                        # warr=dataset.read(1,window=w4)
                        # log.debug("=== warrshape ===")
                        # log.debug(warr.shape)
                        # warr=np.maximum(warr,ds2.read())
                        # print("=== w4 ===")
                        # print([w4[0][0],w4[0][1],w4[1][0],w4[1][1]])
                        # mem_arr[0][w4[0][0]:w4[0][1],w4[1][0]:w4[1][1]]=warr
                        # log.debug(warr.shape)
                        

                        # print(mem_arr.shape)
                        # log.debug(ds2.profile)
                        # warr=None
                        # ds2.close()
                    # with rio.open(new_file,'w',**pr) as dst:
                        # dst.write(mem_arr)
                        # dst.close()
            # mem_arr=None
            # dataset.close()
            # memfile=None
        # return new_file
    # def merge_mi_fine(self,Prev):
        # with rio.Env(GDAL_CACHEMAX=1024,NUM_THREADS='ALL_CPUS') as env:
            # ratio=20
            # urls=[]
            # pol=self.source.tsr.pol
            # ech=self.source.tsr.ech
            # tsp=self.source.daterun
            # pr=self.r.profile
            # b1=self.r.bounds
            # aff=self.r.transform
            # new_file = '/var/www/html/hd/val/aura_' + pol.lower() + '_' + str(tsp) + '_' + str(ech+1) + '.tiff' 
            
            # ar=np.ma.getdata(self.get_array())
            
            # s=ar.shape
            # log.debug(s)
            # new_ar=ar.repeat(ratio,axis=0).repeat(ratio,axis=1)
            # log.debug(new_ar.shape)
            # ar=None
            
            # pr.update(height = pr['height'] * ratio)
            # pr.update(width = pr['width']  * ratio)

            # new_aff = affine.Affine(aff.a / ratio, aff.b, aff.c,aff.d, aff.e / ratio, aff.f)  
            # pr.update(transform=new_aff)
            # prh=pr['height']
            # prw=pr['width']
            
            # if (pol.upper() != 'MULTI'):

                # lib_ech=config.libs_ech[ech]
                # dir = '/home/previ/raster_source/domaines_fine/3857/'           
                # for i in config.domaines_hd:
                    # url=dir+'AURA_'+pol.upper()+'_'+i+'_'+str(tsp)+'_'+lib_ech+'_3857.tif'
                    # urls.append(url)            
            
            # res=71.5
            # w1=rio.windows.from_bounds(b1[0],b1[1],b1[2],b1[3],pr['transform'],boundless=True)
            # log.debug(w1)
            # w4=None
            # with MemoryFile() as memfile:
                # with memfile.open(**pr) as dataset:
                    # dataset.write(new_ar,1)
                    # new_ar=None
                    # mem_arr = dataset.read()
                    # for f2 in urls:
                        # if (os.path.exists(f2)):
                            # ds2=rio.open(f2)
                            # b2=ds2.bounds
                            # log.debug(b2)
                            # ox=abs((b2[0]-b1[0])/res)
                            # oy=abs((b2[3]-b1[3])/res)
                            # w2=rio.windows.from_bounds(b2[0],b2[1],b2[2],b2[3],ds2.transform,boundless=True)
                            # log.debug("=== w2 ===")
                            # print(w2)
                            # w3=rio.windows.intersection(w1,w2)
                            # log.debug("=== w3 ===")
                            # log.debug(w3)
                            # w4=((int(w3[0][0]+oy),int(w3[0][1]+oy)),(int(w3[1][0]+ox),int(w3[1][1]+ox)))
                            # log.debug("=== w4 ===")
                            # log.debug(w4)
                            # warr=dataset.read(1,window=w4)
                            # log.debug("=== warrshape ===")
                            # log.debug(warr.shape)
                            # warr=np.maximum(warr,ds2.read())
                            # print("=== w4 ===")
                            # print([w4[0][0],w4[0][1],w4[1][0],w4[1][1]])
                            # mem_arr[0][w4[0][0]:w4[0][1],w4[1][0]:w4[1][1]]=warr
                            # log.debug(warr.shape)
                            

                            # print(mem_arr.shape)
                            
                            # log.debug(ds2.profile)
                            # warr=None
                            # ds2.close()
                    # with rio.open(new_file,'w',**pr) as dst:
                        # dst.write(mem_arr)
                        # dst.close()
            # mem_arr=None
            # dataset.close()
            # memfile=None
        # return new_file