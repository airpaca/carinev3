#!/usr/bin/env python3
# coding: utf-8

"""Carine v3 :: raster"""


import io
import logging
import rasterio
from rasterio import features
import numpy
import matplotlib.pyplot as plt
import libcarine3


log = logging.getLogger('libcarinev3.raster')


def rasterize_zt(poly, distance, rstshape, rstaff):
    """Création d'un raster d'une zone tampon autour d'un polygone.
    
    :param poly: Polygon.
    :param distance: distance.
    :param rstshape: shape of output.
    :param rstaff: transformation of raster.
    :return: numpy.array.
    """
    # Création de la zone tampon (en projection cartographique !)
    if distance:
        pbuf = poly.buffer(distance, epsg=2154).reproject(4326)
    else:
        pbuf = poly

    # Rasterisation de la zone tampon
    shapes = ((g, 1) for g in [pbuf])
    rbuf = features.rasterize(shapes=shapes,
                              out_shape=rstshape,
                              transform=rstaff,
                              all_touched=True)
    return rbuf


class Raster:
    """Raster."""

    def __init__(self, fn, pol):
        """Raster.
        
        :param fn: path and filename of a raster.
        :param pol: pollutant id.
        """
        self.fn = fn
        self.r = rasterio.open(self.fn, 'r')
        if pol not in libcarine3.POLLUTANTS:
            log.error("cannot reconize pollutant!")
            raise libcarine3.Carinev3Error("cannot reconize pollutant!")
        self.pol = pol
        self.modifs = list()

    def __del__(self):
        """Close raster."""
        self.r.close()

    @property
    def xs(self):
        x0 = self.r.affine.c
        nx = self.r.width
        dx = self.r.affine.a
        return numpy.arange(x0, x0 + nx * dx, dx)

    @property
    def ys(self):
        y0 = self.r.affine.f
        ny = self.r.height
        dy = self.r.affine.e
        return numpy.arange(y0, y0 + ny * dy, dy)

    @property
    def x(self):
        x, _ = numpy.meshgrid(self.xs, self.ys)
        return x

    @property
    def y(self):
        _, y = numpy.meshgrid(self.xs, self.ys)
        return y

    def to_png(self, fn=None, dpi=300):
        """Convert raster into png format.
        
        :param fn: path and filename of output png file or None
        :param dpi:
        :return: None or Pillow.Image if fn is None.
        """
        data = self.r.read(1)
        mask = (data == self.r.nodata)
        data = numpy.ma.array(data, mask=mask)
        del mask
        log.debug(f"read data from raster {self.fn}")

        # Apply modifications
        for delta, geom in self.modifs:
            modif = numpy.zeros(data.shape)

            if geom.geom_type == 'Point':
                g = libcarine3.Point(*geom.coords, epsg=4326)

            elif geom.geom_type == 'Polygon':
                g = libcarine3.Polygon(geom.coords[0], epsg=4326)

            else:
                raise NotImplementedError()

            # Définition des zones tampons pour la décroissance
            ztlims, ztxs, ztys = libcarine3.zt_sigmoide(d=10000, n=30)

            ztlims = list(ztlims[1:][::-1]) + [0]
            ztys = list(ztys[::-1]) + [1]
            for d, pc in zip(ztlims, ztys):
                rbuf = rasterize_zt(g, d, self.r.shape, self.r.affine)
                modif[rbuf == 1] = delta * pc
            data += modif
            log.debug(f"apply modification {delta:+} in {g.wkt}")

        # Limits
        data[(data > -999) & (data < 0)] = 0

        # Create figure
        figsize = (data.shape[1] / dpi, data.shape[0] / dpi)

        fig = plt.figure(frameon=False, figsize=figsize)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis('off')

        # Echelle de couleurs
        cmap = libcarine3.aqvl
        vmin = 0
        vmax = libcarine3.VLS[self.pol] * 2

        plt.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax, interpolation='none')
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

    @property
    def bbox(self):
        """Bounding box of raster.
        
        :return: (xmin, ymin, xmax, ymax).
        """
        return list(self.r.bounds)

    def alter(self, delta, geom):
        """Alter raster.
        
        :param delta: concentration to add.
        :param geom: Point or Polygon.
        """
        self.modifs.append((delta, geom))


if __name__ == '__main__':

    # Test
    r = Raster("/home/jv/azur_data/wgs84_ldv2/"
               "raster_PACA_NO2_20_04_2017_jp0.tif",
               libcarine3.NO2)
    r.alter(100, (5.39, 43.29))
    r.to_png("/tmp/rgb.png", dpi=100)
