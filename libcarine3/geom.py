#!/usr/bin/env python3.6
# coding: utf-8


"""Add reprojection method of shapely's Point and Polygon."""


import pyproj
from shapely.geometry import Point as ShapelyPoint
from shapely.geometry import Polygon as ShapelyPolygon
import numpy


class Point(ShapelyPoint):
    """Point with a specific projection code."""

    def __init__(self, x, y, epsg):
        """Point with a specific projection code.
        
        :param x: x
        :param y: y
        :param epsg: epsg code (int)
        """
        self.epsg = epsg
        super().__init__(x, y)

    def reproject(self, epsg):
        """Reproject geometry into another projection.
         
        :param epsg: epsg code (int).
        :return: Point object.
        """
        p1 = pyproj.Proj(init=f'epsg:{self.epsg}')
        p2 = pyproj.Proj(init=f'epsg:{epsg}')
        x, y = pyproj.transform(p1, p2, self.x, self.y)
        return Point(x, y, epsg)

    def buffer(self, distance, epsg=None, **kwargs):
        """Create buffer around this point.
        
        :param distance: distance.
        :param epsg: epsg code of the return object (same projection if None).
        :param kwargs: kwargs of shapely.geometry.Point object.
        :return: Polygon object.
        """
        if not epsg:
            return Polygon(super().buffer(distance, **kwargs), epsg=self.epsg)
        else:
            return Polygon(self.reproject(epsg).buffer(distance, **kwargs),
                           epsg=epsg)

    def buffers(self, distances, epsg=None, **kwargs):
        """Generator to create buffers around this points.
        
        :param distances: list of distances.
        :param epsg: epsg code of the return object (same projection if None).
        :param kwargs: kwargs of shapely.geometry.Point object.
        :return: Polygon object.
        """
        for d in distances:
            yield self.buffer(d, epsg, **kwargs)


class Polygon(ShapelyPolygon):
    """__Simple__ (only exterior ring) polygon with a specific projection."""

    def __init__(self, coords, epsg):
        """__Simple__ (only exterior ring) polygon  with a specific projection 
        code.

        :param coords: list of points (x, y)
        :param epsg: epsg code (int)
        """
        self.epsg = epsg
        super().__init__(coords)

    def reproject(self, epsg):
        """Reproject geometry into another projection.

        :param epsg: epsg code (int).
        :return: Polygon object.
        """
        p1 = pyproj.Proj(init=f'epsg:{self.epsg}')
        p2 = pyproj.Proj(init=f'epsg:{epsg}')
        c1 = numpy.array(self.exterior.coords).T
        c2 = numpy.array(pyproj.transform(p1, p2, *c1)).T
        return Polygon(c2, epsg)

    def buffer(self, distance, epsg=None, **kwargs):
        """Create buffer around this polygon.

        :param distance: distance.
        :param epsg: epsg code of the return object (same projection if None).
        :param kwargs: kwargs of shapely.geometry.Point object.
        :return: Polygon object.
        """
        if not epsg:
            return Polygon(super().buffer(distance, **kwargs), epsg=self.epsg)
        else:
            return Polygon(self.reproject(epsg).buffer(distance, **kwargs),
                           epsg=epsg)

    def buffers(self, distances, epsg=None, **kwargs):
        """Generator to create buffers around this points.

        :param distances: list of distances.
        :param epsg: epsg code of the return object (same projection if None).
        :param kwargs: kwargs of shapely.geometry.Point object.
        :return: Polygon object.
        """
        for d in distances:
            yield self.buffer(d, epsg, **kwargs)
