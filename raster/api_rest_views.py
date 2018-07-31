# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.decorators.http import require_POST
import json
import logging
from django.template import loader
from django.http import HttpResponse, JsonResponse,HttpResponseRedirect
from .models import *
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from .serializers import *
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework import generics

# Log
log = logging.getLogger('carinev3.raster.api_rest_views')


class DomaineFineViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows Domaines Fines to be viewed or edited.
	"""
	queryset = DomaineFine.objects.all()
	serializer_class = DomaineFineSerializer
	
class DatePrevViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows DatePrev to be viewed or edited.
	"""
	queryset = DatePrev.objects.all()
	serializer_class = DatePrevSerializer
	
