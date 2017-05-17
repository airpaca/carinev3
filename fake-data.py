#!/usr/bin/env python3.6
# coding: utf-8

"""Create fake data..."""


import datetime

import django
django.setup()

from raster.models import Expertise


dr = datetime.date(2017, 5, 15)


# Clean up database
Expertise.objects.all().delete()


# Point (Marseille)
point = 'POINT(5.40 43.29)'
e = Expertise(daterun=dr, pol='NO2', ech=0, delta=50, geom=point)
e.save()

# Point (Toulon)
point = 'POINT(5.91 43.13)'
e = Expertise(daterun=dr, pol='NO2', ech=0, delta=60, geom=point)
e.save()

# Small polygon (Aix-en-Provence)
poly = 'POLYGON((5.38 43.55, 5.39 43.43, 5.56 43.47, 5.46 43.56, 5.38 43.55))'
e = Expertise(daterun=dr, pol='PM10', ech=0, delta=15, geom=poly)
e.save()

# Big polygon (Littoral des Alpes-Maritimes) with min
poly = ('POLYGON((7.3978 43.6815, 7.3266 43.8066, 7.0223 43.7208, '
        '6.7548 43.5588, 6.6665 43.4017, 6.7744 43.2888, 7.3978 43.6815))')
e = Expertise(daterun=dr, pol='PM10', ech=1, delta=-10, geom=poly)
e.save()

# Polygon (Toulon)
poly = ('POLYGON((5.7595 43.0172, 5.7886 43.1313, 5.8806 43.2107, '
        '6.0242 43.2004, 6.0641 43.1411, 6.0272 43.0116, 5.7595 43.0172))')
e = Expertise(daterun=dr, pol='PM10', ech=1, delta=10, geom=poly)
e.save()

# Remove too much concentration
poly = ('POLYGON((5.5858 43.2775, 5.5824 43.2721, 5.5983 43.2622, '
        '5.6131 43.2737, 5.5989 43.2822, 5.5858 43.2775))')
e = Expertise(daterun=dr, pol='PM10', ech=1, delta=-50, mn=40, geom=poly)
e.save()
