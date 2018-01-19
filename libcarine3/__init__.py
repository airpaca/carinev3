#!/usr/bin/env python3
# coding: utf-8

from libcarine3.const import *
from libcarine3.raster import Raster
#from libcarine3.colors import aqvl
from libcarine3.geom import Point, Polygon
from libcarine3.sigmoid import zt_sigmoide


class Carinev3Error(Exception):
    pass
