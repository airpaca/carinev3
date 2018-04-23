# -*- coding: utf-8 -*-
import logging
import datetime
import json
import psycopg2
import MySQLdb as msql
import rasterio as rio
import datetime
import fiona
import numpy as np
import random
import rasterstats
from django.core import serializers
from pyproj import Proj,transform
from django.views.decorators.http import require_POST
from django.template import loader
from django.http import HttpResponse, JsonResponse,HttpResponseRedirect
from .models import *
import libcarine3
from libcarine3 import *
import config,logins
import django.utils.timezone as tz
import os
import itertools
from django.views.decorators.cache import never_cache
import urllib.request
from rasterio import merge,windows
from rasterio.windows import from_bounds
import affine
from rasterstats import zonal_stats
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import urllib.request
from django.views.decorators.cache import never_cache

@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')    
def config_html(request):
    """Index."""
    template = loader.get_template('config/config.html')
    context = {'ctx_list': Context.objects.all(),'ctx_active':Context.objects.get(active=True),'db': settings.DATABASES}
    return HttpResponse(template.render(context, request))
@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')
def config_js(request):
    """Application (Javascript)."""
    template = loader.get_template('config/config.js')
    context = {}
    return HttpResponse(template.render(context, request))
@login_required(login_url='accounts/login/?next=inf-carine3/carinev3/raster')
def set_ctx(request):
    ctx_id = request.GET.get('ctx_id')
    ctx=Context.objects.get(active=True)
    desactive=ctx.nom
    ctx.active=False
    ctx.save()
    ctx=Context.objects.get(id=ctx_id)
    ctx.active=True
    active=ctx.nom
    ctx.save()
    return JsonResponse(dict(active=active,desactive=desactive))