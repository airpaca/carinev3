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
def to_png(data, fn=None, dpi=1000):
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
    console.log(vmax)

    plt.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax,clim=(0.0,100.0))
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

    def __init__(self, fn, pol):
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
                mk_ssup = modif
            # Use mask if mn or mx
            # FIXME: comment faire le traitement avec les bornes min et max
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
            
            
            modif[(rbuf == 255) & mk_mn & mk_mx & mk_ssup] = expertise.delta
            data += modif

        #data=libcarine3.sous_indice(data,self.pol)
        #log.debug(f"apply modification {expertise.delta:+} in {g.wkt}")

        # if (self.pol!=10):
            # data=libcarine3.merge_tools.sous_indice(data,self.pol)
        return data
    def sample_gen(self, x,y, indexes=None):
        #rewrite de la source du meme nom de rio (rio.sample.sample_gen) 
        index = self.r.index
        d= self.get_array()
        if isinstance(indexes, int):
            indexes = [indexes]
        r, c = index(x, y)
        window = ((r, r+1), (c, c+1))
        data = d[r][c]
        return(data)
    def to_png(self,data, fn=None, dpi=300):
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
        vmax = np.max(data)
        log.debug(vmax)
        plt.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax, clim=(0.0,100.0))
        log.debug("creating plot done!")

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
